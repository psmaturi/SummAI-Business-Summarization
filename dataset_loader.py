import pandas as pd

def load_dataset():
    try:
        df = pd.read_csv("dataset/train.csv")
        return df
    except Exception as e:
        print("Dataset loading error:", e)
        return None
