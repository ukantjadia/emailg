from flask import Flask
from flask_cors import CORS
from routes.input_form_routes import input_form
from routes.main_routes import main_bp
from logging_setup import setup_logging     # Enable logging
from config.config import config
from models import db
from models.feedback_model import MessageFeedback  # <-- Import here, not in __init__.py

def create_app(config_class=config):
    """Create and configure the Flask application"""
    setup_logging()
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(config_class)
    db.init_app(app)

    # Production cookie settings for session auth
    app.config["SESSION_COOKIE_SAMESITE"] = "None"
    app.config["SESSION_COOKIE_SECURE"] = True

    # 🌐 Enable CORS with allowed origins if provided
    # Initialize CORS
    CORS(app, origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "https://35.165.209.201",
        "https://main.d2fzqm2i2qb7f3.amplifyapp.com",
        "http://35.165.209.201",
        "https://sandboxdev.saasquatchleads.com",
        "https://www.saasquatchleads.com",
        "http://54.166.155.63:3000",
        "http://54.166.155.63",
        "https://app.saasquatchleads.com",
    ], methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
       allow_headers=["Content-Type", "Authorization"],
       supports_credentials=True)

    # 🔌 Register the email generation API
    app.register_blueprint(input_form)
    app.register_blueprint(main_bp)

    with app.app_context():
        print("creating the edb db ")
        print('DB URI:', app.config['SQLALCHEMY_DATABASE_URI'])
        db.create_all()  # This will create tables if they do not exist

    return app

app = create_app()

# 🚀 Start the Flask app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8001)
