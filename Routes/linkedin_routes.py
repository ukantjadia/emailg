from flask import Blueprint, request, jsonify
from controllers import generate_linkedin_controller

linkedin_bp = Blueprint('linkedin_bp', __name__)

@linkedin_bp.route('/generate_linkedin_message', methods=['POST'])
def generate_linkedin_message():
    try:
        data = request.get_json()
        tone = data.get('tone')
        name = data.get('name')
        company = data.get('company')
        purpose = data.get('purpose')
        word_limit = data.get('word_limit', 100)  # Default to 100 words

        result = generate_linkedin_controller.generate_linkedin_message(
            tone=tone,
            name=name,
            company=company,
            purpose=purpose,
            word_limit=word_limit
        )
        return jsonify({"message": result, "status": "success"})
    except Exception as e:
        return jsonify({"message": str(e), "status": "error"}), 500
