"""
Invoice-PO matching and discrepancy detection
"""
from fuzzywuzzy import fuzz
import config
import json


class InvoicePOMatcher:
    def __init__(self):
        self.fuzzy_threshold = config.FUZZY_MATCH_THRESHOLD
        self.qty_tolerance = config.QUANTITY_TOLERANCE
        self.price_tolerance = config.PRICE_TOLERANCE
        self.amount_tolerance = config.AMOUNT_TOLERANCE

    def match_documents(self, invoice_data, po_data):
        """
        Match invoice against purchase order
        Returns match result with score and discrepancies
        """
        discrepancies = []
        match_score = 0
        total_checks = 0

        # 1. Vendor name matching (fuzzy)
        vendor_match_score = fuzz.ratio(
            invoice_data.get('vendor_name', '').lower(),
            po_data.get('vendor_name', '').lower()
        )
        vendor_match = vendor_match_score >= self.fuzzy_threshold

        if vendor_match:
            match_score += 20
        else:
            discrepancies.append({
                'field': 'vendor_name',
                'invoice_value': invoice_data.get('vendor_name'),
                'po_value': po_data.get('vendor_name'),
                'severity': 'high',
                'message': f'Vendor name mismatch (similarity: {vendor_match_score}%)'
            })
        total_checks += 1

        # 2. Total amount matching
        inv_total = float(invoice_data.get('total_amount', 0))
        po_total = float(po_data.get('total_amount', 0))

        amount_diff = abs(inv_total - po_total)
        amount_diff_percent = (amount_diff / po_total * 100) if po_total > 0 else 100
        amount_match = amount_diff_percent <= (self.amount_tolerance * 100)

        if amount_match:
            match_score += 30
        else:
            discrepancies.append({
                'field': 'total_amount',
                'invoice_value': inv_total,
                'po_value': po_total,
                'difference': amount_diff,
                'difference_percent': round(amount_diff_percent, 2),
                'severity': 'high' if amount_diff_percent > 10 else 'medium',
                'message': f'Total amount mismatch: Difference of {amount_diff} ({amount_diff_percent:.2f}%)'
            })
        total_checks += 1

        # 3. Line item matching
        line_item_results = self._match_line_items(
            invoice_data.get('line_items', []),
            po_data.get('line_items', [])
        )

        if line_item_results['all_matched']:
            match_score += 50
        else:
            match_score += line_item_results['match_percentage'] * 0.5
            discrepancies.extend(line_item_results['discrepancies'])

        # Calculate final match status
        if match_score >= 90:
            match_status = 'matched'
        elif match_score >= 70:
            match_status = 'partial_match'
        else:
            match_status = 'mismatch'

        return {
            'match_status': match_status,
            'match_score': round(match_score, 2),
            'vendor_match': vendor_match,
            'amount_match': amount_match,
            'line_items_match': line_item_results['all_matched'],
            'discrepancies': discrepancies,
            'summary': self._generate_summary(match_status, discrepancies)
        }

    def _match_line_items(self, invoice_items, po_items):
        """Match line items between invoice and PO"""
        if not invoice_items or not po_items:
            return {
                'all_matched': False,
                'match_percentage': 0,
                'discrepancies': [{
                    'field': 'line_items',
                    'severity': 'high',
                    'message': 'Missing line items in invoice or PO'
                }]
            }

        discrepancies = []
        matched_count = 0

        for inv_item in invoice_items:
            # Find best matching PO item
            best_match = None
            best_score = 0

            for po_item in po_items:
                # Match by item code if available
                if inv_item.get('item_code') and po_item.get('item_code'):
                    if inv_item['item_code'] == po_item['item_code']:
                        best_match = po_item
                        best_score = 100
                        break

                # Otherwise, fuzzy match by description
                score = fuzz.ratio(
                    inv_item.get('item_description', '').lower(),
                    po_item.get('item_description', '').lower()
                )

                if score > best_score:
                    best_score = score
                    best_match = po_item

            # Check if match is good enough
            if best_match and best_score >= self.fuzzy_threshold:
                # Check quantity
                inv_qty = float(inv_item.get('quantity', 0))
                po_qty = float(best_match.get('quantity', 0))
                qty_diff = abs(inv_qty - po_qty)
                qty_diff_percent = (qty_diff / po_qty * 100) if po_qty > 0 else 100

                if qty_diff_percent > (self.qty_tolerance * 100):
                    discrepancies.append({
                        'field': 'line_item_quantity',
                        'item': inv_item.get('item_description'),
                        'invoice_value': inv_qty,
                        'po_value': po_qty,
                        'difference': qty_diff,
                        'severity': 'medium',
                        'message': f'Quantity mismatch for {inv_item.get("item_description")}: Invoice={inv_qty}, PO={po_qty}'
                    })

                # Check unit price
                inv_price = float(inv_item.get('unit_price', 0))
                po_price = float(best_match.get('unit_price', 0))
                price_diff = abs(inv_price - po_price)
                price_diff_percent = (price_diff / po_price * 100) if po_price > 0 else 100

                if price_diff_percent > (self.price_tolerance * 100):
                    discrepancies.append({
                        'field': 'line_item_price',
                        'item': inv_item.get('item_description'),
                        'invoice_value': inv_price,
                        'po_value': po_price,
                        'difference': price_diff,
                        'severity': 'medium',
                        'message': f'Price mismatch for {inv_item.get("item_description")}: Invoice={inv_price}, PO={po_price}'
                    })

                if qty_diff_percent <= (self.qty_tolerance * 100) and price_diff_percent <= (
                        self.price_tolerance * 100):
                    matched_count += 1
            else:
                discrepancies.append({
                    'field': 'line_item_not_found',
                    'item': inv_item.get('item_description'),
                    'severity': 'high',
                    'message': f'Item not found in PO: {inv_item.get("item_description")}'
                })

        match_percentage = (matched_count / len(invoice_items) * 100) if invoice_items else 0

        return {
            'all_matched': matched_count == len(invoice_items) and len(discrepancies) == 0,
            'match_percentage': match_percentage,
            'matched_count': matched_count,
            'total_items': len(invoice_items),
            'discrepancies': discrepancies
        }

    @staticmethod
    def _generate_summary(match_status, discrepancies):
        """Generate human-readable summary"""
        if match_status == 'matched':
            return 'Invoice matches PO completely. Ready for approval.'

        high_severity = [d for d in discrepancies if d.get('severity') == 'high']
        medium_severity = [d for d in discrepancies if d.get('severity') == 'medium']

        summary = f'Found {len(discrepancies)} discrepancies: '
        summary += f'{len(high_severity)} high severity, {len(medium_severity)} medium severity. '
        summary += 'Review required before approval.'

        return summary
