import mysql.connector

def get_db_connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="parola_ta",
        database="chat_db"
    )
    return conn
