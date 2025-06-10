import psycopg2

DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'Integrationdatabase'
DB_USER = 'efrat'
DB_PASSWORD = 'efrat123'

def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
