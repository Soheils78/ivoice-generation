# Invoice Generation System

This is a small project for an invoice generation system using Python.  
I developed this project for **Golden Look L.L.C**, a company based in Dubai.

The project uses:
- **Tkinter** → for the user interface (GUI)
- **SQLite** → for saving the invoice data into a database
- **FPDF** → for creating PDF files

---

## How It Works

 - You can add customer details (name, address, phone).  
 - You can add items (with item number, description, quantity, and price).  
 - You can save the invoice into the database.  
 - You can view, edit, or delete the invoices.  
 - You can generate **PDF invoices** and **PDF delivery notes**.

---

## Project Files and Folders

- **main.py** → this is the main Python file that runs the whole program.
- **invoice.db** → the SQLite database file where all invoice records are saved.
- **invoices/** → this folder saves the PDF files for each invoice you create.
- **dn/** → this folder saves the delivery note PDF files.
- **deletedInvoices/** → this folder saves the PDF files for invoices that were deleted (so you still have a record).

---

## How to Run

1. Make sure you have Python installed.
2. Install the required Python libraries.

---

## Notes

- This project is still simple and can be improved.
- Some features like tax are set to 0% now.
- The system will create folders automatically if they don’t exist.

---

## Author

This project was implemented by **Soheil Salemi** for **Golden Look L.L.C** (Dubai).  
I have the right and permission to share this project on my GitHub.

Thank you for checking my project!
