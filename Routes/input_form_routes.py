from flask import Blueprint, render_template, request, jsonify
from controllers.prompt_controller import build_prompt
from config.config import generate_with_model
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
        tone          = data["tone"]
        focus         = data["focus"]
        company       = data["company_name"]
        industry      = data["industry"]
        context       = " ".join(data["additional_context"])
        model_choice  = data["model_choice"]

        logger.info("Inputs: %s", data)

        # 1) Build the prompt
        prompt = build_prompt(tone, focus, company, industry, context)
        if prompt.startswith("⚠️"):
            return jsonify({ "error": prompt }), 400

        # 2) Call the selected LLM
        generated_message = generate_with_model(prompt, model_choice)

        # 3) Respond with the generated text
        return jsonify({
            "message": generated_message,
            "prompt_version": f"{tone}_{focus}_v1",
            "model_used": model_choice
        }), 200

    except ValueError as ve:
        logger.error("Invalid model_choice", exc_info=True)
        return jsonify({ "error": str(ve) }), 400

    except Exception as e:
        logger.error("Error in generate_email", exc_info=True)
        # Surface user‐friendly message if it's a runtime error from call_claude
        msg = str(e)
        status = 500
        if "credits" in msg.lower():
            status = 402
        return jsonify({ "error": msg }), status
