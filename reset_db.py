"""
Reset the Supabase database schema.
WARNING: This will DROP all tables and data! Use with extreme caution.

Usage:
    python reset_db.py
"""
import environ
import dj_database_url

env = environ.Env()
environ.Env.read_env(".env")

import psycopg2

# Parse DATABASE_URL from .env (same one Django uses)
db_config = dj_database_url.parse(env("DATABASE_URL"))

conn = psycopg2.connect(
    dbname=db_config["NAME"],
    user=db_config["USER"],
    password=db_config["PASSWORD"],
    host=db_config["HOST"],
    port=db_config["PORT"],
)
conn.autocommit = True
with conn.cursor() as cursor:
    cursor.execute("DROP SCHEMA public CASCADE;")
    cursor.execute("CREATE SCHEMA public;")
    cursor.execute("GRANT ALL ON SCHEMA public TO postgres;")
    cursor.execute("GRANT ALL ON SCHEMA public TO public;")
conn.close()
print("Successfully reset the Supabase database schema.")
