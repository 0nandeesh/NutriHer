import streamlit as st
from utils.generate_plan import generate_plan

# --- Dummy user credentials (plaintext for testing/demo) ---
users = {
    "nandeesh": "test123",
    "gayatri": "test456",
    "roopa": "test789"
}

# --- Login screen ---
def login():
    st.title("🔐 NutriHer Login")
    st.markdown("Please log in to access your personalized diet plan.")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username in users and users[username] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success("✅ Login successful")
            st.rerun()  # ✅ Updated for latest Streamlit version
        else:
            st.error("❌ Invalid username or password")

# --- Initialize login state ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# --- If not logged in, show login page ---
if not st.session_state.logged_in:
    login()

# --- Main NutriHer app after login ---
else:
    st.set_page_config(page_title="NutriHer", layout="centered")

    st.sidebar.title("🌿 NutriHer")
    st.sidebar.success(f"Welcome, {st.session_state.username}")
    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.rerun()

    st.title("🌿 NutriHer – Personalized Nutrition for Women 35+")
    st.markdown("#### Get a full-day diet plan tailored to your health goals, preferences, and lifestyle.")

    # --- Sidebar Inputs ---
    st.sidebar.header("👤 About You")
    age = st.sidebar.slider("🎂 Age", 35, 55, 42)
    weight = st.sidebar.number_input("⚖️ Weight (in kg)", min_value=40, max_value=120, value=60)
    activity = st.sidebar.selectbox("🏃‍♀️ Activity Level", ["Sedentary", "Lightly Active", "Active"])
    diet_pref = st.sidebar.radio("🥗 Dietary Preference", ["Vegetarian", "Non-Vegetarian"])
    health_goals = st.sidebar.multiselect("🎯 Health Goals", [
        "Hormonal Balance", "Weight Loss", "Iron Deficiency",
        "Digestive Health", "Energy Boosting", "Bone Health"
    ])

    # --- Generate Diet Plan ---
    if st.button("🍽️ Get My Diet Plan"):
        if not health_goals:
            st.warning("⚠️ Please select at least one health goal.")
        else:
            for goal in health_goals:
                st.subheader(f"✅ Diet Plan for {goal}")
                plan = generate_plan(goal, age)
                if plan:
                    st.markdown("### 🥗 Full-Day Meal Plan")
                    st.markdown(f"- **🥣 Breakfast:** {plan['breakfast']}")
                    st.markdown(f"- **🍛 Lunch:** {plan['lunch']}")
                    st.markdown(f"- **🍲 Dinner:** {plan['dinner']}")
                    st.markdown(f"- **🍎 Snacks:** {plan['snacks']}")

                    st.markdown("### 🧪 Macronutrient Breakdown")
                    col1, col2, col3 = st.columns(3)
                    col1.metric("💪 Protein", plan['macros'].get("Protein", "N/A"))
                    col2.metric("🍚 Carbs", plan['macros'].get("Carbs", "N/A"))
                    col3.metric("🧈 Fat", plan['macros'].get("Fat", "N/A"))

                    st.markdown("### 🔁 Suggested Alternatives")
                    alt1, alt2, alt3 = st.columns(3)
                    alt1.markdown(f"**🍳 Breakfast:** {plan['alternatives'].get('Breakfast', '-')}")
                    alt2.markdown(f"**🥘 Lunch:** {plan['alternatives'].get('Lunch', '-')}")
                    alt3.markdown(f"**🌙 Dinner:** {plan['alternatives'].get('Dinner', '-')}")
                    st.markdown("---")
                else:
                    st.error(f"❌ No plan found for goal: '{goal}' and your age: {age}.")

    # --- Community Section ---
    with st.expander("💬 Community Forum"):
        st.write("Share your tips, recipes, or wellness experience:")
        post = st.text_area("✍️ Your message")
        if st.button("📨 Post"):
            st.success("✅ Thanks for sharing! (Simulated post saved)")
