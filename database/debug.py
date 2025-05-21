import mysql.connector

conn = mysql.connector.connect(
        host="192.168.192.1",
        user="root",
        password="password",
        database="pandapower_db"
    )
cursor = conn.cursor()
cursor.execute("UPDATE line_cb SET value = %s WHERE name = 'line_cb_0'", (0,))
conn.commit()
conn.close()