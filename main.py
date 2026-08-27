from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import os, json, uuid, hashlib, secrets
import uvicorn

app = FastAPI()

# تنظیمات پایه
PORT = int(os.environ.get("PORT", 8080))
ADMIN_USER = "admin"
ADMIN_PASS = os.environ.get("ADMIN_PASSWORD", "admin123")
DATA_DIR = os.environ.get("DATA_DIR", "/data")
PANEL_DOMAIN = os.environ.get("RAILWAY_PUBLIC_DOMAIN", "localhost")
XRAY_CONFIG_FILE = "xray_config.json"

def load_state():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)
    state_file = os.path.join(DATA_DIR, "spider_state.json")
    if not os.path.exists(state_file):
        return {"users": []}
    with open(state_file, 'r') as f:
        return json.load(f)

def save_state(state):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(os.path.join(DATA_DIR, "spider_state.json"), 'w') as f:
        json.dump(state, f, indent=2)

# صفحه ورود
@app.get("/login")
async def login_page():
    return """
    <html><head><title>Panel</title></head><body style="font-family:sans-serif; background:#0f172a; color:#fff; display:flex; justify-content:center; align-items:center; height:100vh;">
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

# ساخت کانفیگ
@app.post("/api/create_config")
async def create_config(request: Request):
    form = await request.form()
    user_uuid = str(uuid.uuid4())
    link = f"vless://{user_uuid}@{PANEL_DOMAIN}:443?type=ws&security=tls&path=%2F#Panel"
    state = load_state()
    state["users"].append({"id": user_uuid, "username": form["username"]})
    save_state(state)
    return {"message": "Config Created", "link": link}

# مسیر اتصال به هسته Xray
@app.get("/xray/{uuid}")
async def get_xray_config(uuid: str):
    with open(XRAY_CONFIG_FILE, 'r') as f:
        return JSONResponse(content=json.load(f))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)
