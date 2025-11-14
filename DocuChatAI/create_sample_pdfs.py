from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import os

os.makedirs("sample_docs", exist_ok=True)


def create_invoice_pdf():
    filename = "sample_docs/sample_invoice.pdf"
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    c.setFont("Helvetica-Bold", 24)
    c.drawString(1*inch, height - 1*inch, "INVOICE")
    
    c.setFont("Helvetica", 12)
    c.drawString(1*inch, height - 1.5*inch, "From: Example Tech Solutions")
    c.drawString(1*inch, height - 1.7*inch, "123 Business Street, Riyadh, Saudi Arabia")
    c.drawString(1*inch, height - 1.9*inch, "VAT: 300123456700003")
    
    c.drawString(1*inch, height - 2.4*inch, "Invoice Number: INV-2025-101")
    c.drawString(1*inch, height - 2.6*inch, "Invoice Date: 2025-11-01")
    c.drawString(1*inch, height - 2.8*inch, "Due Date: 2025-12-01")
    
    c.setFont("Helvetica-Bold", 14)
    c.drawString(1*inch, height - 3.3*inch, "Items:")
    
    c.setFont("Helvetica", 11)
    y_position = height - 3.7*inch
    c.drawString(1*inch, y_position, "Cloud Service Subscription")
    c.drawString(5*inch, y_position, "1 x 1000.00 SAR")
    
    y_position -= 0.3*inch
    c.drawString(1*inch, y_position, "Support Hours")
    c.drawString(5*inch, y_position, "5 x 100.00 SAR")
    
    c.setFont("Helvetica-Bold", 14)
    y_position -= 0.5*inch
    c.drawString(4*inch, y_position, "Total Amount: 1,500.00 SAR")
    
    c.setFont("Helvetica", 10)
    y_position -= 0.8*inch
    c.drawString(1*inch, y_position, "Payment Terms: Net 30 days")
    c.drawString(1*inch, y_position - 0.2*inch, "Bank Transfer: IBAN SA1234567890123456789012")
    
    c.save()
    print(f"Created: {filename}")


def create_id_pdf():
    filename = "sample_docs/sample_national_id.pdf"
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    c.setFont("Helvetica-Bold", 20)
    c.drawString(2*inch, height - 1*inch, "NATIONAL IDENTITY CARD")
    c.drawString(2*inch, height - 1.3*inch, "Kingdom of Saudi Arabia")
    
    c.setFont("Helvetica", 12)
    c.drawString(1.5*inch, height - 2*inch, "ID Number: 1234567890")
    c.drawString(1.5*inch, height - 2.3*inch, "Name: Ahmed Mohammed Al-Rashid")
    c.drawString(1.5*inch, height - 2.6*inch, "Date of Birth: 15/03/1990")
    c.drawString(1.5*inch, height - 2.9*inch, "Gender: Male")
    c.drawString(1.5*inch, height - 3.2*inch, "Nationality: Saudi Arabia")
    c.drawString(1.5*inch, height - 3.5*inch, "Issue Date: 01/01/2020")
    c.drawString(1.5*inch, height - 3.8*inch, "Expiry Date: 01/01/2030")
    
    c.save()
    print(f"Created: {filename}")


def create_bank_statement_pdf():
    filename = "sample_docs/sample_bank_statement.pdf"
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    c.setFont("Helvetica-Bold", 18)
    c.drawString(2*inch, height - 1*inch, "BANK STATEMENT")
    
    c.setFont("Helvetica", 12)
    c.drawString(1*inch, height - 1.5*inch, "Al Rajhi Bank")
    c.drawString(1*inch, height - 1.7*inch, "P.O. Box 28, Riyadh 11411, Saudi Arabia")
    
    c.drawString(1*inch, height - 2.2*inch, "Account Number: SA1234567890")
    c.drawString(1*inch, height - 2.4*inch, "Account Holder: Mohammed Abdullah")
    c.drawString(1*inch, height - 2.6*inch, "Statement Period: 01/10/2025 - 31/10/2025")
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(1*inch, height - 3.1*inch, "Opening Balance: 15,000.00 SAR")
    c.drawString(1*inch, height - 3.3*inch, "Closing Balance: 18,450.00 SAR")
    
    c.setFont("Helvetica", 11)
    y_position = height - 3.8*inch
    c.drawString(1*inch, y_position, "Recent Transactions:")
    
    y_position -= 0.3*inch
    c.drawString(1*inch, y_position, "05/10/2025 - Salary Deposit")
    c.drawString(5*inch, y_position, "+ 8,000.00 SAR")
    
    y_position -= 0.3*inch
    c.drawString(1*inch, y_position, "10/10/2025 - Rent Payment")
    c.drawString(5*inch, y_position, "- 3,500.00 SAR")
    
    y_position -= 0.3*inch
    c.drawString(1*inch, y_position, "15/10/2025 - Utility Bill")
    c.drawString(5*inch, y_position, "- 450.00 SAR")
    
    c.save()
    print(f"Created: {filename}")


def create_payslip_pdf():
    filename = "sample_docs/sample_payslip.pdf"
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    c.setFont("Helvetica-Bold", 20)
    c.drawString(2.5*inch, height - 1*inch, "PAYSLIP")
    
    c.setFont("Helvetica", 12)
    c.drawString(1*inch, height - 1.5*inch, "Company: Tech Arabia Ltd.")
    c.drawString(1*inch, height - 1.7*inch, "Pay Period: October 2025")
    
    c.drawString(1*inch, height - 2.2*inch, "Employee Name: Fatima Al-Zahrani")
    c.drawString(1*inch, height - 2.4*inch, "Employee ID: EMP-5678")
    c.drawString(1*inch, height - 2.6*inch, "Department: Engineering")
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(1*inch, height - 3.1*inch, "Earnings:")
    c.setFont("Helvetica", 11)
    c.drawString(1.5*inch, height - 3.4*inch, "Basic Salary: 12,000.00 SAR")
    c.drawString(1.5*inch, height - 3.6*inch, "Housing Allowance: 3,000.00 SAR")
    c.drawString(1.5*inch, height - 3.8*inch, "Transport Allowance: 1,000.00 SAR")
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(1*inch, height - 4.3*inch, "Gross Salary: 16,000.00 SAR")
    
    c.setFont("Helvetica", 11)
    c.drawString(1*inch, height - 4.8*inch, "Deductions:")
    c.drawString(1.5*inch, height - 5.1*inch, "GOSI: 960.00 SAR")
    c.drawString(1.5*inch, height - 5.3*inch, "Medical Insurance: 200.00 SAR")
    
    c.setFont("Helvetica-Bold", 14)
    c.drawString(1*inch, height - 5.8*inch, "Net Pay: 14,840.00 SAR")
    
    c.save()
    print(f"Created: {filename}")


if __name__ == "__main__":
    create_invoice_pdf()
    create_id_pdf()
    create_bank_statement_pdf()
    create_payslip_pdf()
    print("\nAll sample PDFs created successfully!")
