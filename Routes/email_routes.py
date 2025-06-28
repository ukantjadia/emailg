from flask import Blueprint, request, jsonify
from controllers.prompt_controller import build_prompt
import logging

logger = logging.getLogger(__name__)
email_api = Blueprint("email_api", __name__)

@email_api.route("/api/generate-email", methods=["POST"])
def generate_email():
    try:
        data = request.get_json()
        tone = data.get("tone", "")
        focus = data.get("focus", "")
        company = data.get("company_name", "")
        context_points = data.get("additional_context", [])
        extra_context = data.get("optional_context", "")

        context = " ".join(context_points)
        if extra_context:
            context += f" {extra_context}"

        prompt = build_prompt(tone, focus, company, context)

        return jsonify({
            "message": prompt,
            "prompt_version": f"{tone}_{focus}_v1"
        })

    except Exception as e:
        logger.error("❌ Error in generate_email route", exc_info=True)
        return jsonify({ "error": str(e) }), 500
