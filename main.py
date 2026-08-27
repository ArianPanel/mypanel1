from fastapi import FastAPI, Request
import uvicorn, secrets

app = FastAPI()

# متن اصلی پنل (صفحه لاگین و مدیریت) اینجا قرار میگیرد
@app.get("/")
def root():
    return {"message": "Panel Running"}

# برای فعالسازی کانفیگها، مسیر WebSocket باید به هسته Xray متصل شود
@app.get("/ws/vless/{uuid}")
async def proxy_ws(uuid: str, request: Request):
    # این بخش در پروژههای کامل به هسته Xray متصل میشود
    return {"status": "running", "uuid": uuid}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
