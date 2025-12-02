import re
import os
import streamlit as st
import pandas as pd
import psycopg2
from dotenv import load_dotenv
import google.generativeai as genai
import bcrypt
from utils import get_db_url

# Load .env when local
if os.path.exists(".env"):
    load_dotenv()

# Secrets (Cloud Only)
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
HASHED_PASSWORD = st.secrets["HASHED_PASSWORD"].encode("utf-8")

POSTGRES_USERNAME = st.secrets["POSTGRES_USERNAME"]
POSTGRES_PASSWORD = st.secrets["POSTGRES_PASSWORD"]
POSTGRES_SERVER = st.secrets["POSTGRES_SERVER"]
POSTGRES_DATABASE = st.secrets["POSTGRES_DATABASE"]

genai.configure(api_key=GOOGLE_API_KEY)

# Database Schema for AI prompt
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
"""

# ========================= LOGIN =========================
def login_screen():
    st.title("🔐 Secure Login")
    password = st.text_input("Enter password", type="password")

    if st.button("Login"):
        if bcrypt.checkpw(password.encode(), HASHED_PASSWORD):
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("❌ Incorrect password")

def require_login():
    if not st.session_state.get("logged_in"):
        login_screen()
        st.stop()

# ===================== DB CONNECTION =====================
@st.cache_resource
def get_db_connection():
    try:
        conn = psycopg2.connect(get_db_url())
        return conn
    except Exception as e:
        st.error(f"Database error: {e}")
        return None

def run_query(sql):
    conn = get_db_connection()
    try:
        return pd.read_sql_query(sql, conn)
    except Exception as e:
        st.error(f"Error executing query: {e}")
        return None

# ===================== Gemini Processing ==================
@st.cache_resource
def get_genai_client():
    return genai.GenerativeModel("models/gemini-2.0-flash")

def extract_sql(response):
    return re.sub(r"```sql|```", "", response, flags=re.IGNORECASE).strip()

def generate_sql(question):
    prompt = f"""
Generate SQL only. Schema:
{DATABASE_SCHEMA}
Question: {question}
Rules:
- Use JOINs
- No explanation
- LIMIT 100 if many rows
"""

    model = get_genai_client()
    response = model.generate_text(prompt)
    return extract_sql(response.text)

# ======================= Main UI ==========================
def main():
    require_login()

    st.sidebar.title("💡 Example Questions")
    st.sidebar.markdown("""
- How many customers by city?
- Total sales by product category?
- Top 10 products by quantity?
- Average order quantity?

---
    """)
    
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    st.title("🤖 AI-Powered SQL Query Assistant")
    st.markdown("Ask your data anything. I will write SQL for you!")

    if "history" not in st.session_state:
        st.session_state.history = []

    question = st.text_area("Your Question:")

    if st.button("Generate SQL"):
        if question.strip():
            with st.spinner("Thinking..."):
                sql = generate_sql(question)
                st.session_state.generated_sql = sql
                st.session_state.history.append({"q": question, "sql": sql})

    if "generated_sql" in st.session_state:
        st.subheader("Generated SQL")
        updated_sql = st.text_area("Edit Query:", st.session_state.generated_sql)

        if st.button("Run Query"):
            df = run_query(updated_sql)
            if df is not None:
                st.success(f"Rows returned: {len(df)}")
                st.dataframe(df, use_container_width=True)

    if st.session_state.history:
        st.subheader("📜 Query History")
        for item in reversed(st.session_state.history[-5:]):
            with st.expander(item["q"]):
                st.code(item["sql"], language="sql")

if __name__ == "__main__":
    main()
