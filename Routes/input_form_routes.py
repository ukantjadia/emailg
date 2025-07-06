# routes/input_form_routes.py

import uuid
import logging
import asyncio
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify
from flask import redirect, url_for
from controllers.prompt_controller import PromptController
from controllers.generate_controller import GenerateController
from controllers.feedback_controller import FeedbackController
from config.config import Config
from models.feedback_model import MessageFeedback, db

logger = logging.getLogger(__name__)
input_form = Blueprint("email_ui", __name__)

generate_controller = GenerateController()
feedback_controller = FeedbackController()

# default three tones (enthusiastic removed)
DEFAULT_TONES = ["professional", "friendly", "direct"]


@input_form.route("/", methods=["GET"])
@input_form.route("/email-generator", methods=["GET"])
def show_email_form():
    """
    Serves the Email Generator UI.  Now aliased to both “/” and “/email-generator”.
    """
    return render_template("email_generator.html")


@input_form.route("/api/generate-email-all-tones", methods=["POST"])
def generate_email_all_tones():
    # … your existing code for fan-out generation …
    data     = request.get_json(force=True)
    company  = data.get("company_name", "").strip()
    industry = data.get("industry", "").strip()
    focus    = data.get("focus", "")
    model    = data.get("model_choice", "")
    contexts = data.get("additional_context", [])
    parent   = data.get("parent_message_id")

    if not (company and industry and focus and model and contexts):
        return jsonify({"error": "Missing required fields"}), 400
    for i, pt in enumerate(contexts[:3]):
        if len(pt.split()) < 20:
            return jsonify({"error": f"Context point {i+1} must be ≥20 words."}), 400
    context = " ".join(contexts)

    tones = data.get("tones") or DEFAULT_TONES

    async def build_and_call(tone):
        prompt = PromptController.build_prompt(tone, focus, company, industry, context)
        message = await asyncio.to_thread(
            generate_controller.generate_with_model,
            prompt, model
        )
        return {"tone": tone, "prompt": prompt, "message": message}

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        tasks = [build_and_call(t) for t in tones]
        results = loop.run_until_complete(asyncio.gather(*tasks))
    except Exception as e:
        logger.error("Parallel generation error", exc_info=True)
        return jsonify({"error": str(e)}), 500
    finally:
        loop.close()

    output = []
    for r in results:
        msg_id = str(uuid.uuid4())
        feedback_controller.capture_feedback({
            "message_id":        msg_id,
            "parent_message_id": parent,
            "feedback_type":     "generation",
            "user_id":           data.get("user_id","anonymous"),
            "company_name":      company,
            "industry":          industry,
            "tone":              r["tone"],
            "focus":             focus,
            "context":           context,
            "model_used":        model,
            "prompt_template":   f"{r['tone']}_{focus}_{Config.PROMPT_TEMPLATE_VERSION}",
            "prompt_text":       r["prompt"],
            "generated_message": {
                "message":      r["message"],
                "generated_at": datetime.utcnow().isoformat()
            }
        })
        output.append({
            "tone":       r["tone"],
            "message_id": msg_id,
            "message":    r["message"]
        })

    return jsonify(output), 200


@input_form.route("/api/feedback", methods=["POST"])
def submit_feedback():
    data = request.get_json(force=True)
    logger.info("Feedback request: %s", data)
    result = feedback_controller.capture_feedback(data)
    status = 200 if result.get("success") else 400
    return jsonify(result), status


@input_form.route("/feedback-view", methods=["GET"])
def feedback_view():
    all_rows = MessageFeedback.query.order_by(MessageFeedback.timestamp.desc()).all()
    dashboard = {}

    for row in all_rows:
        key = row.parent_message_id or row.message_id
        if key not in dashboard:
            gm = row.generated_message or {}
            dashboard[key] = {
                "message_id":         key,
                "generated":          gm.get("message", ""),
                "upvote_count":       0,
                "downvote_count":     0,
                "regeneration_count": 0,
                "entries":            []
            }
        if row.feedback_type == "upvote":
            dashboard[key]["upvote_count"] += 1
        elif row.feedback_type == "downvote":
            dashboard[key]["downvote_count"] += 1
        elif row.feedback_type == "regeneration":
            dashboard[key]["regeneration_count"] += 1

        dashboard[key]["entries"].append(row.to_dict())

    messages = sorted(
        dashboard.values(),
        key=lambda m: m["entries"][0]["timestamp"],
        reverse=True
    )

    # format first timestamp for display
    for m in messages:
        ts = m["entries"][0]["timestamp"]
        try:
            dt_obj = datetime.fromisoformat(ts)
            m["first_timestamp_fmt"] = dt_obj.strftime("%b %d, %Y %I:%M %p")
        except Exception:
            m["first_timestamp_fmt"] = ts.split(".")[0]

    return render_template("feedback_view.html", messages=messages)
