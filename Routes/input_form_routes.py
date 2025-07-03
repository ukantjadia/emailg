import uuid
import logging
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify
from controllers.prompt_controller import PromptController
from controllers.generate_controller import GenerateController
from controllers.feedback_controller import FeedbackController
from config.config import Config
from models.feedback_model import MessageFeedback, db

logger = logging.getLogger(__name__)
input_form = Blueprint("email_ui", __name__)

generate_controller = GenerateController()
feedback_controller = FeedbackController()


@input_form.route("/email-generator", methods=["GET"])
def show_email_form():
    return render_template("email_generator.html")


@input_form.route("/api/generate-email", methods=["POST"])
def generate_email():
    try:
        data         = request.get_json(force=True)
        tone         = data["tone"]
        focus        = data["focus"]
        company      = data["company_name"]
        industry     = data["industry"]
        model_choice = data["model_choice"]
        user_id      = data.get("user_id", "anonymous")

        # Validate 3 required context points
        context_points = data["additional_context"]
        for i, pt in enumerate(context_points[:3]):
            if len(pt.strip().split()) < 20:
                return jsonify({
                    "error": f"Point {i+1} must be at least 20 words."
                }), 400
        context = " ".join(context_points)

        logger.info("Generate request: %s", data)

        # Build prompt
        prompt = PromptController.build_prompt(
            tone, focus, company, industry, context
        )

        # Call LLM
        generated_message = generate_controller.generate_with_model(
            prompt, model_choice
        )

        # Log “generation” action
        message_id          = str(uuid.uuid4())
        parent_message_id   = data.get("parent_message_id")
        feedback_type       = "regeneration" if parent_message_id else "generation"

        feedback_controller.capture_feedback({
            "message_id":       message_id,
            "parent_message_id": parent_message_id,
            "feedback_type":    feedback_type,
            "user_id":          user_id,
            "company_name":     company,
            "industry":         industry,
            "tone":             tone,
            "focus":            focus,
            "context":          context,
            "model_used":       model_choice,
            "prompt_template":  f"{tone}_{focus}_{Config.PROMPT_TEMPLATE_VERSION}",
            "prompt_text":      prompt,
            "generated_message":{
                "message":     generated_message,
                "generated_at": datetime.utcnow().isoformat()
            }
        })

        return jsonify({
            "message_id":     message_id,
            "parent_message_id": parent_message_id,
            "message":        generated_message,
            "prompt_version": f"{tone}_{focus}_{Config.PROMPT_TEMPLATE_VERSION}",
            "model_used":     model_choice,
            "prompt_text":    prompt
        }), 200

    except Exception as e:
        logger.error("Error in generate_email", exc_info=True)
        return jsonify({"error": str(e)}), 500


@input_form.route("/api/feedback", methods=["POST"])
def submit_feedback():
    data = request.get_json(force=True)
    logger.info("Feedback request: %s", data)

    result = feedback_controller.capture_feedback(data)
    status = 200 if result.get("success") else 400
    return jsonify(result), status


@input_form.route("/feedback-view", methods=["GET"])
def feedback_view():
    """
    Show all feedback rows in a simple HTML table.
    """
    rows = MessageFeedback.query.order_by(
        MessageFeedback.timestamp.desc()
    ).all()
    feedback_list = [r.to_dict() for r in rows]
    return render_template("feedback_view.html", feedback_list=feedback_list)
