import yfinance as yf
import sqlite3
import pandas as pd
from linebot import LineBotApi
from linebot.models import TextSendMessage
from datetime import datetime
import time
import joblib

# --- 設定區 ---
LINE_ACCESS_TOKEN = "4BC9QDlKA6mPj6EDYSSFpKP1ZOyDUPB8UsaYUrWDuLQy6DnARNePl2bEsrppG9JUKUDfSWgAd/EQ8hsYPRj1Q8pIFZ14e0jNCIgnw7BMRKD1Am5pmy6y/Hra2lDmK8nG3KGIaTJa1NorKCYi4g+dPAdB04t89/1O/w1cDnyilFU="
USER_ID = "U82eaa6b869fac623b46eae3524e984c4"
TARGET_STOCKS = ["2330.TW", "2317.TW", "0050.TW"]
line_bot_api = LineBotApi(LINE_ACCESS_TOKEN)

# 嘗試載入 AI 大腦
try:
    model = joblib.load('stock_ai.joblib')
    print("🧠 AI 模型載入成功！")
except:
    model = None
    print("⚠️ 找不到模型檔，僅進行數據採集。")

def job():
    conn = sqlite3.connect('stock_system.db')
    cursor = conn.cursor()
    
    # 1. 建立資料表 (確保有 prediction 欄位)
    cursor.execute('''CREATE TABLE IF NOT EXISTS intraday_ticks 
                     (stock_id TEXT, datetime TEXT, price REAL, volume INTEGER, prediction TEXT, 
                     PRIMARY KEY(stock_id, datetime))''')
    
    for stock_id in TARGET_STOCKS:
        df = yf.download(stock_id, period="1d", interval="1m", progress=False, auto_adjust=True)
        if df.empty or len(df) < 15: continue

        latest_p = float(df['Close'].iloc[-1].item())
        latest_v = int(df['Volume'].iloc[-1].item())
        latest_time = df.index[-1].strftime('%Y-%m-%d %H:%M:%S')

        # --- 新增：初始化預測狀態為 "待命中" ---
        current_pred = "待命中"

        # AI 預測邏輯 (以台積電為例)
        if stock_id == "2330.TW" and model:
            returns = (df['Close'].pct_change().iloc[-1] * 100).item()
            ma5 = df['Close'].rolling(window=5).mean().iloc[-1].item()
            gap = ((latest_p - ma5) / ma5 * 100)
            
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean().iloc[-1].item()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean().iloc[-1].item()
            rsi = 100 - (100 / (1 + (gain/loss)))

            input_data = pd.DataFrame([[returns, gap, rsi]], columns=['returns', 'gap', 'rsi'])
            pred = model.predict(input_data)[0]
            
            # --- 更新：將預測結果存入變數 ---
            current_pred = "📈 看漲" if pred == 1 else "📉 看跌"
            
            msg = f"【AI 監控】{stock_id}\n價格：{latest_p}\n預測：{current_pred}"
            line_bot_api.push_message(USER_ID, TextSendMessage(text=msg))

        # 2. 修改重點：將 current_pred 塞進資料庫 (補上第 5 個問號)
        cursor.execute("INSERT OR REPLACE INTO intraday_ticks VALUES (?, ?, ?, ?, ?)", 
                       (stock_id, latest_time, latest_p, latest_v, current_pred))

    conn.commit()
    conn.close()
    print(f"✅ 數據已存入資料庫：{datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    while True:
        now = datetime.now()
        if True:
        #if now.weekday() < 5 and (9 <= now.hour < 14):
            job()
            time.sleep(60)
        else:
            print(f"💤 非交易時間 ({now.strftime('%H:%M')})，待命中...")
            time.sleep(600)