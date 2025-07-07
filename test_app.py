from flask import Flask, render_template, request
from flask_cors import CORS
from routes.linkedin_routes import linkedin_bp
import os

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# Register only LinkedIn Blueprint
app.register_blueprint(linkedin_bp)

@app.route("/")
def home():
    sample_message = (
        "Hey John! Saw your profile — awesome stuff at OpenAI! "
        "Just wanted to reach out because we might collaborate on AI tools. "
        "Let’s connect if you're up for it!"
    )
    return render_template("linkedin_output.html", message=sample_message)


@app.route("/linkedin_preview", methods=["POST"])
def linkedin_preview():
    message = request.form.get("message", "")
    return render_template("linkedin_output.html", message=message)

if __name__ == '__main__':
    app.run(debug=True, port=8080)
