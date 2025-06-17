def recommend_plan(df, age, lifestyle, concern):
    age_group = "35-45" if age < 45 else "45-55"
    match = df[
        (df['age_range'] == age_group) &
        (df['lifestyle'].str.lower() == lifestyle.lower()) &
        (df['health_concern'].str.lower() == concern.lower())
    ]
    return match.iloc[0] if not match.empty else None
