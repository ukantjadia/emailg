from flask import Blueprint, render_template, request, jsonify
from controllers.prompt_controller import build_prompt
import logging

logger = logging.getLogger(__name__)
input_form = Blueprint("email_ui", __name__)

@input_form.route("/email-generator", methods=["GET"])
def show_email_form():
    return render_template("email_generator.html")


@input_form.route("/api/generate-email", methods=["POST"])
def generate_email():
    try:
        data = request.get_json()
        tone = data.get("tone", "")
        focus = data.get("focus", "")
        company = data.get("company_name", "")
        context_points = data.get("additional_context", [])
        extra_context = data.get("optional_context", "")
        logging.info(f" user inputs are {data}")
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
