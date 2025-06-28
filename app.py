from flask import Flask, render_template

app = Flask(__name__, template_folder='templates', static_folder='static')

@app.route('/')
@app.route('/email-generator')
def email_generator():
    return render_template('email_generator.html')

if __name__ == '__main__':
    app.run(debug=True)
# Flask app entry point
