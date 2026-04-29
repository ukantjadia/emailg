from flask import Blueprint, request, jsonify
from controllers.feedback_controller import FeedbackController

feedback_bp = Blueprint('feedback', __name__)
feedback_controller = FeedbackController()

@feedback_bp.route('/feedback', methods=['POST'])
def capture_feedback():
    return jsonify(feedback_controller.capture_feedback(request.json))

@feedback_bp.route('/analytics', methods=['GET'])
def get_analytics():
    filters = request.args.to_dict()
    return jsonify(feedback_controller.get_feedback_analytics(filters))

@feedback_bp.route('/history', methods=['GET'])
def get_user_history():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'error': 'Missing required parameter: user_id'}), 400
    return jsonify(FeedbackController.get_user_feedback_history(user_id))
