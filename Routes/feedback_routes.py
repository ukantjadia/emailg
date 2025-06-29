from flask import Blueprint, request, jsonify
from controllers.feedback_controller import FeedbackController

feedback_bp = Blueprint('feedback', __name__)
feedback_controller = FeedbackController()

@feedback_bp.route('/feedback', methods=['POST'])
def capture_feedback():
    return jsonify(feedback_controller.capture_feedback(request.json))

@feedback_bp.route('/regenerate', methods=['POST'])
def regenerate_content():
    return jsonify(feedback_controller.handle_regeneration(request.json))

@feedback_bp.route('/analytics', methods=['GET'])
def get_analytics():
    filters = request.args.to_dict()
    return jsonify(feedback_controller.get_feedback_analytics(filters))