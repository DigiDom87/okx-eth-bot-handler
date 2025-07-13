from flask import Flask, request, jsonify
import os
import hmac
import hashlib

app = Flask(__name__)

@app.route("/", methods=["POST"])
def webhook():
    data = request.json
    print("Received TradingView Alert:", data)
    # You could add logic here to forward this to OKX API
    return jsonify({"status": "received"}), 200