from flask import Flask, jsonify, request
import sqlite3

app = Flask(__name__)

def get_candle(symbol, timestamp):
    conn = sqlite3.connect("shared.db")
    cur = conn.cursor()
    cur.execute("""
        SELECT symbol, epoch, open, high, low, close, volume
        FROM candles
        WHERE symbol = ? AND epoch <= ?
        ORDER BY epoch DESC LIMIT 1
    """, (symbol, timestamp))
    row = cur.fetchone()
    conn.close()
    if row:
        return {
            "symbol": row[0],
            "epoch": row[1],
            "open": row[2],
            "high": row[3],
            "low": row[4],
            "close": row[5],
            "volume": row[6]
        }
    return None

@app.route("/get_candle")
def api_get_candle():
    symbol = request.args.get("paridade")
    timestamp = request.args.get("timestamp", type=int)
    if not symbol or not timestamp:
        return jsonify({"error": "Parâmetros inválidos", "success": False}), 400

    candle = get_candle(symbol, timestamp)
    if not candle:
        return jsonify({"error": "Candle não encontrado", "success": False}), 404
    return jsonify({"success": True, "candle": candle})

@app.route("/")
def home():
    return "🟢 SharedDB WebService ativo."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
