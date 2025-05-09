from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)
DB_PATH = "shared.db"

# Inicializa o banco de dados se não existir
def init_db():
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

    # Tabela de entradas (aprendizado da IA)
    cur.execute('''
    CREATE TABLE IF NOT EXISTS entradas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        paridade TEXT,
        tempo INTEGER,
        direcao TEXT,
        resultado TEXT,
        entrada REAL,
        fechamento REAL,
        timestamp_entrada INTEGER,
        timestamp_fechamento INTEGER,
        confluencias TEXT
    )
    ''')

    con.commit()
    con.close()

init_db()

@app.route('/')
def index():
    return '✅ WebService da Carioca IA ativo!', 200

# 🔹 Salvar candle enviado pelo listener
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
            INSERT OR REPLACE INTO candles (symbol, epoch, open, high, low, close, volume)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (symbol, epoch, open_, high, low, close, volume))
        con.commit()
        con.close()
        return jsonify({"success": True, "message": "Candle salvo com sucesso"}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# 🔹 Retornar candles para análise/gráfico
@app.route('/candles', methods=['GET'])
def get_candles():
    symbol = request.args.get("symbol")
    limit = int(request.args.get("limit", 30))
    timeframe = int(request.args.get("timeframe", 60))

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute('''
        SELECT * FROM candles WHERE symbol = ? ORDER BY epoch DESC LIMIT ?
    ''', (symbol, limit * timeframe // 60))  # Corrigido para cobrir o tempo necessário
    rows = cur.fetchall()
    con.close()

    if not rows:
        return jsonify([]), 404

    candles = [{
        "symbol": r[0],
        "timestamp": r[1],
        "open": r[2],
        "high": r[3],
        "low": r[4],
        "close": r[5],
        "volume": r[6]
    } for r in sorted(rows, key=lambda x: x[1])]

    return jsonify(candles), 200

# 🔹 Retornar candle exato para verificar resultado
@app.route('/get_candle_exact', methods=['GET'])
def get_candle_exact():
    paridade = request.args.get("paridade")
    timeframe = int(request.args.get("timeframe"))
    open_time = int(request.args.get("open_time"))

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute('''
        SELECT * FROM candles
        WHERE symbol = ? AND epoch = ?
    ''', (paridade, open_time))
    row = cur.fetchone()
    con.close()

    if not row:
        return jsonify({"success": False, "error": "Candle não encontrado"}), 404

    candle = {
        "symbol": row[0],
        "timestamp": row[1],
        "open": row[2],
        "high": row[3],
        "low": row[4],
        "close": row[5],
        "volume": row[6]
    }

    return jsonify({"success": True, "candle": candle}), 200

# 🔹 Registrar entrada da IA para aprendizado
@app.route('/registrar_entrada', methods=['POST'])
def registrar_entrada():
    try:
        data = request.get_json()
        paridade = data["paridade"]
        tempo = data["tempo"]
        direcao = data["direcao"]
        resultado = data["resultado"]
        entrada = data["entrada"]
        fechamento = data["fechamento"]
        timestamp_entrada = data["timestamp_entrada"]
        timestamp_fechamento = data["timestamp_fechamento"]
        confluencias = data.get("confluencias", "")

        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        cur.execute('''
            INSERT INTO entradas (paridade, tempo, direcao, resultado, entrada, fechamento, timestamp_entrada, timestamp_fechamento, confluencias)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            paridade, tempo, direcao, resultado,
            entrada, fechamento,
            timestamp_entrada, timestamp_fechamento,
            confluencias
        ))
        con.commit()
        con.close()
        return jsonify({"success": True, "message": "Entrada registrada"}), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# 🔹 Rodar o servidor
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
