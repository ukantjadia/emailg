import os
import re

BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # emailgen/
ROUTES_DIR = os.path.join(BASE_DIR, 'routes')
TEMPLATE_PATH = os.path.join(BASE_DIR, 'templates', 'endpoints.html')

route_pattern = re.compile(
    r"""@[\w_]+\.route\(\s*['"]([^'"]+)['"](?:\s*,\s*methods\s*=\s*(\[[^\]]+\]))?""",
    re.MULTILINE
)

def extract_routes_from_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    routes = []
    for match in route_pattern.finditer(content):
        path = match.group(1)
        methods = match.group(2)
        if methods:
            # Clean up methods string
            methods = methods.replace("'", '"')
            try:
                methods_list = eval(methods)
            except Exception:
                methods_list = ["GET"]
        else:
            methods_list = ["GET"]
        routes.append((path, methods_list))
    return routes

def collect_all_routes():
    all_routes = []
    for filename in os.listdir(ROUTES_DIR):
        if filename.endswith('.py'):
            filepath = os.path.join(ROUTES_DIR, filename)
            routes = extract_routes_from_file(filepath)
            for path, methods in routes:
                all_routes.append((path, methods, filename))
    return all_routes

def generate_html(routes):
    html = [
        "<!DOCTYPE html>",
        "<html lang='en'>",
        "<head>",
        "    <meta charset='UTF-8'>",
        "    <title>API & UI Endpoints</title>",
        "    <link rel='stylesheet' href=\"{{ url_for('static', filename='style.css') }}\">",
        "</head>",
        "<body>",
        "    <div class='card'>",
        "        <h1>Available Endpoints</h1>",
        "        <ul>"
    ]
    for path, methods, filename in sorted(routes):
        html.append(
            f"            <li><strong>{', '.join(methods)}</strong> <code>{path}</code> <em>({filename})</em></li>"
        )
    html += [
        "        </ul>",
        "        <p>For more details, see the <a href='/docs'>documentation</a>.</p>",
        "    </div>",
        "</body>",
        "</html>"
    ]
    return '\n'.join(html)

if __name__ == '__main__':
    routes = collect_all_routes()
    html = generate_html(routes)
    with open(TEMPLATE_PATH, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Endpoints HTML generated at {TEMPLATE_PATH}")
