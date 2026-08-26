from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import json
import os
import secrets
from datetime import datetime
import hashlib

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# داده‌ها در حافظه نگهداری می‌شوند تا با ری‌استارت Railway پاک نشوند
USERS = {"admin": {"password": hashlib.sha256("admin123".encode()).hexdigest(), "role": "admin"}}
CONFIGS = {}

def check_auth():
    return session.get('logged_in', False)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in USERS and USERS[username]['password'] == hashlib.sha256(password.encode()).hexdigest():
            session['logged_in'] = True
            session['username'] = username
            session['role'] = USERS[username]['role']
            return redirect(url_for('dashboard'))
        return "❌ نام کاربری یا رمز عبور اشتباه است!"
    return '''
    <h2>🔐 ورود به پنل مدیریت</h2>
    <form method="post">
        <input type="text" name="username" placeholder="نام کاربری" required><br><br>
        <input type="password" name="password" placeholder="رمز عبور" required><br><br>
        <button type="submit">ورود</button>
    </form>
    <p>پیش‌فرض: admin / admin123</p>
    '''

@app.route('/')
@app.route('/dashboard')
def dashboard():
    if not check_auth():
        return redirect(url_for('login'))
    return f'''
    <h2>📊 داشبورد</h2>
    <p>تعداد کل کانفیگ‌ها: {len(CONFIGS)}</p>
    <p>کاربران فعال: {sum(1 for c in CONFIGS.values() if c.get('status') == 'active')}</p>
    <br>
    <a href="/create_config">➕ ساخت کانفیگ جدید</a><br>
    <a href="/logout">🚪 خروج</a>
    '''

@app.route('/create_config', methods=['GET', 'POST'])
def create_config():
    if not check_auth():
        return redirect(url_for('login'))
    if request.method == 'POST':
        name = request.form['name']
        protocol = request.form['protocol']
        expiry = request.form['expiry']
        data_limit = request.form['data_limit']
        config = {
            "name": name,
            "protocol": protocol,
            "expiry": expiry,
            "data_limit": data_limit,
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "uuid": secrets.token_hex(16)
        }
        CONFIGS[name] = config
        return f"✅ کانفیگ {name} ساخته شد! <a href='/'>بازگشت</a>"
    return '''
    <h2>🛠️ ساخت کانفیگ جدید</h2>
    <form method="post">
        <input type="text" name="name" placeholder="نام کاربر" required><br><br>
        <select name="protocol">
            <option value="vless">VLESS</option>
            <option value="vmess">VMESS</option>
            <option value="trojan">Trojan</option>
        </select><br><br>
        <input type="date" name="expiry" required><br><br>
        <input type="text" name="data_limit" placeholder="محدودیت حجم (مثلا 10GB)" value="10GB"><br><br>
        <button type="submit">ساخت کانفیگ</button>
    </form>
    '''

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
