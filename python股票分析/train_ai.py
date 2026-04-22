import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib

def train_model():
    try:
        df = pd.read_csv('ai_training_data.csv')
    except:
        print("❌ 找不到 ai_training_data.csv，請先執行 make_ai_data.py")
        return

    # 選取特徵與標籤
    features = ['returns', 'gap', 'rsi']
    X = df[features]
    y = df['target']

    # 建立隨機森林模型
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)

    # 儲存模型
    joblib.dump(model, 'stock_ai.joblib')
    print("🧠 AI 模型訓練完成！已儲存為 stock_ai.joblib")
    
    # 顯示特徵重要性 (資深工程師愛看的數據)
    importance = dict(zip(features, model.feature_importances_))
    print(f"📊 特徵權重分析：{importance}")

if __name__ == "__main__":
    train_model()