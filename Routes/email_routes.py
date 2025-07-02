# in this we will have the final route which will generate the email

from flask import Blueprint, request, jsonify
from controllers.prompt_controller import PromptController
from controllers.generate_controller import GenerateController
from controllers.feedback_controller import FeedbackController
from config.config import Config
import logging
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

email_bp = Blueprint("email_api", __name__)
feedback_controller = FeedbackController()

@email_bp.route("/api/generate-email", methods=["POST"])
def generate_email():
    try:
        data = request.get_json()
        tone          = data["tone"]
        focus         = data["focus"]
        company       = data["company_name"]
        industry      = data["industry"]
        model_choice  = data["model_choice"]
        user_id       = data.get("user_id", "test_test")

        context_points = data["additional_context"]
        for i, point in enumerate(context_points):
            word_count = len(point.strip().split())
            if word_count < 20:
                return jsonify({
                    "error": f"Point {i + 1} must be at least 20 words. You entered {word_count}."
                }), 400

        context = " ".join(context_points)

        logger.info("Inputs: %s", data)

        # 1) Build the prompt
        try:
            prompt = PromptController.build_prompt(tone, focus, company, industry, context)
        except FileNotFoundError as fnf:
            return jsonify({ "error": str(fnf) }), 404
        except Exception as e:
            return jsonify({ "error": str(e) }), 500

        # 2) Call the selected LLM via controller
        generated_message = GenerateController.generate_with_model(prompt, model_choice)

        # 3) Log the generation as feedback
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
        feedback_controller.capture_feedback(feedback_data)

        # 4) Respond with the generated text and prompt_text
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
        return jsonify({ "error": str(ve) }), 400

    except Exception as e:
        logger.error("Error in generate_email", exc_info=True)
        msg = str(e)
        status = 500
        if "credits" in msg.lower():
            status = 402
        return jsonify({ "error": msg }), status
