from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)
DB_PATH = "shared.db"

# Cria o banco e tabelas, se necessário
def init_db():
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
            symbol TEXT,
            tempo INTEGER,
            direcao TEXT,
            resultado TEXT,
            open_time INTEGER,
            close_time INTEGER,
            open REAL,
            close REAL
        )
    ''')
    con.commit()
    con.close()

init_db()

@app.route('/')
def home():
    return 'WebService de Candles ativo!'

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
            data['symbol'], data['epoch'], data['open'],
            data['high'], data['low'], data['close'], data['volume']
        ))
        con.commit()
        con.close()
        return jsonify({"success": True, "message": "Candle salvo"}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/candles', methods=['GET'])
def candles():
    try:
        symbol = request.args.get("symbol")
        limit = int(request.args.get("limit"))
        timeframe = int(request.args.get("timeframe"))

        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        cur.execute('''
            SELECT * FROM candles
            WHERE symbol = ?
            ORDER BY epoch DESC
            LIMIT ?
        ''', (symbol, limit))
        rows = cur.fetchall()
        con.close()

        candles = []
        for row in reversed(rows):
            candles.append({
                "symbol": row[0],
                "epoch": row[1],
                "open": row[2],
                "high": row[3],
                "low": row[4],
                "close": row[5],
                "volume": row[6],
                "timestamp": row[1]
            })
        return jsonify(candles), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_candle_exact', methods=['GET'])
def get_candle_exact():
    try:
        symbol = request.args.get("paridade")
        timeframe = int(request.args.get("timeframe"))
        open_time = int(request.args.get("open_time"))

        close_time = open_time + timeframe

        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        cur.execute('''
            SELECT * FROM candles
            WHERE symbol = ? AND epoch = ?
        ''', (symbol, open_time))
        row = cur.fetchone()
        con.close()

        if row:
            candle = {
                "symbol": row[0],
                "epoch": row[1],
                "open": row[2],
                "high": row[3],
                "low": row[4],
                "close": row[5],
                "volume": row[6],
                "timestamp": row[1]
            }
            return jsonify({"success": True, "candle": candle}), 200
        else:
            return jsonify({"success": False, "error": "Candle não encontrado"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/registrar_entrada', methods=['POST'])
def registrar_entrada():
    try:
        data = request.get_json()
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        cur.execute('''
            INSERT INTO entradas (symbol, tempo, direcao, resultado, open_time, close_time, open, close)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['symbol'], data['tempo'], data['direcao'], data['resultado'],
            data['open_time'], data['close_time'], data['open'], data['close']
        ))
        con.commit()
        con.close()
        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
