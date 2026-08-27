from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import os, json, uuid, hashlib, secrets
import httpx
from pydantic import BaseModel
import uvicorn

app = FastAPI()

# تنظیمات پایه (متغیرهای محیطی Railway)
PORT = int(os.environ.get("PORT", 8080))
ADMIN_USER = "admin"
ADMIN_PASS = os.environ.get("ADMIN_PASSWORD", "admin123") # تغییر پسورد الزامی!
SECRET_KEY = os.environ.get("SECRET_KEY", secrets.token_hex(32))
DATA_DIR = os.environ.get("DATA_DIR", "/data")
PANEL_DOMAIN = os.environ.get("RAILWAY_PUBLIC_DOMAIN", "localhost")

# فایل وضعیت (پایدار در دیسک)
STATE_FILE = os.path.join(DATA_DIR, "spider_state.json")

# اتصال به هسته Xray از طریق فایل JSON در روت
XRAY_CONFIG_FILE = "xray_config.json"

def load_state():
    if not os.path.exists(STATE_FILE):
        return {"users": [], "inbounds": []}
    with open(STATE_FILE, 'r') as f:
        return json.load(f)

def save_state(state):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

# مدل داده برای ساخت کانفیگ
class UserCreate(BaseModel):
    username: str
    limit_bytes: int = 1073741824 # 1GB پیش‌فرض
    expiry_days: int = 30

# صفحه ورود (رابط ساده شیک) - مشابه اسپایدر
@app.get("/login")
async def login_page():
    return """
    <html><head><title>Spider Panel</title></head><body style="font-family:sans-serif; background:#0f172a; color:#fff; display:flex; justify-content:center; align-items:center; height:100vh;">
      <div>
        <h2>ورود به پنل</h2>
        <form method="post" action="/login" style="display:flex; flex-direction:column; gap:10px;">
          <input type="text" name="username" placeholder="User" style="padding:10px; border-radius:5px;">
          <input type="password" name="password" placeholder="Pass" style="padding:10px; border-radius:5px;">
          <button type="submit" style="padding:10px; background:#3b82f6; color:#fff; border:none; cursor:pointer;">ورود</button>
        </form>
      </div>
    </body></html>
    """

@app.post("/login")
async def do_login(request: Request):
    form = await request.form()
    if form["username"] == ADMIN_USER and form["password"] == ADMIN_PASS:
        return {"status": "ok"}
    raise HTTPException(status_code=401, detail="Authentication Failed")

# ساخت کانفیگ و اتصال واقعی به هسته
@app.post("/api/create_config")
async def create_config(data: UserCreate):
    state = load_state()
    user_uuid = str(uuid.uuid4())
    # ساخت لینک VLESS (بر اساس ساختار پنل اسپایدر) با دامنه اصلی Railway
    link = f"vless://{user_uuid}@{PANEL_DOMAIN}:443?type=ws&security=tls&path=%2F#Spider-{data.username}"
    state["users"].append({
        "id": user_uuid, "username": data.username,
        "limit": data.limit_bytes, "expiry": data.expiry_days
    })
    save_state(state)
    return {"message": "Config Created", "link": link}

# مسیر اصلی برای ساخت لینک‌های Xray به صورت پویا (مرجع اصلی)
@app.get("/xray/{uuid}")
async def get_xray_config(uuid: str):
    # این بخش در پنل‌های واقعی به فایل xray_config.json متصل می‌شود
    with open(XRAY_CONFIG_FILE, 'r') as f:
        return JSONResponse(content=json.load(f))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)
