from flask import Flask, render_template
from Routes.email_routes import email_api  # POST /api/generate-email route
from logging_setup import setup_logging     # Enable logging

# 🔧 Setup logging first
setup_logging()

# 🔨 Initialize Flask app
app = Flask(__name__, template_folder='templates', static_folder='static')

# 🔌 Register the email generation API
app.register_blueprint(email_api)

# 🌐 Route to render the HTML form
@app.route('/')
@app.route('/email-generator')
def email_generator():
    return render_template('email_generator.html')

# 🚀 Start the Flask app
if __name__ == '__main__':
    app.run(debug=True)
