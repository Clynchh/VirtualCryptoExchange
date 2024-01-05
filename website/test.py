import flask
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

username = "bob"
password = "bob1234"

connection = sqlite3.connect("C:\\Users\\corey\\OneDrive\\Desktop\\Database_Working\\website\\exchange.db")
cursor = connection.cursor()
cursor.execute("""
    SELECT hashed_password 
    FROM users where username = ?""", (username,))

hashed_pass = cursor.fetchone()

connection.commit()
connection.close()
print(hashed_pass[0])

print()