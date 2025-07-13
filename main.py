from flask import Flask, request, jsonify
import os
import hmac
import hashlib

app = Flask(__name__)

@app.route("/", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True)
        print("✅ Received TradingView Alert:")
        print(data, flush=True)
        return jsonify({"status": "received"}), 200
    except Exception as e:
        print("❌ Error receiving alert:", e, flush=True)
        return jsonify({"status": "error", "message": str(e)}), 400
