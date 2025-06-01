import pandas as pd
import os
from sklearn.linear_model import LinearRegression

def load_model(data_path="user_feedback.csv"):
    required_columns = ["feature1", "feature2", "label", "frequency"]

    if not os.path.exists(data_path) or os.path.getsize(data_path) == 0:
        print("[Init] Writing dummy training data...")
        dummy_data = pd.DataFrame({
            "feature1": [1, 2, 3, 4],
            "feature2": [2, 1, 3, 4],
            "label": [5.0, 4.0, 6.5, 7.0],
            "frequency": [3, 2, 1, 4]
        })
        dummy_data.to_csv(data_path, index=False)

    df = pd.read_csv(data_path)

    if not all(col in df.columns for col in required_columns):
        raise ValueError("CSV file is malformed or missing required columns.")

    df = df.dropna(subset=required_columns)

    if df.shape[0] < 2:
        print("[Init] Not enough valid rows. Reinitializing dummy data...")
        dummy_data = pd.DataFrame({
            "feature1": [1, 2, 3, 4],
            "feature2": [2, 1, 3, 4],
            "label": [5.0, 4.0, 6.5, 7.0],
            "frequency": [3, 2, 1, 4]
        })
        dummy_data.to_csv(data_path, index=False)
        df = dummy_data

    df_expanded = df.loc[df.index.repeat(df['frequency'])].reset_index(drop=True)
    X = df_expanded[['feature1', 'feature2']]
    y = df_expanded['label']
    model = LinearRegression().fit(X, y)

    print(f"[✅] Model trained on {len(X)} samples from {len(df)} unique records.")
    return model

def predict(model, f1, f2):
    return float(model.predict([[f1, f2]])[0])

def retrain_model(data_path="user_feedback.csv"):
    return load_model(data_path)

def recommend_from_frequency(data_path_or_df, f1, f2, top_n=3):
    if isinstance(data_path_or_df, str):
        df = pd.read_csv(data_path_or_df)
    else:
        df = data_path_or_df

    filtered = df[(df['feature1'] == f1) & (df['feature2'] == f2)]
    top_labels = filtered.groupby('label')['frequency'].sum().sort_values(ascending=False)
    return top_labels.head(top_n).index.tolist()

