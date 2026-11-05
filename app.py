from flask import Flask, render_template, request, jsonify, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "spider_man_secret_admin_key_change_this"  # Session security ke liye

# Database (Demo ke liye dictionary, aap ise file ya database se bhi jod sakte hain)
DATABASE = {
    "keys": {
        "SPIDER-WOLF-777": {"active": True, "device_id": None},
        "ADMIN-KEY-999": {"active": True, "device_id": None}
    },
    "config": {
        "is_app_active": True  # Master Kill Switch
    }
}

# Admin Login Credentials
ADMIN_USER = "admin"
ADMIN_PASS = "wolf1ed"

# --- API Endpoints (AIDE Pro App ke liye) ---
@app.route('/api/verify-key', methods=['POST'])
def verify_key():
    data = request.json
    key = data.get('key')
    device_id = data.get('deviceId')

    # Check Master Kill Switch
    if not DATABASE["config"]["is_app_active"]:
        return jsonify({"success": False, "message": "App is locked by Admin!"})

    if not key or key not in DATABASE["keys"]:
        return jsonify({"success": False, "message": "Invalid or expired activation key!"})

    key_data = DATABASE["keys"][key]
    if not key_data["active"]:
        return jsonify({"success": False, "message": "This key has been disabled!"})

    # Device Binding
    if key_data["device_id"] is None:
        key_data["device_id"] = device_id
    elif key_data["device_id"] != device_id:
        return jsonify({"success": False, "message": "Key already bound to another device!"})

    return jsonify({"success": True, "message": "Key verified successfully!"})

# --- Admin Panel Routes ---
@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == ADMIN_USER and password == ADMIN_PASS:
            session['logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('admin.html', error="Invalid Username or Password")
    return render_template('admin.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('admin_login'))
    return render_template('admin.html', data=DATABASE, logged_in=True)

@app.route('/admin/toggle-app', methods=['POST'])
def toggle_app():
    if not session.get('logged_in'):
        return jsonify({"success": False})
    
    current_status = DATABASE["config"]["is_app_active"]
    DATABASE["config"]["is_app_active"] = not current_status
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/add-key', methods=['POST'])
def add_key():
    if not session.get('logged_in'):
        return redirect(url_for('admin_login'))
    
    new_key = request.form.get('new_key')
    if new_key:
        DATABASE["keys"][new_key] = {"active": True, "device_id": None}
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete-key/<key_name>')
def delete_key(key_name):
    if not session.get('logged_in'):
        return redirect(url_for('admin_login'))
    
    if key_name in DATABASE["keys"]:
        del DATABASE["keys"][key_name]
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/logout')
def logout():
    session.clear()
    return redirect(url_for('admin_login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
