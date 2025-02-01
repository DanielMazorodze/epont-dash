import streamlit as st
import pandas as pd
import json


st.set_page_config(
    page_title="Quantilytix-Epont ESD Programme",
    layout="wide",
    initial_sidebar_state="expanded"
)


# --- User Authentication ---
users = {"info@epont.co.za": {"password": "admin123"}, "user": {"password": "user123"}}

def authenticate(username, password):
    return users.get(username, {}).get("password") == password

# Session State for Login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("Welcome! Login To Continue")
    username = st.text_input("Email", placeholder="Enter email")
    password = st.text_input("Password", placeholder="Enter password", type="password")
    login_button = st.button("Login")

    if login_button:
        if authenticate(username, password):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success(f"Welcome {username}!")
            st.rerun()
        else:
            st.error("Invalid username or password")
    st.stop()

# --- Load Dataset ---
file_path = "Intervention_Database.xlsx"
xls = pd.ExcelFile(file_path)
df = xls.parse('Sheet1')

# --- Streamlit UI ---
st.title("Quantilytix-Epont ESD Programme")

# --- Sidebar Filters with Logo ---
col1, col2, col3 = st.sidebar.columns([3,3, 5])
with col1:
    st.image("logo.png", width=500)  # Replace with your actual logo file
with col2:
    st.image("epnt.png", width=500)  # Replace with your actual logo file
with col3:
    st.sidebar.header("Filters")

# --- Sidebar Filters ---
companies = ["All"] + df["Company Name"].unique().tolist()
categories = ["All"] + df["Intervention_Category"].unique().tolist()
genders = ["All"] + df["Gender"].unique().tolist()
youth_options = ["All"] + df["Youth"].unique().tolist()

selected_company = st.sidebar.multiselect("Select Company", companies, default=["All"])
selected_category = st.sidebar.multiselect("Select Category", categories, default=["All"])
selected_gender = st.sidebar.multiselect("Select Gender", genders, default=["All"])
selected_youth = st.sidebar.radio("Show Youth", youth_options, index=0, horizontal=True)

# --- Logout Button ---
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()

# --- Apply Filters ---
filtered_df = df.copy()

if "All" not in selected_company:
    filtered_df = filtered_df[filtered_df["Company Name"].isin(selected_company)]

if "All" not in selected_category:
    filtered_df = filtered_df[filtered_df["Intervention_Category"].isin(selected_category)]

if "All" not in selected_gender:
    filtered_df = filtered_df[filtered_df["Gender"].isin(selected_gender)]

if selected_youth != "All":
    filtered_df = filtered_df[filtered_df["Youth"] == selected_youth]

# --- Collapsible Filtered Data Table ---
with st.expander("📊 View Filtered Data", expanded=False):
    st.dataframe(filtered_df)

# --- Highcharts Visualization ---
st.write("### 📈 Interventions by Category")

category_counts = filtered_df["Intervention_Category"].value_counts().reset_index()
category_counts.columns = ["Intervention_Category", "Count"]

# Convert data to Highcharts format
chart_data = [{"name": row["Intervention_Category"], "y": row["Count"]} for _, row in category_counts.iterrows()]

# Highcharts JSON config
highcharts_config = {
    "chart": {"type": "column"},
    "title": {"text": "Interventions per Category"},
    "xAxis": {"type": "category"},
    "yAxis": {"title": {"text": "Number of Interventions"}},
    "series": [{"name": "Categories", "data": chart_data}],
}

# Render Highcharts
st.components.v1.html(f"""
    <script src="https://code.highcharts.com/highcharts.js"></script>
    <div id="container"></div>
    <script>
    Highcharts.chart('container', {json.dumps(highcharts_config)});
    </script>
""", height=400)
