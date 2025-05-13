import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="password",
    database="pandapower_db"
)
cursor = conn.cursor()
cursor.execute("SHOW TABLES;")
for row in cursor.fetchall():
    print(row)

cursor.execute("SELECT * from fm;")
for row in cursor.fetchall():
    print(row)

cursor.execute("SELECT * from bus_voltage ORDER BY value;")
for row in cursor.fetchall():
    print(row)
conn.close()