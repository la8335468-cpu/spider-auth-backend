from flask import Flask, render_template_string, request, jsonify, redirect, url_for, session
import os

app = Flask(__name__)
app.secret_key = "spider_man_secret_admin_key_change_this"

# Database (Fixed keys conflict issue)
DATABASE = {
    "license_keys": {
        "SPIDER-WOLF-777": {"active": True, "device_id": None},
        "ADMIN-KEY-999": {"active": True, "device_id": None}
    },
    "config": {
        "is_app_active": True  # Master Kill Switch
    }
}

# Admin Credentials
ADMIN_USER = "Aman77"
ADMIN_PASS = "Aman77"

# Root URL open hone par seedha /admin par bhej dega
@app.route('/')
def home():
    return redirect(url_for('admin_login'))

# --- API Endpoints (AIDE Pro App ke liye) ---
@app.route('/api/verify-key', methods=['POST'])
def verify_key():
    try:
        data = request.json or {}
        key = data.get('key')
        device_id = data.get('deviceId')

        if not DATABASE["config"]["is_app_active"]:
            return jsonify({"success": False, "message": "App is locked by Admin!"})

        if not key or key not in DATABASE["license_keys"]:
            return jsonify({"success": False, "message": "Invalid or expired activation key!"})

        key_data = DATABASE["license_keys"][key]
        if not key_data["active"]:
            return jsonify({"success": False, "message": "This key has been disabled!"})

        if key_data["device_id"] is None:
            key_data["device_id"] = device_id
        elif key_data["device_id"] != device_id:
            return jsonify({"success": False, "message": "Key already bound to another device!"})

        return jsonify({"success": True, "message": "Key verified successfully!"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

# --- Admin Panel HTML Template ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Spider-Man Admin Panel</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Poppins', sans-serif; }
        body { background: #0b0f19; color: #fff; padding: 20px; display: flex; justify-content: center; }
        .container { width: 100%; max-width: 600px; background: rgba(255,255,255,0.05); backdrop-filter: blur(10px); padding: 30px; border-radius: 15px; border: 1px solid rgba(0,242,254,0.2); margin-top: 40px; }
        h2 { color: #00f2fe; margin-bottom: 20px; text-align: center; }
        h3 { color: #00f2fe; margin-top: 20px; margin-bottom: 10px; font-size: 16px; }
        input, button { width: 100%; padding: 12px; margin: 10px 0; border-radius: 8px; border: 1px solid rgba(255,255,255,0.2); background: rgba(255,255,255,0.05); color: #fff; outline: none; }
        button { background: #ff334b; border: none; font-weight: 600; cursor: pointer; }
        button:hover { opacity: 0.9; }
        table { width: 100%; margin-top: 10px; border-collapse: collapse; }
        th, td { padding: 10px; border-bottom: 1px solid rgba(255,255,255,0.1); text-align: left; font-size: 13px; }
        th { color: #00f2fe; }
        .error { color: #ff334b; text-align: center; font-size: 13px; margin-bottom: 10px; }
        .status-box { background: rgba(0,242,254,0.1); padding: 15px; border-radius: 8px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; }
    </style>
</head>
<body>
    <div class="container">
        {% if not logged_in %}
            <h2>Spider-Man Admin Login</h2>
            {% if error %}<p class="error">{{ error }}</p>{% endif %}
            <form method="POST">
                <input type="text" name="username" placeholder="Username" required>
                <input type="password" name="password" placeholder="Password" required>
                <button type="submit">Login</button>
            </form>
        {% else %}
            <h2>Spider-Man Control Panel</h2>
            
            <div class="status-box">
                <div>
                    <strong>App Status:</strong> 
                    <span style="color: {% if data.config.is_app_active %}#00ffcc{% else %}#ff334b{% endif %};">
                        {% if data.config.is_app_active %}ONLINE (Active){% else %}OFFLINE (Locked){% endif %}
                    </span>
                </div>
                <form action="{{ url_for('toggle_app') }}" method="POST" style="width: auto; margin:0;">
                    <button type="submit" style="padding: 6px 12px; background: {% if data.config.is_app_active %}#ff334b{% else %}#00ffcc{% endif %}; color: #000;">
                        {% if data.config.is_app_active %}Lock App{% else %}Unlock App{% endif %}
                    </button>
                </form>
            </div>

            <h3>Generate New Key</h3>
            <form action="{{ url_for('add_key') }}" method="POST">
                <input type="text" name="new_key" placeholder="Enter New License Key" required>
                <button type="submit">Add Key</button>
            </form>

            <h3>Existing Keys</h3>
            <table>
                <tr>
                    <th>License Key</th>
                    <th>Device Bound</th>
                    <th>Action</th>
                </tr>
                {% for key, info in data.license_keys.items() %}
                <tr>
                    <td>{{ key }}</td>
                    <td>{{ info.device_id if info.device_id else 'Not Bound' }}</td>
                    <td><a href="{{ url_for('delete_key', key_name=key) }}" style="color: #ff334b; text-decoration: none;">Delete</a></td>
                </tr>
                {% endfor %}
            </table>
            
            <br>
            <a href="{{ url_for('logout') }}"><button style="background:#444;">Logout</button></a>
        {% endif %}
    </div>
</body>
</html>
"""

# --- Admin Panel Routes ---
@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == ADMIN_USER and password == ADMIN_PASS:
            session['logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            error = "Invalid Username or Password"
    return render_template_string(HTML_TEMPLATE, logged_in=False, error=error)

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('admin_login'))
    return render_template_string(HTML_TEMPLATE, logged_in=True, data=DATABASE)

@app.route('/admin/toggle-app', methods=['POST'])
def toggle_app():
    if not session.get('logged_in'):
        return redirect(url_for('admin_login'))
    
    current_status = DATABASE["config"]["is_app_active"]
    DATABASE["config"]["is_app_active"] = not current_status
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/add-key', methods=['POST'])
def add_key():
    if not session.get('logged_in'):
        return redirect(url_for('admin_login'))
    
    new_key = request.form.get('new_key')
    if new_key:
        DATABASE["license_keys"][new_key] = {"active": True, "device_id": None}
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete-key/<key_name>')
def delete_key(key_name):
    if not session.get('logged_in'):
        return redirect(url_for('admin_login'))
    
    if key_name in DATABASE["license_keys"]:
        del DATABASE["license_keys"][key_name]
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/logout')
def logout():
    session.clear()
    return redirect(url_for('admin_login'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
