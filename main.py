import csv
import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk


# Database connection and setup
def connect_db():
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS inventory (
                        product_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        product_name TEXT NOT NULL UNIQUE,
                        quantity INTEGER NOT NULL)''')
    conn.commit()
    conn.close()

# Function to add a new product
def add_product():
    product_name = entry_name.get().strip()
    try:
        product_quantity = int(entry_quantity.get())
    except ValueError:
        messagebox.showerror("Invalid Input", "Quantity must be a number.")
        return
    
    if product_name == "":
        messagebox.showerror("Input Error", "Product Name cannot be empty.")
        return
    
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    
    try:
        cursor.execute("INSERT INTO inventory (product_name, quantity) VALUES (?, ?)",
                       (product_name, product_quantity))
        conn.commit()
        update_inventory_list()
        clear_entries()
        messagebox.showinfo("Success", f"Product '{product_name}' added.")
    except sqlite3.IntegrityError:
        messagebox.showerror("Duplicate Entry", "Product already exists.")
    
    conn.close()

# Function to update an existing product
def update_product():
    product_name = entry_name.get().strip()
    try:
        product_quantity = int(entry_quantity.get())
    except ValueError:
        messagebox.showerror("Invalid Input", "Quantity must be a number.")
        return
    
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE inventory SET quantity = ? WHERE product_name = ?",
                   (product_quantity, product_name))
    
    if cursor.rowcount == 0:
        messagebox.showerror("Error", f"Product '{product_name}' not found.")
    else:
        conn.commit()
        update_inventory_list()
        clear_entries()
        messagebox.showinfo("Success", f"Product '{product_name}' updated to {product_quantity} units.")

    conn.close()
    
# Function to delete a product
def delete_product():
    product_name = entry_name.get().strip()
    
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM inventory WHERE product_name = ?", (product_name,))
    
    if cursor.rowcount == 0:
        messagebox.showerror("Error", f"Product '{product_name}' not found.")
    else:
        conn.commit()
        update_inventory_list()
        clear_entries()
        messagebox.showinfo("Success", f"Product '{product_name}' deleted.")
    
    conn.close()

# Function to search products
def search_product():
    search_query = entry_search.get().strip()
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM inventory WHERE product_name LIKE ?", ('%' + search_query + '%',))
    products = cursor.fetchall()
    
    listbox_inventory.delete(*listbox_inventory.get_children())
    
    for product in products:
        listbox_inventory.insert('', 'end', values=(product[0], product[1], product[2]))
    
    conn.close()

# Function to update the inventory list
def update_inventory_list():
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM inventory")
    products = cursor.fetchall()
    
    listbox_inventory.delete(*listbox_inventory.get_children())
    
    for product in products:
        listbox_inventory.insert('', 'end', values=(product[0], product[1], product[2]))
    
    conn.close()

# Function to export inventory to a CSV file
def export_to_csv():
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM inventory")
    products = cursor.fetchall()
    
    with open("inventory_report.csv", "w", newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Product ID", "Product Name", "Quantity"])
        writer.writerows(products)
    
    messagebox.showinfo("Export Successful", "Inventory data exported to inventory_report.csv")
    
    conn.close()

# Function to clear entry fields
def clear_entries():
    entry_name.delete(0, tk.END)
    entry_quantity.delete(0, tk.END)

# Login functionality
def login():
    username = entry_username.get().strip()
    password = entry_password.get().strip()
    
    if username == "" or password == "":
        messagebox.showerror("Error", "Username and password cannot be empty.")
        return
    
    try:
        with open("users.csv", mode="r") as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0] == username and row[1] == password:
                    login_window.destroy()  # Close the login window
                    main_window()  # Open the main inventory window
                    return
        messagebox.showerror("Error", "Invalid credentials.")
    except FileNotFoundError:
        messagebox.showerror("Error", "No users found. Please register first.")

# Registration functionality
def register():
    username = entry_username.get().strip()
    password = entry_password.get().strip()
    
    if username == "" or password == "":
        messagebox.showerror("Error", "Username and password cannot be empty.")
        return
    
    try:
        with open("users.csv", mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([username, password])
            messagebox.showinfo("Success", "Registration successful.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

# Main inventory management window
def main_window():
    global entry_name, entry_quantity, entry_search, listbox_inventory
    
    root = tk.Tk()
    root.title("Inventory Management System")
    root.geometry("650x550")
    
    # Title label at the top center
    title_label = tk.Label(root, text="Inventory Management System", font=("Arial", 16, "bold"),)
    title_label.grid(row=0, column=0, columnspan=3, pady=10)
    
    # Connecting to the database and setting up tables
    connect_db()

    # Labels and entry fields for product name and quantity
    label_name = tk.Label(root, text="Product Name:")
    label_name.grid(row=1, column=0, padx=10, pady=10)
    entry_name = tk.Entry(root)
    entry_name.grid(row=1, column=1, padx=10, pady=10)

    label_quantity = tk.Label(root, text="Quantity:")
    label_quantity.grid(row=2, column=0, padx=10, pady=10)
    entry_quantity = tk.Entry(root)
    entry_quantity.grid(row=2, column=1, padx=10, pady=10)

    # Buttons to add, update, delete, and search products
    button_add = tk.Button(root, text="Add Product", command=add_product, activebackground="lightgreen")
    button_add.grid(row=3, column=0, padx=10, pady=10)

    button_update = tk.Button(root, text="Update Product", command=update_product, activebackground="skyblue")
    button_update.grid(row=3, column=1, padx=10, pady=10)

    button_delete = tk.Button(root, text="Delete Product", command=delete_product, activebackground="red")
    button_delete.grid(row=3, column=2, padx=10, pady=10)

    # Search field
    label_search = tk.Label(root, text="Search Product:")
    label_search.grid(row=4, column=0, padx=10, pady=10)
    entry_search = tk.Entry(root)
    entry_search.grid(row=4, column=1, padx=10, pady=10)

    button_search = tk.Button(root, text="Search", command=search_product)
    button_search.grid(row=4, column=2, padx=10, pady=10)

    # Inventory list (Treeview) to display current inventory
    listbox_inventory = ttk.Treeview(root, columns=("Product ID", "Product Name", "Quantity"), show="headings")
    listbox_inventory.heading("Product ID", text="Product ID")
    listbox_inventory.heading("Product Name", text="Product Name")
    listbox_inventory.heading("Quantity", text="Quantity")
    listbox_inventory.grid(row=5, column=0, columnspan=3, padx=10, pady=10)

    # Export to CSV button
    button_export = tk.Button(root, text="Export to CSV", command=export_to_csv, activebackground="yellow")
    button_export.grid(row=6, column=0, columnspan=3, pady=10)

    # Populate the inventory list on startup
    update_inventory_list()

    # Start the Tkinter main loop
    root.mainloop()

# Login window
login_window = tk.Tk()
login_window.title("Login")
login_window.geometry("300x300")

label_username = tk.Label(login_window, text="Username:")
label_username.pack(pady=10)
entry_username = tk.Entry(login_window)
entry_username.pack()

label_password = tk.Label(login_window, text="Password:")
label_password.pack(pady=10)
entry_password = tk.Entry(login_window, show="*")
entry_password.pack()

button_login = tk.Button(login_window, text="Login", command=login)
button_login.pack(pady=10)

button_register = tk.Button(login_window, text="Register", command=register)
button_register.pack(pady=10)

login_window.mainloop()
