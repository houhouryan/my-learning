from flask import Flask, render_template, jsonify
import sqlite3
import pandas as pd
import os

app = Flask(__name__)

# 確保路徑正確，直接讀取同資料夾的資料庫
DB_PATH = os.path.join(os.path.dirname(__file__), 'stock_system.db')

def get_db_data():
    if not os.path.exists(DB_PATH):
        return []
    conn = sqlite3.connect(DB_PATH)
    # 我們撈取最近 20 筆資料
    query = "SELECT * FROM intraday_ticks ORDER BY datetime DESC LIMIT 20"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df.to_dict(orient='records')

@app.route('/')
def index():
    return render_template('HTML1.html')

# --- app.py 修正部分 ---
@app.route('/api/data')
def api_data():
    conn = sqlite3.connect('stock_system.db')
    # 確保 SQL 撈取的資料包含所有欄位
    query = "SELECT * FROM intraday_ticks ORDER BY datetime DESC LIMIT 20"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return jsonify(df.to_dict(orient='records'))

if __name__ == '__main__':
    print("🚀 戰情室後端已啟動：http://127.0.0.1:5000")
    app.run(debug=True, port=5000)