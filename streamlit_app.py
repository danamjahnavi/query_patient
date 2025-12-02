import re
import streamlit as st
import pandas as pd
import psycopg2
import bcrypt
import google.generativeai as genai
from dotenv import load_dotenv
from utils import get_db_url


# Load environment variables
load_dotenv()

# Secrets
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
HASHED_PASSWORD = st.secrets["HASHED_PASSWORD"].encode("utf-8")


# Database schema for Gemini Context
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

Rules:
- Always use JOINs to fetch descriptive values
- DATE format: YYYY-MM-DD
- Use LIMIT 100 if query returns many rows
"""


# ---------------------- LOGIN SYSTEM ----------------------
def login_screen():
    st.title("🔐 Secure Login")
    st.markdown("---")

    password = st.text_input("Password:", type="password")

    if st.button("Login"):
        if bcrypt.checkpw(password.encode("utf-8"), HASHED_PASSWORD):
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Incorrect password")

    st.markdown("---")
    st.info("🔒 Your access is protected with secure hashing")


def require_login():
    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        login_screen()
        st.stop()


# ---------------------- DATABASE CONNECTION ----------------------
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
    if conn:
        try:
            return pd.read_sql_query(sql, conn)
        except Exception as e:
            st.error(f"SQL Error: {e}")
    return None


# ---------------------- GEMINI SQL GENERATION ----------------------
@st.cache_resource
def gemini_model():
    genai.configure(api_key=GOOGLE_API_KEY)
    return genai.GenerativeModel("gemini-1.5-flash")


def generate_sql(question):
    model = get_genai_client()
    prompt = f"""
    You are a PostgreSQL expert. Convert the user question into a valid SQL query.
    Only return SQL — no explanations.

    Database Schema:
    {DATABASE_SCHEMA}

    User Question: {question}
    """

    try:
        response = model.generate_content(prompt)
        sql_text = response.text
        sql = extract_sql_from_response(sql_text)
        return sql
    except Exception as e:
        st.error(f"Gemini API Error: {e}")
        return None



# ---------------------- MAIN UI ----------------------
def main():
    require_login()
    
    st.title("🤖 AI-Powered SQL Query Assistant")
    st.markdown("Ask your data anything — I will write SQL for you!")
    st.markdown("---")

    # Sidebar
    st.sidebar.header("💡 Example Questions")
    st.sidebar.markdown("""
- How many customers by city?
- Total sales by category?
- Top 10 products by quantity?
- Average quantity ordered?
    """)

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    # Session State Setup
    if 'generated_sql' not in st.session_state:
        st.session_state.generated_sql = None

    if 'query_history' not in st.session_state:
        st.session_state.query_history = []

    # Main Input
    question = st.text_area("Your Question:")

    if st.button("Generate SQL"):
        if question.strip():
            sql_query = generate_sql(question)
            if sql_query:
                st.session_state.generated_sql = sql_query
                st.session_state.query_history.append(question)
        else:
            st.warning("Please enter a valid question")

    # Show SQL + Execution Button
    if st.session_state.generated_sql:
        st.subheader("Generated SQL Query")
        edited_sql = st.text_area("Edit SQL if needed:", 
                                  value=st.session_state.generated_sql, height=200)

        if st.button("Run Query"):
            df = run_query(edited_sql)
            if df is not None:
                st.success(f"Query returned {len(df)} rows")
                st.dataframe(df, use_container_width=True)

    # Query history section
    if st.session_state.query_history:
        st.markdown("---")
        st.subheader("🕘 Query History")
        for q in reversed(st.session_state.query_history[-5:]):
            st.write(f"• {q}")


if __name__ == "__main__":
    main()
