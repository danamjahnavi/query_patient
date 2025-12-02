import os
from dotenv import load_dotenv
import streamlit as st

def get_db_url():
    if "DB_USER" in st.secrets:
        user = st.secrets["DB_USER"]
        password = st.secrets["DB_PASSWORD"]
        host = st.secrets["DB_HOST"]
        database = st.secrets["DB_NAME"]
        port = st.secrets.get("DB_PORT", "5432")
        return f"postgresql://{user}:{password}@{host}:{port}/{database}"

    
    load_dotenv()
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST")
    database = os.getenv("DB_NAME")
    port = os.getenv("DB_PORT", "5432")

    if not all([user, password, host, database]):
        raise Exception("Missing DB credentials in st.secrets or .env")

    return f"postgresql://{user}:{password}@{host}:{port}/{database}"
