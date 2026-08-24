from flask import Flask, jsonify
import threading, time, json, os, requests
from datetime import datetime
app = Flask(__name__)
BALANCE_FILE = "balance.json"
START_BALANCE = 15.0003
def load_balance():
    if os.path.exists(BALANCE_FILE):
        try:
            with open(BALANCE_FILE) as f:
                return json.load(f)
        except:
            pass
    return {"balance": START_BALANCE, "profit": 0.0003, "trades": 17, "last_price": {}}
balance_data = load_balance()
COINS = ["bitcoin", "ethereum", "solana", "dogecoin", "cardano"]
def bot_loop():
    global balance_data
    while True:
        try:
            url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana,dogecoin,cardano&vs_currencies=usd"
            r = requests.get(url, timeout=10).json()
            for coin in COINS:
                price = r[coin]["usd"]
                last = balance_data.get("last_price", {}).get(coin, price)
                if price < last * 0.998:
                    balance_data["last_price"][coin] = price
                if price > last * 1.001:
                    profit = balance_data["balance"] * 0.001
                    balance_data["balance"] += profit
                    balance_data["profit"] += profit
                    balance_data["trades"] += 1
                    balance_data["last_price"][coin] = price
                    with open(BALANCE_FILE, "w") as f:
                        json.dump(balance_data, f)
            time.sleep(10)
        except:
            time.sleep(10)
@app.route("/")
def home():
    return f"<h1>JAIX LIVE</h1><p>Balance: ${balance_data['balance']:.4f}</p><p>Profit: ${balance_data['profit']:.5f}</p><p>Trades: {balance_data['trades']}</p><p>{datetime.now()}</p>"
@app.route("/ping")
def ping():
    return "pong"
@app.route("/balance")
def bal():
    return jsonify(balance_data)
threading.Thread(target=bot_loop, daemon=True).start()
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
