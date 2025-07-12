
from fastapi import FastAPI, Request
import hmac
import hashlib
import os
import httpx

app = FastAPI()

API_KEY = os.getenv("OKX_API_KEY")
API_SECRET = os.getenv("OKX_API_SECRET")
API_PASSPHRASE = os.getenv("OKX_API_PASSPHRASE")

@app.post("/webhook")
async def webhook(request: Request):
    payload = await request.json()
    signal = payload.get("signal")

    if signal not in ["buy", "sell"]:
        return {"status": "error", "message": "Invalid signal"}

    # This is a stub for now — here you would build your trade execution logic
    print(f"Received {signal} signal")

    return {"status": "success", "signal": signal}
