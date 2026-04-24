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
    Group all feedback by message_id (or parent_message_id),
    count each feedback_type, and allow inline drill-down.
    """
    all_rows = MessageFeedback.query.order_by(
        MessageFeedback.timestamp.desc()
    ).all()

    dashboard = {}
    for row in all_rows:
        key = row.parent_message_id or row.message_id
        if key not in dashboard:
            # capture one snippet of the generated email
            gen = ""
            gm = row.generated_message
            if isinstance(gm, dict):
                gen = gm.get("message", "")
            elif gm:
                gen = gm
            dashboard[key] = {
                "message_id": key,
                "generated": gen,
                "upvote_count": 0,
                "downvote_count": 0,
                "regeneration_count": 0,
                "entries": []
            }
        if row.feedback_type == "upvote":
            dashboard[key]["upvote_count"] += 1
        elif row.feedback_type == "downvote":
            dashboard[key]["downvote_count"] += 1
        elif row.feedback_type == "regeneration":
            dashboard[key]["regeneration_count"] += 1

        dashboard[key]["entries"].append(row.to_dict())

    # sort by newest activity
    messages = sorted(
        dashboard.values(),
        key=lambda m: m["entries"][0]["timestamp"],
        reverse=True
    )

    return render_template("feedback_view.html", messages=messages)

