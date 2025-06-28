from flask import Blueprint, render_template

bp = Blueprint("email_ui", __name__)

@bp.route("/email-generator", methods=["GET"])
def show_email_form():
    return render_template("email_generator.html")
