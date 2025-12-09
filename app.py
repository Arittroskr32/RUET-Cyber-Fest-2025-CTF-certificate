from flask import Flask, render_template, request, redirect, url_for
import hashlib
import os
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'change-this-secret-key-in-production')

CERTIFICATE_PORT = int(os.environ.get('CERTIFICATE_PORT', '5000'))
CERTIFICATES_DB = 'certificates.json'

def load_certificates():
    """Load certificates database"""
    if os.path.exists(CERTIFICATES_DB):
        with open(CERTIFICATES_DB, 'r') as f:
            return json.load(f)
    return []

def save_certificate(cert_data):
    """Save certificate to database"""
    certs = load_certificates()
    certs.append(cert_data)
    with open(CERTIFICATES_DB, 'w') as f:
        json.dump(certs, f, indent=2)

def generate_certificate_hash(full_name, position, timestamp):
    """
    Generate MD5 hash based on full name, position, and timestamp
    Format: Full_Name:Position_in_digit:Timestamp
    Returns: x + hash (lowercase hex)
    """
    data = f"{full_name}:{position}:{timestamp}"
    hash_obj = hashlib.md5(data.encode())
    return 'x' + hash_obj.hexdigest()

@app.route('/')
def index():
    """Main certificate page - displays form for manual input"""
    return render_template('certificate.html')

@app.route('/generate', methods=['POST'])
def generate_certificate():
    """Generate certificate from manual input"""
    roll = request.form.get('roll', '').strip()
    if not roll:
        return render_template('certificate.html', error='Please enter a roll number')

    # Load info.json and find entry
    info_path = 'info.json'
    if not os.path.exists(info_path):
        return render_template('certificate.html', error='info.json not found')
    with open(info_path, 'r', encoding='utf-8') as f:
        infos = json.load(f)
    entry = next((item for item in infos if item.get('roll') == roll), None)
    if not entry or not entry.get('name') or not str(entry.get('position')).isdigit():
        return render_template('certificate.html', error='Invalid roll number')

    full_name = entry['name'].strip()
    position = int(entry['position'])

    # Generate timestamp and certificate hash
    timestamp = datetime.now().isoformat()
    cert_hash = generate_certificate_hash(full_name, position, timestamp)

    # Save certificate to database
    cert_data = {
        'display_name': full_name,
        'position': position,
        'hash': cert_hash,
        'timestamp': timestamp,
        'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    save_certificate(cert_data)

    return render_template('certificate.html',
                         display_name=full_name,
                         position=position,
                         cert_hash=cert_hash,
                         event_name='RUET Cyber Fest CTF 2025',
                         event_date=datetime.now().strftime('%B %d, %Y'),
                         certificate_generated=True)


def batch_generate_certificates():
    from jinja2 import Environment, FileSystemLoader
    info_path = 'info.json'
    cert_dir = 'certificate'
    template_path = 'templates'
    template_file = 'certificate.html'
    event_name = 'RUET Cyber Fest CTF 2025'
    event_date = datetime.now().strftime('%B %d, %Y')

    # Load info.json
    with open(info_path, 'r', encoding='utf-8') as f:
        infos = json.load(f)

    # Prepare Jinja2 environment
    env = Environment(loader=FileSystemLoader(template_path))
    template = env.get_template(template_file)

    os.makedirs(cert_dir, exist_ok=True)

    # Helper: fix image paths for local HTML viewing
    def fix_img_paths(html):
        return html.replace('/static/', 'static/')

    # Try to import imgkit for PNG export
    try:
        import imgkit
        imgkit_available = True
    except ImportError:
        imgkit_available = False
        print("imgkit not installed. PNG export will be skipped. Install with: pip install imgkit and install wkhtmltoimage.")

    for entry in infos:
        name = entry.get('name', '').strip()
        position = entry.get('position', '')
        roll = entry.get('roll', '')
        if not name or not str(position).isdigit() or not roll:
            print(f"Skipping roll {roll}: missing or invalid data.")
            continue
        position = int(position)
        timestamp = datetime.now().isoformat()
        cert_hash = generate_certificate_hash(name, position, timestamp)
        cert_data = {
            'display_name': name,
            'position': position,
            'cert_hash': cert_hash,
            'event_name': event_name,
            'event_date': event_date,
            'certificate_generated': True
        }
        rendered = template.render(**cert_data)
        rendered_fixed = fix_img_paths(rendered)
        out_html = os.path.join(cert_dir, f"{roll}.html")
        with open(out_html, 'w', encoding='utf-8') as outf:
            outf.write(rendered_fixed)
        print(f"Generated certificate HTML for {name} (Roll: {roll}) -> {out_html}")

        # PNG export
        if imgkit_available:
            out_png = os.path.join(cert_dir, f"{roll}.png")
            options = {
                'format': 'png',
                'encoding': 'UTF-8',
                'width': 1200,
                'height': 850,
                'quiet': ''
            }
            try:
                imgkit.from_string(rendered_fixed, out_png, options=options)
                print(f"Generated certificate PNG for {name} (Roll: {roll}) -> {out_png}")
            except Exception as e:
                print(f"Failed to generate PNG for {roll}: {e}")

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'batch':
        batch_generate_certificates()
    else:
        print(f"""
╔═══════════════════════════════════════════════════════════════╗
║          CTF Certificate Generator - Manual Mode              ║
║═══════════════════════════════════════════════════════════════║
║   Port: {CERTIFICATE_PORT}                                    ║
║   Mode: Manual Name and Position Input                        ║
╚═══════════════════════════════════════════════════════════════╝
        """)
        app.run(debug=True, host='0.0.0.0', port=CERTIFICATE_PORT)
