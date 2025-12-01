import os
from dotenv import find_dotenv, load_dotenv

# Load .env file anywhere in project
dotenv_path = find_dotenv()
if dotenv_path:
    load_dotenv(dotenv_path)
else:
    raise Exception(".env file not found!")

def get_db_url():
    POSTGRES_USERNAME = os.getenv("POSTGRES_USERNAME")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_SERVER = os.getenv("POSTGRES_SERVER")
    POSTGRES_DATABASE = os.getenv("POSTGRES_DATABASE")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

    print("DEBUG:", POSTGRES_USERNAME, POSTGRES_SERVER, POSTGRES_DATABASE)

    if None in [POSTGRES_USERNAME, POSTGRES_PASSWORD, POSTGRES_SERVER, POSTGRES_DATABASE]:
        raise Exception("Missing environment variables!")

    return f"postgresql://{POSTGRES_USERNAME}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DATABASE}"
