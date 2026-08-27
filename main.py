from fastapi import FastAPI, Request
import uvicorn
import os

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Panel Running"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
