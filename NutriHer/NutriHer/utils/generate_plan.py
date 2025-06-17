def generate_plan(goal, age):
    import pandas as pd

    def parse_macros(macros_str):
        macros = {}
        if pd.notna(macros_str):
            for part in macros_str.split(','):
                if ':' in part:
                    key, value = part.strip().split(':')
                    macros[key.strip()] = value.strip()
        return macros

    def parse_alternatives(alt_str):
        alternatives = {}
        if pd.notna(alt_str):
            for part in alt_str.split('|'):
                if ':' in part:
                    key, value = part.strip().split(':')
                    alternatives[key.strip()] = value.strip()
        return alternatives

    try:
        df = pd.read_csv("data/predefined_diet_plans.csv")

        # Normalize text
        df['goal'] = df['goal'].astype(str).str.strip().str.lower()
        df['age_range'] = df['age_range'].astype(str).str.strip()
        goal = goal.strip().lower()

        print("Looking for goal:", goal)
        print("Available goals:", df['goal'].unique())

        # Filter by goal
        goal_matches = df[df['goal'] == goal]

        if goal_matches.empty:
            print("No matching goal found in CSV.")
            return None

        # Filter by age range
        def age_in_range(row):
            try:
                start, end = map(int, row['age_range'].split('-'))
                return start <= age <= end
            except Exception as e:
                print("Error parsing age_range:", row['age_range'], "=>", e)
                return False

        match = goal_matches[goal_matches.apply(age_in_range, axis=1)]

        if match.empty:
            print(f"No age match found for goal: {goal} and age: {age}")
            return None

        row = match.iloc[0]

        return {
            'breakfast': row.get('breakfast', 'N/A'),
            'lunch': row.get('lunch', 'N/A'),
            'dinner': row.get('dinner', 'N/A'),
            'snacks': row.get('snacks', 'N/A'),
            'macros': parse_macros(row.get('macros', '')),
            'alternatives': parse_alternatives(row.get('alternatives', ''))
        }

    except Exception as e:
        print("🔥 Error reading CSV or generating plan:", e)
        return None
