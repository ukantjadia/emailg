import uuid
import logging
import asyncio
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify
from controllers.prompt_controller import PromptController
from controllers.generate_controller import GenerateController
from controllers.feedback_controller import FeedbackController
from config.config import Config
from models.feedback_model import MessageFeedback, db

logger = logging.getLogger(__name__)
input_form = Blueprint("email_ui", __name__)

gen_ctrl = GenerateController()
fb_ctrl  = FeedbackController()

DEFAULT_TONES = ["professional", "friendly", "direct"]  # enthusiastic removed


@input_form.route("/", methods=["GET"])
@input_form.route("/email-generator", methods=["GET"])
def show_email_form():
    return render_template("email_generator.html")


# Alias BOTH endpoints to the same logic: initial gen + regenerations
@input_form.route("/api/generate-email", methods=["POST"])
@input_form.route("/api/generate-email-all-tones", methods=["POST"])
def generate_email_all_tones():
    """
    Handles both:
     - initial generation (no parent_message_id, all DEFAULT_TONES)
     - regenerations (parent_message_id supplied, tones override)
    """
    data     = request.get_json(force=True)
    company  = data.get("company_name", "").strip()
    industry = data.get("industry", "").strip()
    focus    = data.get("focus", "")
    model    = data.get("model_choice", "")
    contexts = data.get("additional_context", [])
    parent   = data.get("parent_message_id")    # will be None on first gen

    # validation
    if not (company and industry and focus and model and contexts):
        return jsonify({"error": "Missing required fields"}), 400
    for i, pt in enumerate(contexts[:3]):
        if len(pt.split()) < 20:
            return jsonify({"error": f"Context point {i+1} must be ≥20 words."}), 400
    context = " ".join(contexts)

    # override tones on regen, else use all three
    tones = data.get("tones") or DEFAULT_TONES

    async def build_and_call(tone):
        prompt = PromptController.build_prompt(tone, focus, company, industry, context)
        message = await asyncio.to_thread(
            GenerateController.generate_with_model,
            prompt, model
        )
        return tone, prompt, message

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
    user_id = data.get("user_id", "anonymous")
    for tone, prompt_text, msg in results:
        msg_id = str(uuid.uuid4())
        # persist the 'generation' record, now including parent if any
        fb_ctrl.capture_feedback({
            "message_id":        msg_id,
            "parent_message_id": parent,
            "feedback_type":     "generation",
            "user_id":           user_id,
            "company_name":      company,
            "industry":          industry,
            "tone":              tone,
            "focus":             focus,
            "context":           context,
            "model_used":        model,
            "prompt_template":   f"{tone}_{focus}_{Config.PROMPT_TEMPLATE_VERSION}",
            "prompt_text":       prompt_text,
            "generated_message": {
                "message":      msg,
                "generated_at": datetime.utcnow().isoformat()
            }
        })
        output.append({
            "tone":       tone,
            "message_id": msg_id,
            "message":    msg
        })

    return jsonify(output), 200


@input_form.route("/api/feedback", methods=["POST"])
def submit_feedback():
    data = request.get_json(force=True)
    logger.info("Feedback request: %s", data)
    result = fb_ctrl.capture_feedback(data)
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

    # format first timestamp
    from datetime import datetime as dt
    for m in messages:
        ts = m["entries"][0]["timestamp"]
        try:
            obj = dt.fromisoformat(ts)
            m["first_timestamp_fmt"] = obj.strftime("%b %d, %Y %I:%M %p")
        except:
            m["first_timestamp_fmt"] = ts.split(".")[0]

    return render_template("feedback_view.html", messages=messages)
