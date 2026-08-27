from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
import uvicorn
import os
import hashlib
import secrets

app = FastAPI()

ADMIN_USER = "admin"
ADMIN_PASS_HASH = hashlib.sha256("admin123".encode()).hexdigest()
CONFIGS = {}


@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <h2>🔐 ورود به پنل مدیریت</h2>
    <form method="post" action="/login">
        <input type="text" name="username" placeholder="نام کاربری" required><br><br>
        <input type="password" name="password" placeholder="رمز عبور" required><br><br>
        <button type="submit">ورود</button>
    </form>
    <p>پیش‌فرض: admin / admin123</p>
    """


@app.post("/login", response_class=HTMLResponse)
async def login(username: str = Form(...), password: str = Form(...)):
    if username == ADMIN_USER and hashlib.sha256(password.encode()).hexdigest() == ADMIN_PASS_HASH:
        configs_html = ""
        for name, cfg in CONFIGS.items():
            configs_html += f"<p>{cfg['protocol']}://{cfg['uuid']}@example.com#{cfg['name']}</p>"
        
        return f"""
        <h2>📊 داشبورد</h2>
        <p>تعداد کل کانفیگ‌ها: {len(CONFIGS)}</p>
        <h3>ساخت کانفیگ جدید</h3>
        <form method="post" action="/create_config">
            <input type="text" name="name" placeholder="نام کاربر" required><br><br>
            <select name="protocol">
                <option value="vless">VLESS</option>
                <option value="vmess">VMESS</option>
                <option value="trojan">Trojan</option>
            </select><br><br>
            <button type="submit">ساخت کانفیگ</button>
        </form>
        <h3>لیست کانفیگ‌ها</h3>
        {configs_html}
        """
    return """
    <h2>❌ نام کاربری یا رمز عبور اشتباه است!</h2>
    <a href="/">بازگشت به ورود</a>
    """


@app.post("/create_config", response_class=HTMLResponse)
async def create_config(name: str = Form(...), protocol: str = Form(...)):
    uuid = secrets.token_hex(16)
    config = {"name": name, "protocol": protocol, "uuid": uuid}
    CONFIGS[name] = config
    
    configs_html = ""
    for name, cfg in CONFIGS.items():
        configs_html += f"<p>{cfg['protocol']}://{cfg['uuid']}@example.com#{cfg['name']}</p>"
        
    return f"""
    <h2>✅ کانفیگ {name} ساخته شد!</h2>
    <h2>📊 داشبورد</h2>
    <p>تعداد کل کانفیگ‌ها: {len(CONFIGS)}</p>
    <a href="/">بازگشت به داشبورد</a>
    <br><br>
    <h3>لیست کانفیگ‌ها</h3>
    {configs_html}
    """


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
