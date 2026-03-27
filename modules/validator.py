"""
Data validation and business rule checking
"""
from datetime import datetime, timedelta
import re


class DataValidator:
    @staticmethod
    def validate_invoice(invoice_data):
        """Validate invoice data and check business rules"""
        errors = []
        warnings = []

        # Check required fields
        required_fields = ['invoice_number', 'vendor_name', 'total_amount', 'invoice_date']
        for field in required_fields:
            if not invoice_data.get(field) or invoice_data[field] == 'N/A':
                errors.append(f'Missing required field: {field}')

        # Validate invoice number format
        inv_num = invoice_data.get('invoice_number', '')
        if inv_num and inv_num != 'N/A':
            if not re.match(r'^[A-Z0-9-]+$', inv_num, re.IGNORECASE):
                warnings.append(f'Invalid invoice number format: {inv_num}')

        # Validate amounts
        total = invoice_data.get('total_amount', 0)
        subtotal = invoice_data.get('subtotal', 0)
        tax = invoice_data.get('tax_amount', 0)

        if total <= 0:
            errors.append('Total amount must be greater than 0')

        if subtotal > 0 and tax >= 0:
            expected_total = subtotal + tax
            if abs(total - expected_total) > 0.01:  # Allow 1 cent rounding
                warnings.append(f'Total amount mismatch: Expected {expected_total}, got {total}')

        # Validate date
        try:
            inv_date = datetime.strptime(invoice_data.get('invoice_date', ''), '%Y-%m-%d')

            # Check if date is not too far in the past or future
            today = datetime.now()
            if inv_date > today + timedelta(days=30):
                warnings.append('Invoice date is in the future')
            if inv_date < today - timedelta(days=365):
                warnings.append('Invoice date is more than 1 year old')
        except:
            errors.append('Invalid invoice date format (should be YYYY-MM-DD)')

        # Validate line items
        line_items = invoice_data.get('line_items', [])
        if not line_items:
            errors.append('No line items found')
        else:
            calculated_total = 0
            for idx, item in enumerate(line_items):
                qty = item.get('quantity', 0)
                price = item.get('unit_price', 0)
                line_total = item.get('line_total', 0)

                if qty <= 0:
                    errors.append(f'Line item {idx + 1}: Invalid quantity')
                if price <= 0:
                    errors.append(f'Line item {idx + 1}: Invalid unit price')

                expected_line_total = qty * price
                if abs(line_total - expected_line_total) > 0.01:
                    warnings.append(f'Line item {idx + 1}: Line total mismatch')

                calculated_total += line_total

            # Check if line items sum to subtotal
            if subtotal > 0 and abs(calculated_total - subtotal) > 0.01:
                warnings.append(f'Line items total ({calculated_total}) does not match subtotal ({subtotal})')

        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }

    @staticmethod
    def validate_po(po_data):
        """Validate purchase order data"""
        errors = []
        warnings = []

        # Check required fields
        required_fields = ['po_number', 'vendor_name', 'total_amount', 'po_date']
        for field in required_fields:
            if not po_data.get(field) or po_data[field] == 'N/A':
                errors.append(f'Missing required field: {field}')

        # Validate PO number format
        po_num = po_data.get('po_number', '')
        if po_num and po_num != 'N/A':
            if not re.match(r'^[A-Z0-9-]+$', po_num, re.IGNORECASE):
                warnings.append(f'Invalid PO number format: {po_num}')

        # Validate amounts
        total = po_data.get('total_amount', 0)
        if total <= 0:
            errors.append('Total amount must be greater than 0')

        # Validate date
        try:
            po_date = datetime.strptime(po_data.get('po_date', ''), '%Y-%m-%d')

            today = datetime.now()
            if po_date > today + timedelta(days=30):
                warnings.append('PO date is in the future')
            if po_date < today - timedelta(days=730):
                warnings.append('PO date is more than 2 years old')
        except:
            errors.append('Invalid PO date format (should be YYYY-MM-DD)')

        # Validate line items
        line_items = po_data.get('line_items', [])
        if not line_items:
            errors.append('No line items found')
        else:
            calculated_total = 0
            for idx, item in enumerate(line_items):
                qty = item.get('quantity', 0)
                price = item.get('unit_price', 0)
                line_total = item.get('line_total', 0)

                if qty <= 0:
                    errors.append(f'Line item {idx + 1}: Invalid quantity')
                if price <= 0:
                    errors.append(f'Line item {idx + 1}: Invalid unit price')

                calculated_total += line_total

        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
