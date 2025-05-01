from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

@app.route("/get_candle")
def get_candle():
    paridade = request.args.get("paridade")
    timestamp = int(request.args.get("timestamp"))
    
    try:
        con = sqlite3.connect("shared.db")
        cur = con.cursor()
        cur.execute("""
            SELECT symbol, epoch, open, close
            FROM candles
            WHERE symbol = ? AND epoch <= ?
            ORDER BY epoch DESC
            LIMIT 1
        """, (paridade, timestamp))
        row = cur.fetchone()
        con.close()

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
            return jsonify({"success": False, "error": "Candle não encontrado"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
