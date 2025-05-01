from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

@app.route("/")
def home():
    return "WebService está online!"

@app.route("/get_candle")
def get_candle():
    paridade = request.args.get("paridade")
    timestamp = request.args.get("timestamp", type=int)

    if not paridade or not timestamp:
        return jsonify({"error": "parâmetros inválidos", "success": False})

    try:
        conn = sqlite3.connect("shared.db")
        cur = conn.cursor()
        cur.execute("""
            SELECT symbol, epoch, open, close FROM candles 
            WHERE symbol = ? AND epoch <= ?
            ORDER BY epoch DESC LIMIT 1
        """, (paridade, timestamp))
        row = cur.fetchone()
        conn.close()

        if row:
            return jsonify({
                "success": True,
                "candle": {
                    "symbol": row[0],
                    "epoch": row[1],
                    "open": row[2],
                    "close": row[3]
                }
            })
        else:
            return jsonify({"success": False, "error": "Candle não encontrado"})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
