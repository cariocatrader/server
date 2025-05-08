from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)
DB_PATH = "shared.db"

# Inicializa banco de dados com as tabelas necessárias
def init_db():
    if not os.path.exists(DB_PATH):
        open(DB_PATH, 'w').close()

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

    # Tabela de entradas realizadas
    cur.execute('''
        CREATE TABLE IF NOT EXISTS entradas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paridade TEXT,
            direcao TEXT,
            resultado TEXT,
            horario_entrada TEXT,
            horario_fechamento TEXT,
            rsi REAL,
            ema9 REAL,
            tipo_entrada TEXT,
            em_suporte_ou_resistencia INTEGER
        )
    ''')

    con.commit()
    con.close()

@app.route("/")
def index():
    return "✅ WebService de Candles e Entradas ativo!"

@app.route("/salvar_candle", methods=["POST"])
def salvar_candle():
    try:
        data = request.get_json()
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        cur.execute('''
            INSERT OR IGNORE INTO candles (symbol, epoch, open, high, low, close, volume)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            data["symbol"], data["epoch"], data["open"], data["high"],
            data["low"], data["close"], data["volume"]
        ))
        con.commit()
        con.close()
        return jsonify({"success": True, "message": "Candle salvo"}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/get_candle", methods=["GET"])
def get_candle():
    paridade = request.args.get("paridade")
    timestamp = request.args.get("timestamp")
    if not paridade or not timestamp:
        return jsonify({"success": False, "error": "Parâmetros ausentes"}), 400

    try:
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        cur.execute("SELECT * FROM candles WHERE symbol=? AND epoch=?", (paridade, int(timestamp)))
        row = cur.fetchone()
        con.close()

        if row:
            keys = ["symbol", "epoch", "open", "high", "low", "close", "volume"]
            return jsonify({"success": True, "candle": dict(zip(keys, row))}), 200
        else:
            return jsonify({"success": False, "error": "Candle não encontrado"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/get_candle_exact", methods=["GET"])
def get_candle_exact():
    paridade = request.args.get("paridade")
    timeframe = request.args.get("timeframe")
    open_time = request.args.get("open_time")

    if not paridade or not timeframe or not open_time:
        return jsonify({"success": False, "error": "Parâmetros ausentes"}), 400

    try:
        timeframe = int(timeframe)
        open_time = int(open_time)
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        cur.execute("SELECT * FROM candles WHERE symbol=? AND epoch=?", (paridade, open_time))
        row = cur.fetchone()
        con.close()

        if row:
            keys = ["symbol", "epoch", "open", "high", "low", "close", "volume"]
            return jsonify({"success": True, "candle": dict(zip(keys, row))}), 200
        else:
            return jsonify({"success": False, "error": "Candle exato não encontrado"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# 🆕 NOVO ENDPOINT: Registro de entrada da operação
@app.route("/registrar_entrada", methods=["POST"])
def registrar_entrada():
    try:
        data = request.get_json()
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        cur.execute('''
            INSERT INTO entradas (
                paridade, direcao, resultado, horario_entrada,
                horario_fechamento, rsi, ema9, tipo_entrada, em_suporte_ou_resistencia
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data["paridade"],
            data["direcao"],
            data["resultado"],
            data["horario_entrada"],
            data["horario_fechamento"],
            data.get("rsi"),
            data.get("ema9"),
            data.get("tipo_entrada"),
            int(data.get("em_suporte_ou_resistencia", False))
        ))
        con.commit()
        con.close()
        return jsonify({"success": True, "message": "Entrada registrada"}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=10000)
