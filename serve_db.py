from flask import Flask, request, jsonify
import sqlite3
import os

# Inicializa o Flask
app = Flask(__name__)
DB_PATH = "shared.db"

# Cria o banco de dados se não existir
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

# Inicializa o banco ao iniciar o app
init_db()

# Endpoint raiz
@app.route('/')
def index():
    return 'WebService de Candles ativo!', 200

# Endpoint para salvar candle
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

# Endpoint para consultar candle
@app.route('/get_candle', methods=['GET'])
def get_candle():
    paridade = request.args.get('paridade')
    timestamp = request.args.get('timestamp')

    if not paridade or not timestamp:
        return jsonify({"success": False, "error": "Parâmetros ausentes"}), 400

    try:
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        cur.execute("""
            SELECT symbol, epoch, open, high, low, close, volume
            FROM candles
            WHERE symbol = ?
            AND epoch = ?
        """, (paridade, int(timestamp)))
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
                "volume": row[6]
            }
            return jsonify({"success": True, "candle": candle}), 200
        else:
            return jsonify({"success": False, "error": "Candle não encontrado"}), 404

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Inicia o Flask quando chamado diretamente
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
