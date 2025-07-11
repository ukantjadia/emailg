# routes/input_form_routes.py

import uuid
import logging
import asyncio
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify

from controllers.prompt_controller import PromptController
from controllers.generate_controller import GenerateController
from controllers.feedback_controller import FeedbackController
from config.config import Config
from models.feedback_model import MessageFeedback

logger = logging.getLogger(__name__)
input_form = Blueprint("email_ui", __name__)

DEFAULT_TONES = ["professional", "friendly", "direct"]  # enthusiastic removed

@input_form.route("/", methods=["GET"])
@input_form.route("/email-generator", methods=["GET"])
def show_email_form():
    return render_template("email_generator.html")


@input_form.route("/api/generate-email", methods=["POST"])
def generate_email():
    """
    Handles both initial generation and regenerations.
    Validates inputs (including context word‐count) and
    delegates to GenerateController.generate_all.
    """
    data     = request.get_json(force=True)
    company  = data.get("company_name", "").strip()
    industry = data.get("industry", "").strip()
    focus    = data.get("focus", "")
    model    = data.get("model_choice", "")
    contexts = data.get("additional_context", [])
    parent   = data.get("parent_message_id")  # None on first gen

    # --- ROUTE‐LEVEL VALIDATION ---
    if not (company and industry and focus and model):
        return jsonify({"error": "Missing required fields"}), 400

    # must have at least three context points
    if len(contexts) < 3:
        return jsonify({"error": "At least 3 context points required"}), 400

    # each of the first 3 contexts must be ≥20 words
    for i, pt in enumerate(contexts[:3]):
        if len(pt.split()) < 20:
            return jsonify({"error": f"Context point {i+1} must be ≥20 words."}), 400

    # now safe to join
    data["context_text"] = " ".join(contexts)

    try:
        results = GenerateController.generate_all(data)
        return jsonify(results), 200

    except ValueError as ve:
        logger.warning("Validation error: %s", ve)
        return jsonify({"error": str(ve)}), 400

    except Exception:
        logger.exception("Generation failed")
        return jsonify({"error": "Generation failed"}), 500


@input_form.route("/api/feedback", methods=["POST"])
def submit_feedback():
    data = request.get_json(force=True)
    logger.info("Feedback request: %s", data)
    result = FeedbackController.capture_feedback(data)
    status = 200 if result.get("success") else 400
    return jsonify(result), status


@input_form.route("/feedback-view", methods=["GET"])
def feedback_view():
    all_rows = MessageFeedback.query.order_by(
        MessageFeedback.timestamp.desc()
    ).all()

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
