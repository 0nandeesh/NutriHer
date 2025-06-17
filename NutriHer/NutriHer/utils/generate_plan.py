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

        # Normalize goal
        df['goal'] = df['goal'].astype(str).str.strip().str.lower()
        goal = goal.strip().lower()

        # Filter by goal
        match = df[df['goal'] == goal]

        # Now filter by age range
        def age_in_range(row):
            try:
                start, end = map(int, row['age_range'].split('-'))
                return start <= age <= end
            except:
                return False

        match = match[match.apply(age_in_range, axis=1)]

        if not match.empty:
            row = match.iloc[0]
            return {
                'breakfast': row.get('breakfast', 'N/A'),
                'lunch': row.get('lunch', 'N/A'),
                'dinner': row.get('dinner', 'N/A'),
                'snacks': row.get('snacks', 'N/A'),
                'macros': parse_macros(row.get('macros', '')),
                'alternatives': parse_alternatives(row.get('alternatives', ''))
            }

        return None

    except Exception as e:
        print(f"Error: {e}")
        return None
