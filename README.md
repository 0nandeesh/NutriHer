# NutriHer

NutriHer is a Python-based project focused on nutrition and diet management. It provides utilities to calculate dietary needs, macronutrient distribution, and other nutrition-related logic in a modular and extensible way.

## Features

- Compute Basal Metabolic Rate (BMR)
- Generate macronutrient splits based on calorie intake
- Nutrition and diet utilities that can be extended for custom plans
- Organized, modular architecture for easy scaling and integration

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/0nandeesh/NutriHer.git
   cd NutriHer
   ```

2. (Optional) Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate   # macOS/Linux
   venv\Scripts\activate      # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Example usage inside Python:

```python
from NutriHer import nutrition

# Calculate BMR
bmr = nutrition.calculate_bmr(weight=70, height=175, age=25, gender="male")
print("BMR:", bmr)

# Get macronutrient breakdown
macros = nutrition.get_macros(calories=2500, ratio=(0.4, 0.3, 0.3))
print("Macros:", macros)
```

Run scripts directly from command line:

```bash
python -m NutriHer.<script_name> [args]
```

## Configuration

If your project uses a config file or environment variables, add them here.
Example (config.yaml):

```yaml
default_calorie_target: 2000
macro_ratios:
  protein: 0.3
  carbs: 0.4
  fat: 0.3
```

## Development

- Follow PEP 8 for code style
- Add docstrings for all public functions
- Write unit tests under a `tests/` folder
- Use `black` or `flake8` for formatting/linting

Run tests:

```bash
pytest
```
