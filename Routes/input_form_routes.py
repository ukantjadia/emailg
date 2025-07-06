import uuid
import logging
import asyncio
from datetime import datetime as dt
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

DEFAULT_TONES = ["professional", "friendly", "direct"]  # enthusiastic removed

# … your other routes unchanged …

@input_form.route("/feedback-view", methods=["GET"])
def feedback_view():
    all_rows = MessageFeedback.query.order_by(MessageFeedback.timestamp.desc()).all()
    dashboard = {}

    for row in all_rows:
        key = row.parent_message_id or row.message_id
        if key not in dashboard:
            gen = ""
            gm = row.generated_message
            if isinstance(gm, dict):
                gen = gm.get("message", "")
            elif gm:
                gen = gm
            dashboard[key] = {
                "message_id":         key,
                "generated":          gen,
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

    # format the first timestamp for each message
    for m in messages:
        ts = m["entries"][0]["timestamp"]
        try:
            # parse and reformat
            dt_obj = dt.fromisoformat(ts)
            m["first_timestamp_fmt"] = dt_obj.strftime("%b %d, %Y %I:%M %p")
        except Exception:
            # fallback to raw
            m["first_timestamp_fmt"] = ts.split(".")[0]

    return render_template("feedback_view.html", messages=messages)
