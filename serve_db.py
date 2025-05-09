from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)
DB_PATH = "shared.db"

# Inicializa a base de dados se não existir
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
        cur.execute('''
            CREATE TABLE IF NOT EXISTS entradas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                paridade TEXT,
                direcao TEXT,
                tempo INTEGER,
                resultado TEXT,
                taxa_abertura REAL,
                taxa_fechamento REAL,
                horario_entrada TEXT,
                horario_fechamento TEXT,
                confluencias TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        con.commit()
        con.close()

@app.route('/')
def home():
    return "WebService de Candles e Entradas ativo!", 200

@app.route('/salvar_candle', methods=['POST'])
def salvar_candle():
    try:
        data = request.get_json()
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        cur.execute('''
            INSERT OR IGNORE INTO candles (symbol, epoch, open, high, low, close, volume)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (data['symbol'], data['epoch'], data['open'], data['high'], data['low'], data['close'], data['volume']))
        con.commit()
        con.close()
        return jsonify({"success": True, "message": "Candle salvo"}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/candles')
def get_candles():
    symbol = request.args.get('symbol')
    limit = int(request.args.get('limit', 50))
    timeframe = int(request.args.get('timeframe', 60))

    try:
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        cur.execute('''
            SELECT epoch, open, high, low, close FROM candles
            WHERE symbol = ?
            ORDER BY epoch DESC
            LIMIT ?
        ''', (symbol, limit))
        rows = cur.fetchall()
        con.close()

        candles = []
        for r in reversed(rows):
            candles.append({
                "timestamp": r[0],
                "open": r[1],
                "high": r[2],
                "low": r[3],
                "close": r[4]
            })

        return jsonify(candles), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_candle_exact')
def get_candle_exact():
    symbol = request.args.get('paridade')
    open_time = int(request.args.get('open_time'))
    timeframe = int(request.args.get('timeframe', 60))
    close_time = open_time + timeframe

    try:
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        cur.execute('''
            SELECT open, close FROM candles
            WHERE symbol = ? AND epoch = ?
        ''', (symbol, open_time))
        row = cur.fetchone()
        con.close()

        if not row:
            return jsonify({"success": False, "error": "Candle não encontrado"}), 404

        return jsonify({
            "success": True,
            "candle": {
                "open": row[0],
                "close": row[1]
            }
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/registrar_entrada', methods=['POST'])
def registrar_entrada():
    try:
        data = request.get_json()
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        cur.execute('''
            INSERT INTO entradas (
                paridade, direcao, tempo, resultado,
                taxa_abertura, taxa_fechamento,
                horario_entrada, horario_fechamento,
                confluencias
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['paridade'], data['direcao'], data['tempo'],
            data['resultado'], data['taxa_abertura'], data['taxa_fechamento'],
            data['horario_entrada'], data['horario_fechamento'],
            data.get('confluencias', '')
        ))
        con.commit()
        con.close()
        return jsonify({"success": True, "message": "Entrada registrada"}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Inicializa banco ao iniciar app
init_db()

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
