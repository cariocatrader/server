from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

DB_PATH = "shared.db"

@app.route("/")
def home():
    return "WebService está online!"

@app.route("/get_candle")
def get_candle():
    paridade = request.args.get("paridade")
    timestamp = request.args.get("timestamp", type=int)

    if not paridade or not timestamp:
        return jsonify({"error": "Parâmetros ausentes", "success": False})

    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""
            SELECT symbol, epoch, open, high, low, close, volume
            FROM candles
            WHERE symbol = ?
            AND epoch <= ?
            ORDER BY epoch DESC
            LIMIT 1
        """, (paridade, timestamp))
        row = cur.fetchone()
        conn.close()

        if row:
            keys = ["symbol", "epoch", "open", "high", "low", "close", "volume"]
            candle = dict(zip(keys, row))
            return jsonify({"success": True, "candle": candle})
        else:
            return jsonify({"success": False, "error": "Candle não encontrado"})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


