from flask import Blueprint, render_template, request, redirect, url_for

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Redirect to email generator page"""
    return redirect('/email-generator')


@main_bp.route('/docs')
def user_docs():
    """Render the user documentation page (coming soon message)"""
    return """
    <html>
        <head>
            <title>Documentation Coming Soon</title>
            <style>
                body { font-family: Arial, sans-serif; background: #f9f9f9; }
                .centered { max-width: 500px; margin: 100px auto; padding: 2em; background: #fff; border-radius: 8px; box-shadow: 0 2px 8px #eee; text-align: center; }
                h1 { color: #2d7be5; }
                p { color: #555; }
            </style>
        </head>
        <body>
            <div class="centered">
                <h1>🚧 Documentation Coming Soon!</h1>
                <p>We're working hard to bring you comprehensive user documentation.<br>
                Please check back later.</p>
            </div>
        </body>
    </html>
    """


@main_bp.route('/endpoints')
def endpoints():
    """Render a page listing all API endpoints"""
    return render_template('endpoints.html')
