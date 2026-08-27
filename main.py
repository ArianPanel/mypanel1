from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import uvicorn
import os
import hashlib
import secrets

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# اطلاعات اولیه (برای تست - بعداً باید در دیتابیس ذخیره شود)
ADMIN_USER = "admin"
ADMIN_PASS_HASH = hashlib.sha256("admin123".encode()).hexdigest()

# ذخیره کانفیگ‌های ساخته شده
CONFIGS = {}


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})


@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == ADMIN_USER and hashlib.sha256(password.encode()).hexdigest() == ADMIN_PASS_HASH:
        return templates.TemplateResponse("dashboard.html", {"request": request, "configs": CONFIGS})
    return templates.TemplateResponse("login.html", {"request": request, "error": "Wrong credentials"})


@app.post("/create_config")
async def create_config(name: str = Form(...), protocol: str = Form(...)):
    uuid = secrets.token_hex(16)
    config = {"name": name, "protocol": protocol, "uuid": uuid}
    CONFIGS[name] = config
    return templates.TemplateResponse("dashboard.html", {"request": request, "configs": CONFIGS})
