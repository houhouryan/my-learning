import sqlite3
import pandas as pd

def make_training_data():
    conn = sqlite3.connect('stock_system.db')
    # 撈取台積電的所有歷史紀錄
    query = "SELECT * FROM intraday_ticks WHERE stock_id = '2330.TW' ORDER BY datetime ASC"
    df = pd.read_sql_query(query, conn)
    conn.close()

    if len(df) < 20:
        print("❌ 資料量不足（至少需要 20 筆），請先執行 stock_main.py 採集數據。")
        return

    # 計算特徵 (Features)
    df['returns'] = df['price'].pct_change() * 100
    df['ma5'] = df['price'].rolling(window=5).mean()
    df['gap'] = (df['price'] - df['ma5']) / df['ma5'] * 100
    
    # 計算 RSI (14)
    delta = df['price'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    df['rsi'] = 100 - (100 / (1 + (gain/loss)))

    # 標籤 (Target): 下一分鐘的價格比這一分鐘高，就標記為 1 (漲)，否則為 0
    df['target'] = (df['price'].shift(-1) > df['price']).astype(int)

    # 移除空值並存檔
    df = df.dropna()
    df.to_csv('ai_training_data.csv', index=False)
    print("✅ AI 訓練資料集已生成：ai_training_data.csv")
    print(df.tail())

if __name__ == "__main__":
    make_training_data()