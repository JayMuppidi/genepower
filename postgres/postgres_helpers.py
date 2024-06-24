from dotenv import load_dotenv
import os
import psycopg2 #used for interacting with the database
load_dotenv()# write details like host, user, password, dbname in .env file, this loads them into this script
db_name = os.getenv("PG_DB_NAME")
user = os.getenv("PG_DB_USER")
password = os.getenv("PG_DB_PASSWORD")
host = os.getenv("PG_DB_HOST")
port = int(os.getenv("PG_DB_PORT"))

def postgresQ(query):
    conn = psycopg2.connect(
        dbname=db_name,
        user=user,
        password=password,
        host=host,
        port=port
    )
    cur = conn.cursor()
    cur.execute(query)
    results = cur.fetchall() if cur.description else None
    return results