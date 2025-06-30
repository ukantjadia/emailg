# Routes/input_form_routes.py

from flask import Blueprint, render_template, request, jsonify
from controllers.prompt_controller import build_prompt
from controllers.generate_controller import GenerateController
from controllers.feedback_controller import FeedbackController
import logging

logger = logging.getLogger(__name__)
input_form = Blueprint("email_ui", __name__)

# Instantiate controllers
generate_controller = GenerateController()
feedback_controller = FeedbackController()


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

        logger.info("Generate request: %s", data)

        # Build prompt template
        prompt = build_prompt(tone, focus, company, industry, context)
        if prompt.startswith("⚠️"):
            return jsonify({"error": prompt}), 400

        # Call the chosen LLM
        generated_message = generate_controller.generate(prompt, model_choice)

        return jsonify({
            "message": generated_message,
            "prompt_version": f"{tone}_{focus}_v1",
            "model_used": model_choice
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

    result = feedback_controller.capture_feedback(data)
    status = 200 if result.get("success") else 400
    return jsonify(result), status
