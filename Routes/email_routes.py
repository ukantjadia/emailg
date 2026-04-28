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

        # Required fields
        tone = data["tone"]
        focus = data["focus"]
        company = data["company_name"]
        industry = data["industry"]
        model_choice = data["model_choice"]
        user_id = data.get("user_id", "test_test")

        # Handle context (generation vs regeneration)
        if "additional_context" in data:
            context_points = data["additional_context"]

            for i, point in enumerate(context_points[:3]):
                word_count = len(point.strip().split())
                if word_count < 20:
                    return jsonify({
                        "error": f"Point {i + 1} must be at least 20 words. You entered {word_count}."
                    }), 400

            context = " ".join(context_points)

        else:
            # Regeneration case
            context = data.get("context", "")
            if not context:
                return jsonify({"error": "Context is required"}), 400

        logger.info("Inputs: %s", data)

        # 1) Build the prompt
        try:
            prompt = PromptController.build_prompt(
                tone, focus, company, industry, context
            )
        except FileNotFoundError as fnf:
            return jsonify({"error": str(fnf)}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500

        # 2) Call the selected LLM
        generated_message = GenerateController.generate_with_model(
            prompt, model_choice
        )

        # 3) Generate IDs + feedback tracking
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

        # 4) Response
        return jsonify({
            "message": generated_message,
            "prompt_version": f"{tone}_{focus}_{Config.PROMPT_TEMPLATE_VERSION}",
            "model_used": model_choice,
            "message_id": message_id,
            "parent_message_id": parent_message_id,
            "prompt_text": prompt
        }), 200

    except KeyError as ke:
        logger.error("Missing required field", exc_info=True)
        return jsonify({"error": f"Missing field: {str(ke)}"}), 400

    except ValueError as ve:
        logger.error("Invalid input", exc_info=True)
        return jsonify({"error": str(ve)}), 400

    except Exception as e:
        logger.error("Error in generate_email", exc_info=True)
        return jsonify({"error": str(e)}), 500
