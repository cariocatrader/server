from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)
DB_PATH = "shared.db"

# Criação da tabela, se não existir
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

@app.route('/')
def index():
    return "WebService de candles ativo!", 200

@app.route('/salvar_candle', methods=['POST'])
def salvar_candle():
    try:
        data = request.get_json()
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        cur.execute('''
            INSERT OR IGNORE INTO candles (symbol, epoch, open, high, low, close, volume)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['symbol'],
            data['epoch'],
            data['open'],
            data['high'],
            data['low'],
            data['close'],
            data['volume']
        ))
        con.commit()
        con.close()
        return jsonify({"success": True, "message": "Candle salvo"}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/candles', methods=['GET'])
def get_candles():
    symbol = request.args.get("symbol")
    timeframe = int(request.args.get("timeframe", 60))
    limit = int(request.args.get("limit", 30))
    try:
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
        candles = [dict(row) for row in reversed(rows)]
        return jsonify(candles)
    except Exception as e:
        return jsonify([])

@app.route('/get_candle', methods=['GET'])
def get_candle():
    paridade = request.args.get("paridade")
    timestamp = int(request.args.get("timestamp"))
    try:
        con = sqlite3.connect(DB_PATH)
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute('''
            SELECT * FROM candles
            WHERE symbol = ? AND epoch = ?
        ''', (paridade, timestamp))
        row = cur.fetchone()
        con.close()
        if row:
            return jsonify({"success": True, "candle": dict(row)})
        return jsonify({"success": False, "error": "Candle não encontrado"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/get_candle_exact', methods=['GET'])
def get_candle_exact():
    paridade = request.args.get("paridade")
    timeframe = int(request.args.get("timeframe"))  # em segundos
    open_time = int(request.args.get("open_time"))

    try:
        con = sqlite3.connect(DB_PATH)
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("""
            SELECT * FROM candles
            WHERE symbol = ? AND epoch = ?
            LIMIT 1
        """, (paridade, open_time))
        row = cur.fetchone()
        con.close()

        if row:
            return jsonify({"success": True, "candle": dict(row)})
        return jsonify({"success": False, "error": "Candle não encontrado para o horário solicitado"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# Inicializa o banco
init_db()

# Executa localmente (caso precise testar fora do Render)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
