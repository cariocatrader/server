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

# Endpoint para salvar um candle (POST)
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

# Inicializa o banco
init_db()

# Exibe rota raiz
@app.route('/')
def index():
    return 'WebService de Candles ativo!', 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

