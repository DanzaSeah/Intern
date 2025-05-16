import mysql.connector
import tkinter as tk
from tkinter import ttk, messagebox

def fetch_table_names(conn):
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES;")
    tables = [row[0] for row in cursor.fetchall()]
    cursor.close()
    return tables

def fetch_table_data(conn, table_name):
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name};")
    columns = [col[0] for col in cursor.description]
    rows = cursor.fetchall()
    cursor.close()
    return columns, rows

def launch_ui():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="password",
            database="pandapower_db"
        )
    except Exception as e:
        messagebox.showerror("Database Error", str(e))
        return

    root = tk.Tk()
    root.title("Pandapower DB Viewer")
    root.geometry("900x600")

    table_names = fetch_table_names(conn)
    table_var = tk.StringVar(value=table_names[0])

    frame = tk.Frame(root)
    frame.pack(expand=True, fill='both')

    tree = None

    def update_table(selected_table):
        nonlocal tree
        for widget in frame.winfo_children():
            widget.destroy()

        columns, rows = fetch_table_data(conn, selected_table)

        tree = ttk.Treeview(frame, columns=columns, show='headings')
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor=tk.CENTER, stretch=True)
        for row in rows:
            tree.insert('', tk.END, values=row)
        tree.pack(expand=True, fill='both')

    def refresh_table():
        update_table(table_var.get())
        root.after(10, refresh_table)  

    dropdown = ttk.OptionMenu(root, table_var, table_names[0], *table_names, command=update_table)
    dropdown.pack(pady=10)

    refresh_btn = ttk.Button(root, text="Refresh Now", command=lambda: update_table(table_var.get()))
    refresh_btn.pack(pady=5)

    update_table(table_var.get())
    root.after(10, refresh_table)

    root.mainloop()

if __name__ == "__main__":
    launch_ui()
