import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import datetime
from fpdf import FPDF
import os
# from PIL import Image

# Connect to SQLite database
conn = sqlite3.connect("invoice.db")
cursor = conn.cursor()

# Ensure the table structure is correct
cursor.execute('''
    CREATE TABLE IF NOT EXISTS invoices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        invoice_to TEXT,
        address TEXT,
        postcode TEXT,
        phone TEXT,
        items TEXT,
        subtotal REAL,
        tax REAL,
        total REAL
    )
''')
conn.commit()

class InvoiceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Invoice System new")
        self.root.geometry("1000x650")

        # Invoice Number & Date
        tk.Label(self.root, text="Invoice No:", font=("Arial", 10)).grid(row=0, column=0, padx=5, pady=5)
        self.invoice_number = tk.Entry(self.root, state="disabled")
        self.invoice_number.grid(row=0, column=1, padx=5, pady=5)
        self.load_invoice_number()  # Auto-increment invoice number

        tk.Label(self.root, text="Date:", font=("Arial", 10)).grid(row=0, column=2, padx=5, pady=5)
        self.date = tk.Entry(self.root)
        self.date.insert(0, datetime.date.today().strftime("%Y-%m-%d"))
        self.date.grid(row=0, column=3, padx=5, pady=5)

        # Invoice To Section
        tk.Label(self.root, text="Invoice To:").grid(row=1, column=0, padx=5, pady=5)
        self.invoice_to = tk.Entry(self.root, width=40)
        self.invoice_to.grid(row=1, column=1, columnspan=3, padx=5, pady=5)

        tk.Label(self.root, text="Address:").grid(row=2, column=0, padx=5, pady=5)
        self.address = tk.Entry(self.root, width=40)
        self.address.grid(row=2, column=1, columnspan=3, padx=5, pady=5)

        tk.Label(self.root, text="Postcode:").grid(row=3, column=0, padx=5, pady=5)
        self.postcode = tk.Entry(self.root, width=20)
        self.postcode.grid(row=3, column=1, padx=5, pady=5)

        tk.Label(self.root, text="Phone:").grid(row=3, column=2, padx=5, pady=5)
        self.phone = tk.Entry(self.root, width=20)
        self.phone.grid(row=3, column=3, padx=5, pady=5)

        # Items Table
        self.tree = ttk.Treeview(self.root, columns=("Item No", "Description", "Quantity", "Price", "Total"),
                                 show="headings")
        self.tree.heading("Item No", text="Item No")
        self.tree.heading("Description", text="Description")
        self.tree.heading("Quantity", text="Quantity")
        self.tree.heading("Price", text="Price (£)")
        self.tree.heading("Total", text="Total (£)")
        self.tree.grid(row=4, column=0, columnspan=4, padx=10, pady=10)

        # Item Entry Fields
        tk.Label(self.root, text="Item No:").grid(row=5, column=0, padx=5, pady=5)
        self.item_no_entry = tk.Entry(self.root)
        self.item_no_entry.grid(row=5, column=1, padx=5, pady=5)

        tk.Label(self.root, text="Description:").grid(row=5, column=2, padx=5, pady=5)
        self.desc_entry = tk.Entry(self.root)
        self.desc_entry.grid(row=5, column=3, padx=5, pady=5)

        tk.Label(self.root, text="Quantity:").grid(row=6, column=0, padx=5, pady=5)
        self.qty_entry = tk.Entry(self.root)
        self.qty_entry.grid(row=6, column=1, padx=5, pady=5)

        tk.Label(self.root, text="Price (£):").grid(row=6, column=2, padx=5, pady=5)
        self.price_entry = tk.Entry(self.root)
        self.price_entry.grid(row=6, column=3, padx=5, pady=5)

        # Add Item Button
        self.add_item_button = tk.Button(self.root, text="Add Item", command=self.add_item)
        self.add_item_button.grid(row=7, column=0, columnspan=4, pady=10)

        # Add Remove Item Button
        self.remove_item_button = tk.Button(self.root, text="Remove Item", command=self.remove_item)
        self.remove_item_button.grid(row=7, column=2, columnspan=2, pady=10)

        # Subtotal, Tax, and Grand Total
        self.subtotal_label = tk.Label(self.root, text="Subtotal: £0.00", font=("Arial", 12))
        self.subtotal_label.grid(row=8, column=0, columnspan=2, pady=5)

        self.tax_label = tk.Label(self.root, text="Tax (0%): £0.00", font=("Arial", 12))
        self.tax_label.grid(row=9, column=0, columnspan=2, pady=5)

        self.total_label = tk.Label(self.root, text="Grand Total: £0.00", font=("Arial", 14, "bold"))
        self.total_label.grid(row=10, column=0, columnspan=2, pady=10)

        # Buttons
        self.submit_button = tk.Button(self.root, text="Submit Invoice", command=self.submit_invoice)
        self.submit_button.grid(row=11, column=0, columnspan=2, pady=10)

        self.view_button = tk.Button(self.root, text="View Invoices", command=self.view_invoices)
        self.view_button.grid(row=11, column=2, columnspan=2, pady=10)

        # Store added items
        self.items = []

    def load_invoice_number(self):
        """ Fetch the last invoice number and increment it. """
        cursor.execute("SELECT MAX(id) FROM invoices")
        result = cursor.fetchone()[0]
        next_invoice = 1 if result is None else result + 1
        self.invoice_number.config(state="normal")
        self.invoice_number.delete(0, tk.END)
        self.invoice_number.insert(0, str(next_invoice))
        self.invoice_number.config(state="disabled")

    def add_item(self):
        """ Adds an item to the table and updates the total. """
        item_no = self.item_no_entry.get()
        desc = self.desc_entry.get()
        qty = self.qty_entry.get()
        price = self.price_entry.get()

        if not item_no or not desc or not qty or not price:
            messagebox.showwarning("Warning", "Please fill all fields!")
            return

        try:
            qty = int(qty)
            price = float(price)
            total = qty * price
        except ValueError:
            messagebox.showerror("Error", "Quantity must be an integer and Price must be a number!")
            return

        # Add item to the internal list and the Treeview
        self.items.append((item_no, desc, qty, price, total))
        self.tree.insert("", "end", values=(item_no, desc, qty, f"£{price:.2f}", f"£{total:.2f}"))

        # Clear the entry fields after adding the item
        self.item_no_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.qty_entry.delete(0, tk.END)
        self.price_entry.delete(0, tk.END)

        # Update totals
        self.update_totals()

    def remove_item(self):
        """ Removes the selected item from the Items Table and updates the total. """
        selected_item = self.tree.selection()

        if not selected_item:
            messagebox.showerror("Error", "Please select an item to remove.")
            return

        # Get selected item values
        item_values = self.tree.item(selected_item, "values")

        # Find and remove the selected item from self.items
        for item in self.items:
            if (str(item[0]) == item_values[0] and
                    item[1] == item_values[1] and
                    str(item[2]) == item_values[2] and
                    f"£{item[3]:.2f}" == item_values[3] and
                    f"£{item[4]:.2f}" == item_values[4]):
                self.items.remove(item)
                break  # Stop after removing the first matching item

        # Remove the item from Treeview
        self.tree.delete(selected_item)

        # Update totals
        self.update_totals()

        messagebox.showinfo("Success", "Item removed successfully!")

    def update_totals(self):
        """ Recalculates the subtotal, tax, and grand total. """
        subtotal = sum(item[4] for item in self.items)
        tax = subtotal * 0.00
        grand_total = subtotal + tax

        self.subtotal_label.config(text=f"Subtotal: £{subtotal:.2f}")
        self.tax_label.config(text=f"Tax (0%): £{tax:.2f}")
        self.total_label.config(text=f"Grand Total: £{grand_total:.2f}")

    def submit_invoice(self):
        """ Saves or updates the invoice in the database. """
        if not self.items:
            messagebox.showerror("Error", "You need to add at least one item.")
            return

        if hasattr(self, 'edit_mode') and self.edit_mode:
            # Update the existing invoice
            cursor.execute("""UPDATE invoices SET date=?, invoice_to=?, address=?, postcode=?, phone=?, items=?, 
                              subtotal=?, tax=?, total=? WHERE id=?""",
                           (self.date.get(), self.invoice_to.get(), self.address.get(), self.postcode.get(),
                            self.phone.get(),
                            str(self.items), sum(item[4] for item in self.items),
                            sum(item[4] for item in self.items) * 0.00,
                            sum(item[4] for item in self.items) * 1.00, self.current_invoice_id))
            conn.commit()
            messagebox.showinfo("Success", "Invoice updated successfully!")
            self.edit_mode = False  # Reset edit mode
            del self.current_invoice_id  # Remove the invoice ID
        else:
            # Insert a new invoice as usual
            cursor.execute("""INSERT INTO invoices (date, invoice_to, address, postcode, phone, items, subtotal, tax, total) 
                              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                           (self.date.get(), self.invoice_to.get(), self.address.get(), self.postcode.get(),
                            self.phone.get(),
                            str(self.items), sum(item[4] for item in self.items),
                            sum(item[4] for item in self.items) * 0.10,
                            sum(item[4] for item in self.items) * 1.10))
            conn.commit()
            messagebox.showinfo("Success", "Invoice submitted successfully!")

        # Hide all widgets and show options
        for widget in self.root.winfo_children():
            if widget.winfo_manager() == 'grid':
                widget.grid_remove()
        self.show_invoice_options()

    def show_invoice_options(self):
        """ Displays only two buttons: 'Generate New Invoice' and 'View Invoices'. """
        self.generate_new_button = tk.Button(self.root, text="Generate New Invoice", font=("Arial", 12),
                                             command=self.show_invoice_form)
        self.generate_new_button.pack(pady=20)

        self.view_invoices_button = tk.Button(self.root, text="View Invoices", font=("Arial", 12),
                                              command=self.view_invoices)
        self.view_invoices_button.pack(pady=10)

    def show_invoice_form(self):
        """ Clears the form and brings back the invoice creation fields. """
        # Destroy the two buttons to prevent duplication
        if hasattr(self, 'generate_new_button'):
            self.generate_new_button.destroy()
        if hasattr(self, 'view_invoices_button'):
            self.view_invoices_button.destroy()

        # Restore all hidden widgets
        for widget in self.root.winfo_children():
            widget.grid()

        # Reset fields
        self.invoice_to.delete(0, tk.END)
        self.address.delete(0, tk.END)
        self.postcode.delete(0, tk.END)
        self.phone.delete(0, tk.END)
        self.tree.delete(*self.tree.get_children())
        self.items.clear()
        self.update_totals()

        if not hasattr(self, 'edit_mode') or not self.edit_mode:
            self.load_invoice_number()

    def edit_selected_invoice(self, tree):
        """ Loads the selected invoice into the form for editing. """
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select an invoice to edit.")
            return

        invoice_id = tree.item(selected_item, "values")[0]

        cursor.execute("SELECT * FROM invoices WHERE id=?", (invoice_id,))
        invoice = cursor.fetchone()
        if not invoice:
            messagebox.showerror("Error", "Invoice not found!")
            return

        # Switch to the invoice form
        self.show_invoice_form()

        # Fill the form with the selected invoice data
        self.invoice_number.config(state="normal")
        self.invoice_number.delete(0, tk.END)
        self.invoice_number.insert(0, invoice[0])
        self.invoice_number.config(state="disabled")

        self.date.delete(0, tk.END)
        self.date.insert(0, invoice[1])

        self.invoice_to.delete(0, tk.END)
        self.invoice_to.insert(0, invoice[2])

        self.address.delete(0, tk.END)
        self.address.insert(0, invoice[3])

        self.postcode.delete(0, tk.END)
        self.postcode.insert(0, invoice[4])

        self.phone.delete(0, tk.END)
        self.phone.insert(0, invoice[5])

        # Load items into the tree view
        self.tree.delete(*self.tree.get_children())  # Clear all items from the table
        self.items.clear()  # Clear the stored items
        items = eval(invoice[6])  # Convert the string back to a list of items
        for item in items:
            self.items.append(item)
            self.tree.insert("", "end", values=(item[0], item[1], item[2], f"£{item[3]:.2f}", f"£{item[4]:.2f}"))

        # Update totals
        self.update_totals()

        # Enable Edit Mode
        self.edit_mode = True
        self.current_invoice_id = invoice_id

    def delete_selected_invoice(self, tree):
        """ Deletes the selected invoice from the database and refreshes the view. """
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select an invoice to delete.")
            return

        # Get the selected invoice ID
        invoice_id = tree.item(selected_item, "values")[0]

        # Confirm the deletion with the user
        confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete invoice #{invoice_id}?")
        if not confirm:
            return

        # Fetch the invoice details before deletion
        cursor.execute("SELECT * FROM invoices WHERE id=?", (invoice_id,))
        invoice = cursor.fetchone()
        if not invoice:
            messagebox.showerror("Error", "Invoice not found!")
            return

        # Generate a PDF for the deleted (clanked) invoice
        self.generate_clanked_invoice_pdf(invoice)


        # Delete the invoice from the database
        cursor.execute("DELETE FROM invoices WHERE id=?", (invoice_id,))
        conn.commit()

        # Remove the selected item from the Treeview
        tree.delete(selected_item)

        # Remove associated PDF files if they exist
        invoice_file = os.path.join("invoices", f"Invoice_{invoice_id}.pdf")
        delivery_note_file = os.path.join("dn", f"Delivery_Note_{invoice_id}.pdf")

        if os.path.exists(invoice_file):
            os.remove(invoice_file)
        if os.path.exists(delivery_note_file):
            os.remove(delivery_note_file)

        messagebox.showinfo("Success", f"Invoice #{invoice_id} deleted successfully!")

    def view_invoices(self):
        """ Opens a new window to show all invoices and allow printing. """
        view_window = tk.Toplevel(self.root)
        view_window.title("Submitted Invoices")
        view_window.geometry("600x400")

        tree = ttk.Treeview(view_window, columns=("ID", "Date", "Invoice To", "Total"), show="headings")
        tree.heading("ID", text="Invoice No")
        tree.heading("Date", text="Date")
        tree.heading("Invoice To", text="Invoice To")
        tree.heading("Total", text="Total (£)")
        tree.pack(fill="both", expand=True)

        cursor.execute("SELECT id, date, invoice_to, total FROM invoices")
        invoices = cursor.fetchall()
        for row in invoices:
            tree.insert("", "end", values=row)

        # Function to print the selected invoice
        def print_selected_invoice():
            selected_item = tree.selection()
            if not selected_item:
                messagebox.showerror("Error", "Please select an invoice to print.")
                return

            invoice_id = tree.item(selected_item, "values")[0]  # Get selected invoice ID
            self.print_invoice(invoice_id)  # Call print_invoice function

        # Function to print the delivery note along with the invoice
        def print_selected_delivery_note():
            selected_item = tree.selection()
            if not selected_item:
                messagebox.showerror("Error", "Please select an invoice to generate the delivery note.")
                return

            invoice_id = tree.item(selected_item, "values")[0]  # Get selected invoice ID
            self.print_invoice(invoice_id)  # Print Invoice
            self.print_delivery_note(invoice_id)  # Print Delivery Note

        # Print Invoice Button
        print_button = tk.Button(view_window, text="Print Invoice", command=print_selected_invoice)
        print_button.pack(pady=10)

        # Delivery Note Button (Prints both Invoice and Delivery Note)
        delivery_note_button = tk.Button(view_window, text="Print Delivery Note", command=print_selected_delivery_note)
        delivery_note_button.pack(pady=10)

        # Edit Invoice Button
        edit_button = tk.Button(view_window, text="Edit Invoice", command=lambda: self.edit_selected_invoice(tree))
        edit_button.pack(pady=10)

        # Delete Invoice Button
        delete_button = tk.Button(view_window, text="Delete Invoice",
                                  command=lambda: self.delete_selected_invoice(tree))
        delete_button.pack(pady=10)

    def print_delivery_note(self, invoice_id):
        """ Generates a Delivery Note PDF and saves it in the 'dn' directory. """

        # Ensure the "dn" directory exists
        dn_dir = "dn"
        if not os.path.exists(dn_dir):
            os.makedirs(dn_dir)

        cursor.execute("SELECT * FROM invoices WHERE id=?", (invoice_id,))
        invoice = cursor.fetchone()
        if not invoice:
            messagebox.showerror("Error", "Invoice not found!")
            return

        dn_filename = os.path.join(dn_dir, f"Delivery_Note_{invoice_id}.pdf")  # Save in "dn" folder
        pdf = FPDF()
        pdf.add_page()

        # Add the logo at the top center
        logo_path = "logo.png"  # Ensure this file is in the same directory
        if os.path.exists(logo_path):
            pdf.image(logo_path, x=25, y=25, w=150, h=200)  # Cover entire A4 page (210mm x 297mm)
            pdf.image("headerlogo.png", x=75, y=10, w=60)  # Adjust `x`, `y`, and `w` as needed

        # Move cursor down after logo
        pdf.ln(20)
        # # Add a simple header
        # pdf.set_font("Arial", "B", 16)
        # pdf.cell(200, 10, "Delivery Note", ln=True, align='C')


        # Set font for details
        pdf.set_font("Arial", size=12)

        # Invoice Header
        # pdf.cell(170, 10, "CASTLE MARKET LTD", ln=True, align='C')
        pdf.cell(170, 10, f"GOLDEN LOOK L.L.C", ln=True)
        pdf.cell(170, 10, f"A240, AL KARAMA SHOPPING COMPLEX, AL KARAMA, DUBAI UAE", ln=True)
        pdf.cell(170, 10, f"Phone: ---------", ln=True)
        pdf.ln(10)

        # Delivery Note Information
        pdf.cell(200, 10, "Delivery Note", ln=True, align='C')
        pdf.cell(85, 10, f"Invoice No: {invoice_id}", ln=True)
        pdf.cell(85, 10, f"Date: {invoice[1]}", ln=True)
        pdf.cell(85, 10, f"Name: {invoice[2]}", ln=True)
        pdf.cell(85, 10, f"Address: {invoice[3]}", ln=True)
        pdf.cell(85, 10, f"Phone: {invoice[5]}", ln=True)
        pdf.ln(10)

        # Table Header
        pdf.set_font("Arial", style='B', size=12)
        pdf.cell(100, 10, "Description", border=1)
        pdf.cell(30, 10, "Quantity", border=1, align='C')
        pdf.ln()

        # Convert stored items back to list
        pdf.set_font("Arial", size=12)
        items = eval(invoice[6])  # Convert string back to list of tuples
        for item in items:
            pdf.cell(100, 10, str(item[1]), border=1)
            pdf.cell(30, 10, str(item[2]), border=1, align='C')
            pdf.ln()

        # Space for receiver's signature
        pdf.ln(10)
        pdf.cell(170, 10, "Receiver's Name:", ln=True)
        pdf.cell(170, 10, "Receiver's Phone Number:", ln=True)
        pdf.ln(15)
        pdf.cell(170, 10, "Receiver's Signature: ____________________________", ln=True)

        pdf.output(dn_filename)

        messagebox.showinfo("Success", f"Delivery Note saved as {dn_filename}")

        # Automatically open the PDF
        if os.name == 'nt':  # Windows
            os.startfile(dn_filename)
        elif os.name == 'posix':  # macOS/Linux
            os.system(f"open {dn_filename}")









    def print_invoice(self, invoice_id):
        """ Generates and saves the invoice as a PDF in the 'invoices' directory with 2 cm right padding and opens it. """

        # Ensure the "invoices" directory exists
        invoices_dir = "invoices"
        if not os.path.exists(invoices_dir):
            os.makedirs(invoices_dir)

        cursor.execute("SELECT * FROM invoices WHERE id=?", (invoice_id,))
        invoice = cursor.fetchone()
        if not invoice:
            messagebox.showerror("Error", "Invoice not found!")
            return

        pdf_filename = os.path.join(invoices_dir, f"Invoice_{invoice_id}.pdf")  # Save in "invoices" folder
        pdf = FPDF()
        pdf.add_page()

        # Add the logo at the top center
        logo_path = "logo.png"  # Ensure this file is in the same directory
        if os.path.exists(logo_path):
            pdf.image(logo_path, x=25, y=25, w=150, h=200)  # Cover entire A4 page (210mm x 297mm)
            pdf.image("headerlogo.png", x=75, y=10, w=60)  # Adjust `x`, `y`, and `w` as needed


        # Move cursor down after logo
        pdf.ln(20)

        # Set left margin to 1 cm (10 mm)
        pdf.set_left_margin(10)

        # Set font
        pdf.set_font("Arial", size=12)

        # Invoice Header
        # pdf.cell(170, 10, "CASTLE MARKET LTD", ln=True, align='C')
        pdf.cell(170, 10, f"GOLDEN LOOK L.L.C", ln=True)
        pdf.cell(170, 10, f"A 240 AL KARAMA SHOPPING COMPLEX, AL KARAMA, DUBAI, UAE", ln=True)
        pdf.cell(170, 10, f"Phone: ------------", ln=True)
        pdf.ln(10)
        # Invoice Header with Invoice No on the left and Date on the right
        pdf.cell(85, 10, f"Invoice No: {invoice_id}", border=0, align='L')  # Left-aligned
        pdf.cell(85, 10, f"Date: {invoice[1]}", border=0, align='R', ln=True)  # Right-aligned
        pdf.cell(85, 10, f"Bill To: {invoice[2]}", ln=True)
        pdf.cell(85, 10, f"Address: {invoice[3]}", ln=True)
        pdf.cell(85, 10, f"Postcode: {invoice[4]}", ln=True)
        pdf.cell(85, 10, f"Phone: {invoice[5]}", ln=True)
        pdf.ln(10)

        # Table Header
        pdf.set_font("Arial", style='B', size=12)
        pdf.cell(30, 10, "Item No", border=1)
        pdf.cell(70, 10, "Description", border=1)
        pdf.cell(25, 10, "Quantity", border=1, align='C')
        pdf.cell(25, 10, "Price (£)", border=1, align='R')
        pdf.cell(25, 10, "Total (£)", border=1, align='R')
        pdf.ln()

        # Convert stored items back to list
        pdf.set_font("Arial", size=12)
        items = eval(invoice[6])  # Convert string back to list of tuples
        for item in items:
            pdf.cell(30, 10, str(item[0]), border=1)
            pdf.cell(70, 10, str(item[1]), border=1)
            pdf.cell(25, 10, str(item[2]), border=1, align='C')
            pdf.cell(25, 10, f"£{item[3]:.2f}", border=1, align='R')
            pdf.cell(25, 10, f"£{item[4]:.2f}", border=1, align='R')
            pdf.ln()

        # Subtotal, Tax, and Total
        pdf.ln(5)
        pdf.cell(170, 10, f"Subtotal: £{invoice[7]:.2f}", ln=True, align='R')
        pdf.cell(170, 10, f"Tax (0%): £{invoice[8]:.2f}", ln=True, align='R')
        pdf.cell(170, 10, f"Grand Total: £{invoice[9]:.2f}", ln=True, align='R')

        pdf.output(pdf_filename)

        messagebox.showinfo("Success", f"Invoice saved as {pdf_filename}")

        # Automatically open the PDF (cross-platform)
        if os.name == 'nt':  # Windows
            os.startfile(pdf_filename)
        elif os.name == 'posix':  # macOS/Linux
            os.system(f"open {pdf_filename}")

    def generate_clanked_invoice_pdf(self, invoice):
        """ Generates and saves a PDF for a clanked (deleted) invoice. """

        # Ensure the "deletedInvoices" directory exists
        deleted_invoices_dir = "deletedInvoices"
        if not os.path.exists(deleted_invoices_dir):
            os.makedirs(deleted_invoices_dir)

        invoice_id = invoice[0]
        pdf_filename = os.path.join(deleted_invoices_dir, f"Clanked_Invoice_{invoice_id}.pdf")
        pdf = FPDF()
        pdf.add_page()

        # Add the logo at the top center
        logo_path = "logo.png"
        if os.path.exists(logo_path):
            pdf.image(logo_path, x=25, y=25, w=150, h=200)
            pdf.image("headerlogo.png", x=75, y=10, w=60)

        pdf.ln(20)
        pdf.set_left_margin(10)
        pdf.set_font("Arial", size=12)

        # Invoice Header
        pdf.cell(170, 10, f"GOLDEN LOOK TRADING L.L.C", ln=True)
        pdf.cell(170, 10, f"A 240 AL KARAMA SHOPPING COMPLEX, AL KARAMA, DUBAI, UAE", ln=True)
        pdf.cell(170, 10, f"Phone: -------", ln=True)
        pdf.ln(10)

        pdf.cell(85, 10, f"Invoice No: {invoice_id}", border=0, align='L')
        pdf.cell(85, 10, f"Date: {invoice[1]}", border=0, align='R', ln=True)
        pdf.cell(85, 10, f"Bill To: {invoice[2]}", ln=True)
        pdf.cell(85, 10, f"Address: {invoice[3]}", ln=True)
        pdf.cell(85, 10, f"Postcode: {invoice[4]}", ln=True)
        pdf.cell(85, 10, f"Phone: {invoice[5]}", ln=True)
        pdf.ln(10)

        # Table Header
        pdf.set_font("Arial", style='B', size=12)
        pdf.cell(30, 10, "Item No", border=1)
        pdf.cell(70, 10, "Description", border=1)
        pdf.cell(25, 10, "Quantity", border=1, align='C')
        pdf.cell(25, 10, "Price (£)", border=1, align='R')
        pdf.cell(25, 10, "Total (£)", border=1, align='R')
        pdf.ln()

        # Convert stored items back to list
        pdf.set_font("Arial", size=12)
        items = eval(invoice[6])
        for item in items:
            pdf.cell(30, 10, str(item[0]), border=1)
            pdf.cell(70, 10, str(item[1]), border=1)
            pdf.cell(25, 10, str(item[2]), border=1, align='C')
            pdf.cell(25, 10, f"£{item[3]:.2f}", border=1, align='R')
            pdf.cell(25, 10, f"£{item[4]:.2f}", border=1, align='R')
            pdf.ln()

        pdf.ln(5)
        pdf.cell(170, 10, f"Subtotal: £{invoice[7]:.2f}", ln=True, align='R')
        pdf.cell(170, 10, f"Tax (0%): £{invoice[8]:.2f}", ln=True, align='R')
        pdf.cell(170, 10, f"Grand Total: £{invoice[9]:.2f}", ln=True, align='R')

        # Add the clanked message at the bottom
        pdf.ln(20)
        pdf.set_font("Arial", style='B', size=14)
        pdf.set_text_color(255, 0, 0)  # Red text for the clanked message
        pdf.cell(200, 10, "This invoice has been cancelled.", ln=True,
                 align='C')

        pdf.output(pdf_filename)

        messagebox.showinfo("Success", f"Clanked Invoice saved as {pdf_filename}")

        # Automatically open the PDF
        if os.name == 'nt':  # Windows
            os.startfile(pdf_filename)
        elif os.name == 'posix':  # macOS/Linux
            os.system(f"open {pdf_filename}")


if __name__ == "__main__":
    root = tk.Tk()
    app = InvoiceApp(root)
    root.mainloop()
