import streamlit as st
import pandas as pd
import mysql.connector
import random
from faker import Faker
from datetime import datetime, timedelta

# Initialize Faker
fake = Faker()

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="My Crop Management Portal",
    page_icon="🍀",
    layout="wide"
)

# --- CUSTOM CSS FOR BACKGROUND, FONTS, ETC. ---
# Note: Using a linear gradient for a more distinctive background
custom_css = """
<style>
/* Gradient background for the main container */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #f9f9f9 25%, #f0fff0 100%);
    font-family: 'Verdana', sans-serif;
}

/* Title customization */
[data-testid="stHeader"] h1 {
    color: #4b0082; /* Indigo color for the title */
    font-weight: 800;
    font-family: 'Comic Sans MS', cursive, sans-serif; /* Something fun/different */
}

/* Tabs style */
div[class*="stTabs"] button {
    background-color: #ffe4e1;
    font-size: 1rem;
    font-weight: 600;
    color: #4b0082;
    border: 2px solid #ffd4d4;
    border-radius: 8px;
    margin-right: 8px;
    transition: background-color 0.3s, transform 0.3s;
}
div[class*="stTabs"] button:hover {
    background-color: #ffc0cb;
    color: #4b0082;
    transform: scale(1.05);
}

/* Buttons customization */
.stButton>button {
    background-color: #006400 !important; /* Dark Green */
    color: #ffffff !important;
    border-radius: 10px !important;
    font-weight: bold !important;
    padding: 0.6rem 1.2rem !important;
    font-size: 1rem !important;
    border: 2px solid #004a00 !important;
    transition: background-color 0.3s, transform 0.3s;
}
.stButton>button:hover {
    background-color: #228b22 !important; /* ForestGreen */
    transform: scale(1.05);
}

/* Form labels and headers */
label {
    font-weight: 600 !important;
    color: #333333 !important;
    font-size: 1.05rem !important;
}

/* Subheaders style */
h2, h3, h4 {
    color: #4b0082;
    font-family: 'Georgia', serif;
}

/* DataFrame styling */
[data-testid="stDataFrame"] table {
    border: 2px solid #ccc;
    border-radius: 8px;
    font-size: 0.95rem;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# --- DATABASE CONFIG ---
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Pradnya@2312",
    "database": "crop_management"
}

# --- LISTS FOR DROPDOWNS ---
crop_names = ["Wheat", "Rice", "Corn", "Soybean", "Barley", "Sugarcane", "Cotton", "Potato", "Tomato", "Lettuce"]
growth_stages = ["Seedling", "Vegetative", "Flowering", "Fruiting", "Maturity"]
pest_control_measures_list = [
    "Use of organic pesticides",
    "Crop rotation",
    "Neem oil application",
    "Biological pest control",
    "Chemical pesticides",
    "Regular field monitoring"
]

# --- DATABASE CONNECTION ---
def connect_db():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as e:
        st.error(f"Error connecting to database: {e}")
        return None

# --- INSERT MANUAL CROP RECORD ---
def insert_manual_record(crop_name, planting_date, harvest_date, growth_stage, pest_control, yield_prediction):
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO crops (crop_name, planting_date, harvest_date, growth_stage, pest_control_measures, yield_prediction)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (crop_name, planting_date, harvest_date, growth_stage, pest_control, yield_prediction)
            )
            conn.commit()
            st.success("✅ Crop record inserted successfully!")
            st.rerun()  # Live update the UI
        except mysql.connector.Error as e:
            st.error(f"⚠️ Error inserting record: {e}")
        finally:
            conn.close()

# --- GENERATE RANDOM DATA FOR BULK INSERT ---
def generate_data():
    crop_name = random.choice(crop_names)
    planting_date = fake.date_between(start_date="-2y", end_date="today")
    harvest_date = planting_date + timedelta(days=random.randint(60, 180))
    growth_stage = random.choice(growth_stages)
    pest_control = random.choice(pest_control_measures_list)
    yield_prediction = random.randint(500, 5000)
    return (crop_name, planting_date, harvest_date, growth_stage, pest_control, yield_prediction)

# --- BULK INSERT RECORDS ---
def insert_bulk_records(total_records):
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        batch_size = 10000 if total_records >= 10000 else total_records

        for i in range(0, total_records, batch_size):
            current_batch = min(batch_size, total_records - i)
            data_batch = [generate_data() for _ in range(current_batch)]
            cursor.executemany(
                """
                INSERT INTO crops (crop_name, planting_date, harvest_date, growth_stage, pest_control_measures, yield_prediction)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                data_batch
            )
            conn.commit()
            st.info(f"🛠 {i + current_batch} records inserted...")
        st.success(f"✅ {total_records} records inserted successfully!")
        conn.close()
        st.rerun()  # Refresh UI after bulk insertion

# --- FETCH CROP RECORDS ---
def get_top_10_records():
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, crop_name, planting_date, harvest_date, growth_stage, pest_control_measures, yield_prediction 
            FROM crops 
            ORDER BY id ASC
        """)
        rows = cursor.fetchall()
        conn.close()
        return rows
    return []

# --- STREAMLIT UI ---
st.title("🌻 My Crop Management Portal")

tab1, tab2 = st.tabs(["🔖 Insert Data", "📑 View Database"])

with tab1:
    st.subheader("📝 Add a New Crop Record")
    with st.form("manual_entry_form"):
        selected_crop = st.selectbox("🌱 Crop Name", crop_names)
        planting_date = st.date_input("📅 Planting Date")
        harvest_date = st.date_input("🌾 Harvest Date")
        selected_growth_stage = st.selectbox("🌿 Growth Stage", growth_stages)
        selected_pest_control = st.selectbox("🐛 Pest Control Measures", pest_control_measures_list)
        yield_prediction = st.number_input("📊 Yield Prediction (kg)", min_value=0, step=1)
        submitted = st.form_submit_button("➕ Insert Record")
        if submitted:
            insert_manual_record(
                selected_crop,
                planting_date,
                harvest_date,
                selected_growth_stage,
                selected_pest_control,
                yield_prediction
            )

    st.subheader("🚀 Bulk Insert Crop Records")
    bulk_option = st.selectbox("🔢 Select number of records to insert", options=[1000, 10000, 100000])
    if st.button("⚡ Insert Bulk Records"):
        insert_bulk_records(bulk_option)

with tab2:
    st.subheader("🔍 View Crop Records")
    records = get_top_10_records()
    if records:
        columns = ["ID", "Crop Name", "Planting Date", "Harvest Date", "Growth Stage", "Pest Control", "Yield Prediction"]
        df = pd.DataFrame(records, columns=columns)
        # Display only the top 10 records
        st.dataframe(df.drop(columns=["ID"]).head(10), use_container_width=True)
    else:
        st.warning("⚠️ No records found.")
    if st.button("🔄 Refresh Data"):
        st.rerun()
