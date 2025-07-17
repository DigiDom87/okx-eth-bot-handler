from flask import Flask, request, jsonify
import os, time, hmac, hashlib, requests, json

app = Flask(__name__)

API_KEY    = os.getenv("MEXC_API_KEY")
API_SECRET = os.getenv("MEXC_API_SECRET")
BASE_URL   = "https://contract.mexc.com"

LEVERAGE   = 3
SYMBOL     = "ETH_USDT"   # MEXC perpetual

def sign(params: dict, timestamp: str) -> str:
    # build the prehash string: sorted key=val pairs + &timestamp=
    sorted_items = sorted(params.items())
    payload = "&".join(f"{k}={v}" for k, v in sorted_items)
    payload += f"&timestamp={timestamp}"
    return hmac.new(API_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()

def get_usdt_balance() -> float:
    """Fetches your available USDT balance from MEXC Futures."""
    url = BASE_URL + "/api/v1/private/account/assets"
    timestamp = str(int(time.time()*1000))
    params = {"currency": "USDT"}
    signature = sign(params, timestamp)
    headers = {
        "ApiKey":      API_KEY,
        "Request-Time": timestamp,
        "Signature":   signature
    }
    r = requests.get(url, params=params, headers=headers)
    data = r.json()
    print("📊 Balance response:", data, flush=True)
    # data["data"] is a list — find the USDT entry
    for asset in data.get("data", []):
        if asset.get("currency") == "USDT":
            return float(asset.get("availableBalance", 0))
    return 0.0

def place_mexc_order(side: int, vol: float):
    """Places a market order on MEXC Futures."""
    url = BASE_URL + "/api/v1/private/order/submit"
    timestamp = str(int(time.time()*1000))
    order = {
        "symbol":     SYMBOL,
        "price":      0,           # 0 for market
        "vol":        vol,         # contract qty
        "leverage":   LEVERAGE,
        "side":       side,        # 1=Open Long, 2=Open Short
        "type":       1,           # 1=Market
        "open_type":  "isolated",
        "position_id":0,
        "external_oid": str(timestamp)
    }
    signature = sign(order, timestamp)
    headers = {
        "ApiKey":       API_KEY,
        "Request-Time": timestamp,
        "Signature":    signature,
        "Content-Type": "application/json"
    }
    print("🚀 Sending order:", order, flush=True)
    r = requests.post(url, json=order, headers=headers)
    print("📩 MEXC response:", r.status_code, r.text, flush=True)
    return r.json()

@app.route("/", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True)
        print("✅ Alert received:", data, flush=True)

        price = float(data.get("price", 0))
        action = data.get("action", "buy").lower()
        # determine side
        side = 1 if action in ("buy","long") else 2

        # fetch balance and calculate vol
        balance = get_usdt_balance()
        if balance <= 0:
            raise ValueError("USDT balance is zero or unavailable")
        vol = (balance * LEVERAGE) / price
        vol = round(vol, 3)

        # place the trade
        result = place_mexc_order(side, vol)
        return jsonify({"status":"ok","order":result}), 200

    except Exception as e:
        print("❌ Error in webhook:", e, flush=True)
        return jsonify({"status":"error","message":str(e)}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)))

