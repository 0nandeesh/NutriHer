import pandas as pd

def load_diet_data():
    return pd.read_csv('data/diet_plans.csv')

def load_ayurveda_data():
    return pd.read_csv('data/ayurveda_tips.csv')

def load_predefined_diet_plans():
    df = pd.read_csv('data/predefined_diet_plans.csv')  # fixed filename
    df['goal'] = df['goal'].str.strip().str.lower()     # normalize goals
    return df
