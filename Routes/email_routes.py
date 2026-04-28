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
        for i, point in enumerate(context_points[:3]):
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
document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("email-gen-form");
  const resultArea = document.getElementById("result-area");

  let lastFeedbackData = null;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    await generateOrRegenerate();
  });

  async function generateOrRegenerate(regenPayload = null) {
    resultArea.innerHTML = "<em>Generating…</em>";

    let payload;

    if (regenPayload) {
      payload = { ...regenPayload };
    } else {
      const contextPoints = [
        form.context_point_1.value.trim(),
        form.context_point_2.value.trim(),
        form.context_point_3.value.trim(),
      ];

      const optional = form.optional_context.value.trim();
      if (optional) contextPoints.push(optional);

      payload = {
        company_name: form.company_name.value.trim(),
        industry: form.industry.value.trim(),
        tone: form.tone.value,
        focus: form.focus.value,
        additional_context: contextPoints,
        model_choice: form.model_choice.value,
      };
    }

    payload.user_id = '123345-123345-8234';

    try {
      const res = await fetch("/api/generate-email", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.error || res.statusText);
      }

      const response = await res.json();

      const {
        message,
        prompt_version,
        message_id,
        parent_message_id,
        prompt_text
      } = response;

      lastFeedbackData = {
        message_id,
        parent_message_id: parent_message_id || payload.parent_message_id || null,
        feedback_type: null,
        company_name: payload.company_name,
        industry: payload.industry,
        tone: payload.tone,
        focus: payload.focus,
        context: payload.context || (payload.additional_context || []).join(" "),
        model_used: payload.model_choice,
        prompt_template: prompt_version,
        prompt_text: prompt_text || "",
        generated_message: {
          message: message,
          generated_at: new Date().toISOString()
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
      };

      resultArea.innerHTML = `
        <h2>Generated Email</h2>
        <pre>${message}</pre>
        <button id="upvote">👍 Upvote</button>
        <button id="downvote">👎 Downvote</button>
        <button id="regenerate">🔄 Regenerate</button>
      `;

      document.getElementById("upvote").onclick = () => sendFeedback("upvote");
      document.getElementById("downvote").onclick = () => sendFeedback("downvote");

      document.getElementById("regenerate").onclick = () => {
        const regenPayload = {
          company_name: payload.company_name,
          industry: payload.industry,
          tone: payload.tone,
          focus: payload.focus,
          context: payload.context || (payload.additional_context || []).join(" "),
          model_choice: payload.model_choice,
          parent_message_id: message_id   // KEY for regeneration
        };
        generateOrRegenerate(regenPayload);
      };

    } catch (err) {
      resultArea.innerHTML = `<p style="color: red;">Error: ${err.message}</p>`;
    }
  }

  async function sendFeedback(type) {
    if (!lastFeedbackData) return;

    const feedbackPayload = {
      ...lastFeedbackData,
      feedback_type: type,
      user_id: '123345-123345-8234'
    };

    const res = await fetch("/api/feedback", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(feedbackPayload)
    });

    await res.json();
    alert("Thanks for your feedback!");
  }
});
