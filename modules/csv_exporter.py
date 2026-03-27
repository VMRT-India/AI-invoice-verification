"""
CSV export functionality for matched invoices and discrepancies
"""
import pandas as pd
from datetime import datetime
import json
import config


class CSVExporter:
    @staticmethod
    def export_match_results(match_results, output_filename=None):
        """
        Export match results to CSV
        """
        if not output_filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_filename = config.OUTPUT_DIR / f'match_results_{timestamp}.csv'

        # Prepare data for export
        rows = []
        for result in match_results:
            row = {
                'Invoice Number': result.get('invoice_number'),
                'PO Number': result.get('po_number'),
                'Vendor Name': result.get('vendor_name'),
                'Match Status': result.get('match_status'),
                'Match Score': result.get('match_score'),
                'Invoice Total': result.get('invoice_total'),
                'PO Total': result.get('po_total'),
                'Amount Difference': result.get('amount_difference'),
                'Discrepancy Count': len(result.get('discrepancies', [])),
                'Summary': result.get('summary'),
                'Processed Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            rows.append(row)

        df = pd.DataFrame(rows)
        df.to_csv(output_filename, index=False, encoding=config.CSV_ENCODING)

        return str(output_filename)

    @staticmethod
    def export_discrepancies(match_results, output_filename=None):
        """
        Export detailed discrepancies to CSV
        """
        if not output_filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_filename = config.OUTPUT_DIR / f'discrepancies_{timestamp}.csv'

        rows = []
        for result in match_results:
            inv_num = result.get('invoice_number')
            po_num = result.get('po_number')

            for disc in result.get('discrepancies', []):
                row = {
                    'Invoice Number': inv_num,
                    'PO Number': po_num,
                    'Field': disc.get('field'),
                    'Severity': disc.get('severity'),
                    'Invoice Value': disc.get('invoice_value', ''),
                    'PO Value': disc.get('po_value', ''),
                    'Difference': disc.get('difference', ''),
                    'Message': disc.get('message'),
                    'Item': disc.get('item', '')
                }
                rows.append(row)

        if rows:
            df = pd.DataFrame(rows)
            df.to_csv(output_filename, index=False, encoding=config.CSV_ENCODING)
            return str(output_filename)

        return None

    @staticmethod
    def export_invoice_data(invoices, output_filename=None):
        """
        Export extracted invoice data to CSV
        """
        if not output_filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_filename = config.OUTPUT_DIR / f'invoices_{timestamp}.csv'

        rows = []
        for inv in invoices:
            row = {
                'Invoice Number': inv.get('invoice_number'),
                'Vendor Name': inv.get('vendor_name'),
                'Invoice Date': inv.get('invoice_date'),
                'Total Amount': inv.get('total_amount'),
                'Subtotal': inv.get('subtotal'),
                'Tax Amount': inv.get('tax_amount'),
                'Currency': inv.get('currency'),
                'Item Count': len(inv.get('line_items', [])),
                'Processing Status': inv.get('processing_status')
            }
            rows.append(row)

        df = pd.DataFrame(rows)
        df.to_csv(output_filename, index=False, encoding=config.CSV_ENCODING)

        return str(output_filename)
