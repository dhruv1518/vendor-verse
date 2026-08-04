import psycopg2
import environ

env = environ.Env()
environ.Env.read_env(".env")

conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password=env("DB_PASSWORD"),
    host="db.vzpbunqdvdaqtqpbpfnq.supabase.co",
    port="5432"
)
conn.autocommit = True
with conn.cursor() as cursor:
    cursor.execute("DROP SCHEMA public CASCADE;")
    cursor.execute("CREATE SCHEMA public;")
    cursor.execute("GRANT ALL ON SCHEMA public TO postgres;")
    cursor.execute("GRANT ALL ON SCHEMA public TO public;")
conn.close()
print("Successfully reset the Supabase database schema.")
