"""
Sample Invoice and PO Generator
Run this to create test data for the verification system
"""
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from pathlib import Path
import random
from datetime import datetime, timedelta

class SampleDataGenerator:
    def __init__(self):
        self.invoice_dir = Path("data/invoices")
        self.po_dir = Path("data/purchase_orders")

        # Create directories
        self.invoice_dir.mkdir(parents=True, exist_ok=True)
        self.po_dir.mkdir(parents=True, exist_ok=True)

    def generate_invoice_pdf(self, invoice_num, vendor_name, items, output_path):
        """Generate a sample invoice PDF"""
        c = canvas.Canvas(str(output_path), pagesize=letter)
        width, height = letter

        # Title
        c.setFont("Helvetica-Bold", 24)
        c.drawString(1*inch, height - 1*inch, "INVOICE")

        # Invoice details
        c.setFont("Helvetica", 12)
        y = height - 1.5*inch

        c.drawString(1*inch, y, f"Invoice Number: {invoice_num}")
        y -= 0.3*inch
        c.drawString(1*inch, y, f"Invoice Date: {datetime.now().strftime('%Y-%m-%d')}")
        y -= 0.3*inch
        c.drawString(1*inch, y, f"Vendor: {vendor_name}")

        # Line items header
        y -= 0.8*inch
        c.setFont("Helvetica-Bold", 12)
        c.drawString(1*inch, y, "Item Description")
        c.drawString(3.5*inch, y, "Qty")
        c.drawString(4.5*inch, y, "Unit Price")
        c.drawString(6*inch, y, "Total")

        # Line items
        c.setFont("Helvetica", 11)
        y -= 0.05*inch
        c.line(1*inch, y, 7*inch, y)
        y -= 0.3*inch

        subtotal = 0
        for item in items:
            c.drawString(1*inch, y, item['description'][:30])
            c.drawString(3.5*inch, y, str(item['quantity']))
            c.drawString(4.5*inch, y, f"${item['unit_price']:.2f}")
            line_total = item['quantity'] * item['unit_price']
            c.drawString(6*inch, y, f"${line_total:.2f}")
            subtotal += line_total
            y -= 0.3*inch

        # Totals
        y -= 0.2*inch
        c.line(5*inch, y, 7*inch, y)
        y -= 0.3*inch

        c.setFont("Helvetica", 12)
        c.drawString(5*inch, y, "Subtotal:")
        c.drawString(6*inch, y, f"${subtotal:.2f}")
        y -= 0.3*inch

        tax = subtotal * 0.1  # 10% tax
        c.drawString(5*inch, y, "Tax (10%):")
        c.drawString(6*inch, y, f"${tax:.2f}")
        y -= 0.3*inch

        c.setFont("Helvetica-Bold", 14)
        total = subtotal + tax
        c.drawString(5*inch, y, "TOTAL:")
        c.drawString(6*inch, y, f"${total:.2f}")

        c.save()
        print(f"✅ Generated invoice: {output_path.name}")
        return total

    def generate_po_pdf(self, po_num, vendor_name, items, output_path):
        """Generate a sample purchase order PDF"""
        c = canvas.Canvas(str(output_path), pagesize=letter)
        width, height = letter

        # Title
        c.setFont("Helvetica-Bold", 24)
        c.drawString(1*inch, height - 1*inch, "PURCHASE ORDER")

        # PO details
        c.setFont("Helvetica", 12)
        y = height - 1.5*inch

        c.drawString(1*inch, y, f"PO Number: {po_num}")
        y -= 0.3*inch
        c.drawString(1*inch, y, f"PO Date: {datetime.now().strftime('%Y-%m-%d')}")
        y -= 0.3*inch
        c.drawString(1*inch, y, f"Vendor: {vendor_name}")

        # Line items header
        y -= 0.8*inch
        c.setFont("Helvetica-Bold", 12)
        c.drawString(1*inch, y, "Item Description")
        c.drawString(3.5*inch, y, "Qty")
        c.drawString(4.5*inch, y, "Unit Price")
        c.drawString(6*inch, y, "Total")

        # Line items
        c.setFont("Helvetica", 11)
        y -= 0.05*inch
        c.line(1*inch, y, 7*inch, y)
        y -= 0.3*inch

        total = 0
        for item in items:
            c.drawString(1*inch, y, item['description'][:30])
            c.drawString(3.5*inch, y, str(item['quantity']))
            c.drawString(4.5*inch, y, f"${item['unit_price']:.2f}")
            line_total = item['quantity'] * item['unit_price']
            c.drawString(6*inch, y, f"${line_total:.2f}")
            total += line_total
            y -= 0.3*inch

        # Total
        y -= 0.2*inch
        c.line(5*inch, y, 7*inch, y)
        y -= 0.3*inch

        c.setFont("Helvetica-Bold", 14)
        c.drawString(5*inch, y, "TOTAL:")
        c.drawString(6*inch, y, f"${total:.2f}")

        c.save()
        print(f"✅ Generated PO: {output_path.name}")
        return total

    def generate_sample_data(self):
        """Generate sample invoices and POs for testing"""
        print("\n" + "="*70)
        print("Generating Sample Invoice and PO Data")
        print("="*70 + "\n")

        # Sample data sets
        vendors = [
            "ABC Electronics Ltd",
            "Global Office Supplies Inc",
            "Tech Solutions Corp"
        ]

        items_catalog = [
            {"description": "Laptop Computer - Model X1", "unit_price": 1200.00},
            {"description": "Wireless Mouse", "unit_price": 25.00},
            {"description": "USB-C Cable (2m)", "unit_price": 15.00},
            {"description": "Office Chair - Ergonomic", "unit_price": 350.00},
            {"description": "24-inch Monitor", "unit_price": 280.00},
            {"description": "Keyboard - Mechanical", "unit_price": 120.00},
            {"description": "Desk Lamp - LED", "unit_price": 45.00},
            {"description": "Paper Shredder", "unit_price": 85.00},
            {"description": "Filing Cabinet - 4 Drawer", "unit_price": 220.00},
            {"description": "Printer Paper - 500 sheets", "unit_price": 12.00},
        ]

        # Generate 3 matched invoice-PO pairs
        for i in range(1, 4):
            vendor = vendors[i-1]

            # Select random items
            selected_items = random.sample(items_catalog, random.randint(3, 5))
            items = []
            for item in selected_items:
                items.append({
                    'description': item['description'],
                    'quantity': random.randint(1, 10),
                    'unit_price': item['unit_price']
                })

            # Generate matching invoice and PO
            inv_num = f"INV-2025-{1000+i}"
            po_num = f"PO-2025-{2000+i}"

            inv_path = self.invoice_dir / f"invoice_{i}.pdf"
            po_path = self.po_dir / f"po_{i}.pdf"

            self.generate_invoice_pdf(inv_num, vendor, items, inv_path)
            self.generate_po_pdf(po_num, vendor, items, po_path)

        # Generate 1 invoice with discrepancy (different quantity)
        vendor = "ABC Electronics Ltd"
        items = [
            {'description': 'Laptop Computer - Model X1', 'quantity': 5, 'unit_price': 1200.00},
            {'description': 'Wireless Mouse', 'quantity': 10, 'unit_price': 25.00},
        ]

        items_discrepancy = [
            {'description': 'Laptop Computer - Model X1', 'quantity': 3, 'unit_price': 1200.00},  # Different qty
            {'description': 'Wireless Mouse', 'quantity': 10, 'unit_price': 25.00},
        ]

        inv_path = self.invoice_dir / "invoice_4_discrepancy.pdf"
        po_path = self.po_dir / "po_4_discrepancy.pdf"

        self.generate_invoice_pdf("INV-2025-1004", vendor, items, inv_path)
        self.generate_po_pdf("PO-2025-2004", vendor, items_discrepancy, po_path)

        print("\n" + "="*70)
        print("✅ Sample data generation complete!")
        print("="*70)
        print(f"\nGenerated files:")
        print(f"  - Invoices: {len(list(self.invoice_dir.glob('*.pdf')))} PDFs in {self.invoice_dir}")
        print(f"  - POs: {len(list(self.po_dir.glob('*.pdf')))} PDFs in {self.po_dir}")
        print(f"\nYou can now run: python main.py")

if __name__ == "__main__":
    generator = SampleDataGenerator()
    generator.generate_sample_data()
