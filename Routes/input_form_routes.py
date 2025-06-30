# Routes/input_form_routes.py

from flask import Blueprint, render_template, request, jsonify
from controllers.prompt_controller import PromptController
from controllers.generate_controller import GenerateController
from controllers.feedback_controller import FeedbackController
from config.config import Config
import logging
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)
input_form = Blueprint("email_ui", __name__)

@input_form.route("/email-generator", methods=["GET"])
def show_email_form():
    return render_template("email_generator.html")

@input_form.route("/api/generate-email", methods=["POST"])
def generate_email():
    try:
        data = request.get_json(force=True)
        tone         = data["tone"]
        focus        = data["focus"]
        company      = data["company_name"]
        industry     = data["industry"]
        context      = " ".join(data["additional_context"])
        model_choice = data["model_choice"]
        user_id      = data.get("user_id", "test_test")

        logger.info("Generate request: %s", data)

        # Build prompt template
        try:
            prompt = PromptController.build_prompt(tone, focus, company, industry, context)
        except FileNotFoundError as fnf:
            return jsonify({"error": str(fnf)}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500

        # Call the chosen LLM
        try:
            generated_message = GenerateController.generate_with_model(prompt, model_choice)
        except TypeError as te:
            if "authentication method" in str(te).lower() or "api_key" in str(te).lower():
                return jsonify({"error": "Model API key is missing or invalid. Please check your configuration."}), 502
            return jsonify({"error": str(te)}), 500
        except Exception as e:
            return jsonify({"error": str(e)}), 500

        # Log the generation as feedback
        message_id = str(uuid.uuid4())
        parent_message_id = data.get("parent_message_id")
        feedback_type = "regeneration" if parent_message_id else "generation"

        feedback_data = {
            "message_id": message_id,
            "parent_message_id": parent_message_id,
            "feedback_type": feedback_type,
            "user_id": user_id,
            "company_name": company,
            "industry": industry,
            "tone": tone,
            "focus": focus,
            "context": context,
            "model_used": model_choice,
            "prompt_template": f"{tone}_{focus}_{Config.PROMPT_TEMPLATE_VERSION}",
            "prompt_text": prompt,
            "generated_message": {
                "message": generated_message,
                "generated_at": datetime.utcnow().isoformat()
            }
        }
        logger.info(f" capatureing the feedback {feedback_data}")
        FeedbackController.capture_feedback(feedback_data)

        return jsonify({
            "message": generated_message,
            "prompt_version": f"{tone}_{focus}_{Config.PROMPT_TEMPLATE_VERSION}",
            "model_used": model_choice,
            "message_id": message_id,
            "parent_message_id": parent_message_id,
            "prompt_text": prompt
        }), 200

    except ValueError as ve:
        logger.error("Invalid model_choice", exc_info=True)
        return jsonify({"error": str(ve)}), 400

    except Exception as e:
        logger.error("Error in generate_email", exc_info=True)
        return jsonify({"error": "Server error — please try again."}), 500

@input_form.route("/api/feedback", methods=["POST"])
def submit_feedback():
    """
    Capture upvote/downvote feedback from the front end and persist to DB.
    Expects JSON with at least:
      - message_id, feedback_type ('upvote'/'downvote'), user_id
      - company_name, industry, tone, focus, context (string), optional_context?
      - model_used, prompt_template, prompt_text, generated_message (JSON or string)
    """
    data = request.get_json(force=True)
    logger.info("Feedback request: %s", data)

    result = FeedbackController.capture_feedback(data)
    status = 200 if result.get("success") else 400
    return jsonify(result), status
