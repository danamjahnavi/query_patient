import re
import os
import streamlit as st
import pandas as pd
import psycopg2
from dotenv import load_dotenv
import google.generativeai as genai
import bcrypt
from utils import get_db_url  # Returns DB connection URL

# Load .env only if running locally
if os.path.exists(".env"):
    load_dotenv()

# ----------------------------------------------------------------
# REQUIRED SECRETS FROM STREAMLIT CLOUD
# ----------------------------------------------------------------
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
HASHED_PASSWORD = st.secrets["HASHED_PASSWORD"].encode("utf-8")

POSTGRES_USERNAME = st.secrets["POSTGRES_USERNAME"]
POSTGRES_PASSWORD = st.secrets["POSTGRES_PASSWORD"]
POSTGRES_SERVER = st.secrets["POSTGRES_SERVER"]
POSTGRES_DATABASE = st.secrets["POSTGRES_DATABASE"]

genai.configure(api_key=GOOGLE_API_KEY)

# ----------------------------------------------------------------
# Database schema sent to Gemini
# ----------------------------------------------------------------
DATABASE_SCHEMA = """
Database Schema:

LOOKUP TABLES:
- ProductCategory(ProductCategoryID, ProductCategory, ProductCategoryDescription)

CORE TABLES:
- Region(RegionID, Region)
- Country(CountryID, Country, RegionID)
- Customer(CustomerID, FirstName, LastName, Address, City, CountryID)
- Product(ProductID, ProductName, ProductUnitPrice, ProductCategoryID)
- OrderDetail(OrderID, CustomerID, ProductID, OrderDate, QuantityOrdered)

IMPORTANT NOTES:
- Use JOINs to get descriptive values (e.g., Customer → Country → Region)
- OrderDate is DATE type
- QuantityOrdered is INTEGER
- Use aggregates like SUM, AVG, COUNT appropriately
- Add LIMIT 100 to large result queries
"""

# ----------------------------------------------------------------
# LOGIN SCREEN
# ----------------------------------------------------------------
def login_screen():
    st.title("🔐 Secure Login")
    st.write("Enter your password to access the AI SQL Query Assistant.")
    
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if bcrypt.checkpw(password.encode("utf-8"), HASHED_PASSWORD):
            st.session_state.logged_in = True
            st.success("Login successful! Redirecting...")
            st.rerun()
        else:
            st.error("Incorrect password")

    st.info("Passwords are securely protected using bcrypt hashing.")

def require_login():
    if not st.session_state.get("logged_in"):
        login_screen()
        st.stop()

# ----------------------------------------------------------------
# GET DATABASE CONNECTION
# ----------------------------------------------------------------
@st.cache_resource
def get_db_connection():
    try:
        conn = psycopg2.connect(get_db_url())
        return conn
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

def run_query(sql):
    conn = get_db_connection()
    try:
        return pd.read_sql_query(sql, conn)
    except Exception as e:
        st.error(f"❌ SQL execution error: {e}")
        return None

# ----------------------------------------------------------------
# GEMINI SQL GENERATION
# ----------------------------------------------------------------
@st.cache_resource
def get_genai_client():
    return genai.GenerativeModel("models/gemini-2.0-flash")

def extract_sql_from_response(text):
    return re.sub(r"```sql|```", "", text, flags=re.IGNORECASE).strip()

def generate_sql_with_ai(question):
    model = get_genai_client()
    prompt = f"""
Generate a valid PostgreSQL query based on this question and schema.

{DATABASE_SCHEMA}

Question: {question}

Rules:
- Only output SQL (no explanation)
- Use proper JOIN logic
- Include LIMIT 100 for large sets
- Include column aliases using AS
"""

    try:
        response = model.generate_text(prompt)
        return extract_sql_from_response(response.text)
    except Exception as e:
        st.error(f"Error calling Gemini API: {e}")
        return None

# ----------------------------------------------------------------
# MAIN APP
# ----------------------------------------------------------------
def main():
    require_login()

    st.title("🤖 AI-Powered SQL Query Assistant")
    st.markdown("Ask a natural language question — I will convert it into a SQL query!")

    user_question = st.text_input("Your question:")

    if st.button("Generate SQL") and user_question.strip():
        with st.spinner("AI is generating SQL..."):
            sql = generate_sql_with_ai(user_question)
            if sql:
                st.text_area("Generated SQL", sql, height=200)
                if st.button("Run Query"):
                    df = run_query(sql)
                    if df is not None:
                        st.success(f"Returned {len(df)} rows")
                        st.dataframe(df, use_container_width=True)

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

# Run the app
if __name__ == "__main__":
    main()
