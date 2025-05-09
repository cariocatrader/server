from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)
DB_PATH = "shared.db"

def init_db():
    if not os.path.exists(DB_PATH):
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()

        # Tabela de candles
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

        # Tabela de entradas
        cur.execute('''
        CREATE TABLE IF NOT EXISTS entradas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paridade TEXT,
            tempo INTEGER,
            direcao TEXT,
            timestamp_entrada INTEGER,
            timestamp_fechamento INTEGER,
            open_price REAL,
            close_price REAL,
            resultado TEXT
        )
        ''')

        con.commit()
        con.close()

@app.route("/")
def index():
    return "WebService de Candles e Entradas ativo!", 200

@app.route("/salvar_candle", methods=["POST"])
def salvar_candle():
    try:
        data = request.get_json()
        symbol = data["symbol"]
        epoch = data["epoch"]
        open_ = data["open"]
        high = data["high"]
        low = data["low"]
        close = data["close"]
        volume = data["volume"]

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

@app.route("/get_candle", methods=["GET"])
def get_candle():
    try:
        paridade = request.args.get("paridade")
        timestamp = int(request.args.get("timestamp"))

        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        cur.execute('''
            SELECT open, high, low, close, volume
            FROM candles
            WHERE symbol = ? AND epoch = ?
        ''', (paridade, timestamp))
        row = cur.fetchone()
        con.close()

        if row:
            open_, high, low, close, volume = row
            return jsonify({
                "success": True,
                "candle": {
                    "symbol": paridade,
                    "epoch": timestamp,
                    "open": open_,
                    "high": high,
                    "low": low,
                    "close": close,
                    "volume": volume
                }
            }), 200
        else:
            return jsonify({"success": False, "error": "Candle não encontrado"}), 404

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/registrar_entrada", methods=["POST"])
def registrar_entrada():
    try:
        data = request.get_json()
        paridade = data["paridade"]
        tempo = data["tempo"]
        direcao = data["direcao"]
        timestamp_entrada = data["timestamp_entrada"]
        timestamp_fechamento = data["timestamp_fechamento"]
        open_price = data["open_price"]
        close_price = data["close_price"]
        resultado = data["resultado"]

        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        cur.execute('''
            INSERT INTO entradas (
                paridade, tempo, direcao,
                timestamp_entrada, timestamp_fechamento,
                open_price, close_price, resultado
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            paridade, tempo, direcao,
            timestamp_entrada, timestamp_fechamento,
            open_price, close_price, resultado
        ))
        con.commit()
        con.close()

        return jsonify({"success": True, "message": "Entrada registrada"}), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=10000)
