from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)
DB_PATH = "shared.db"

# Inicializa o banco se não existir
def init_db():
    if not os.path.exists(DB_PATH):
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        cur.execute('''
        CREATE TABLE IF NOT EXISTS candles (
            symbol TEXT,
            epoch INTEGER,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume INTEGER,
            PRIMARY KEY (symbol, epoch)
        )
        ''')
        con.commit()
        con.close()

init_db()

# Página inicial
@app.route('/')
def index():
    return 'WebService de Candles ativo!', 200

# Salva um candle via POST
@app.route('/salvar_candle', methods=['POST'])
def salvar_candle():
    try:
        data = request.get_json()
        symbol = data['symbol']
        epoch = data['epoch']
        open_ = data['open']
        high = data['high']
        low = data['low']
        close = data['close']
        volume = data['volume']

        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        cur.execute('''
            INSERT OR IGNORE INTO candles (symbol, epoch, open, high, low, close, volume)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (symbol, epoch, open_, high, low, close, volume))
        con.commit()
        con.close()

        return jsonify({"success": True, "message": "Candle salvo"}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Retorna 1 candle específico para timestamp
@app.route('/get_candle', methods=['GET'])
def get_candle():
    try:
        paridade = request.args.get("paridade")
        timestamp = int(request.args.get("timestamp"))

        con = sqlite3.connect(DB_PATH)
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("""
            SELECT * FROM candles
            WHERE symbol = ? AND epoch <= ?
            ORDER BY epoch DESC
            LIMIT 1
        """, (paridade, timestamp))
        row = cur.fetchone()
        con.close()

        if row:
            return jsonify({"success": True, "candle": dict(row)})
        else:
            return jsonify({"success": False, "error": "Candle não encontrado"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Retorna lista de candles por paridade
@app.route('/candles', methods=['GET'])
def get_candles():
    try:
        symbol = request.args.get('symbol')
        limit = int(request.args.get('limit', 20))

        con = sqlite3.connect(DB_PATH)
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute('''
            SELECT * FROM candles
            WHERE symbol = ?
            ORDER BY epoch DESC
            LIMIT ?
        ''', (symbol, limit))
        rows = cur.fetchall()
        con.close()

        candles = [dict(row) for row in rows]
        return jsonify(candles), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Novo endpoint para candle exato
@app.route('/get_candle_exact', methods=['GET'])
def get_candle_exact():
    try:
        paridade = request.args.get("paridade")
        timeframe = int(request.args.get("timeframe"))
        open_time = int(request.args.get("open_time"))

        close_time = open_time + timeframe

        con = sqlite3.connect(DB_PATH)
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("""
            SELECT * FROM candles
            WHERE symbol = ? 
            AND epoch >= ? 
            AND epoch < ?
            ORDER BY epoch ASC
            LIMIT 1
        """, (paridade, open_time, close_time))
        row = cur.fetchone()
        con.close()

        if row:
            candle = dict(row)
            return jsonify({
                "success": True,
                "candle": {
                    "open": candle["open"],
                    "high": candle["high"],
                    "low": candle["low"],
                    "close": candle["close"],
                    "open_time": candle["epoch"]
                }
            })
        return jsonify({"success": False, "error": "Candle não encontrado"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
