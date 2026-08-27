from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn
import os
import hashlib
import secrets

app = FastAPI()
templates = Jinja2Templates(directory="templates")

ADMIN_USER = "admin"
ADMIN_PASS_HASH = hashlib.sha256("admin123".encode()).hexdigest()
CONFIGS = {}


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == ADMIN_USER and hashlib.sha256(password.encode()).hexdigest() == ADMIN_PASS_HASH:
        return templates.TemplateResponse("dashboard.html", {"request": request, "configs": CONFIGS})
    return templates.TemplateResponse("login.html", {"request": request, "error": "Wrong credentials"})


@app.post("/create_config")
async def create_config(request: Request, name: str = Form(...), protocol: str = Form(...)):
    uuid = secrets.token_hex(16)
    config = {"name": name, "protocol": protocol, "uuid": uuid}
    CONFIGS[name] = config
    return templates.TemplateResponse("dashboard.html", {"request": request, "configs": CONFIGS})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
