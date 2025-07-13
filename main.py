
from flask import Flask, request, jsonify
import os
import time
import hmac
import hashlib
import requests

app = Flask(__name__)

MEXC_API_KEY = os.getenv("MEXC_API_KEY")
MEXC_API_SECRET = os.getenv("MEXC_API_SECRET")

def place_mexc_market_order(symbol, vol, side, open_type="ISOLATED", leverage=3):
    url = "https://api.mexc.com/api/v1/private/future/order/place"
    timestamp = str(int(time.time() * 1000))

    body = {
        "symbol": symbol,
        "price": "0",  # required by MEXC even for market orders
        "vol": vol,
        "leverage": leverage,
        "side": side,  # 1=Open Long, 2=Open Short, 3=Close Long, 4=Close Short
        "type": 1,     # 1 = Market order
        "open_type": open_type,
        "position_id": 0,
        "external_oid": str(int(time.time())),
        "stop_loss_price": "",
        "take_profit_price": "",
        "position_mode": 1
    }

    sign_payload = "&".join([f"{key}={body[key]}" for key in sorted(body)])
    sign_payload += f"&timestamp={timestamp}"
    signature = hmac.new(MEXC_API_SECRET.encode(), sign_payload.encode(), hashlib.sha256).hexdigest()

    headers = {
        "Content-Type": "application/json",
        "ApiKey": MEXC_API_KEY,
        "Request-Time": timestamp,
        "Signature": signature
    }

    response = requests.post(url, json=body, headers=headers)
    return response.json()

@app.route("/", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True)
        print("✅ Received TradingView Alert:", data, flush=True)

        if data.get("strategy") == "live":
            symbol = "ETH_USDT"
            contracts = str(data.get("contracts", "1"))
            # Default to long. Advanced logic can be added for shorts.
            trade_response = place_mexc_market_order(symbol=symbol, vol=contracts, side=1)
            print("📤 Sent order to MEXC:", trade_response, flush=True)

        return jsonify({"status": "received"}), 200

    except Exception as e:
        print("❌ Error receiving alert:", e, flush=True)
        return jsonify({"status": "error", "message": str(e)}), 400
