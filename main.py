"""
Main application for Invoice-PO Verification System
"""
import sys
from pathlib import Path
from datetime import datetime
import json
from tqdm import tqdm
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Import modules
from models.database_models import init_database, get_session, Invoice, PurchaseOrder, MatchResult
from modules.ocr_extractor import OCRExtractor
from modules.ai_processor import AIProcessor
from modules.matcher import InvoicePOMatcher
from modules.validator import DataValidator
from modules.csv_exporter import CSVExporter
from modules.email_processor import EmailProcessor
import config


class InvoicePOVerificationSystem:
    def __init__(self):
        """Initialize the verification system"""
        print(f"{Fore.CYAN}{'=' * 80}")
        print(f"{Fore.CYAN}AI-Powered Invoice & Purchase Order Verification System")
        print(f"{Fore.CYAN}{'=' * 80}\n")

        # Initialize database
        print(f"{Fore.YELLOW}Initializing database...")
        self.session = init_database()

        # Initialize modules
        print(f"{Fore.YELLOW}Loading OCR engine...")
        self.ocr_extractor = OCRExtractor()

        print(f"{Fore.YELLOW}Loading AI processor...")
        self.ai_processor = AIProcessor()

        print(f"{Fore.YELLOW}Initializing matcher...")
        self.matcher = InvoicePOMatcher()

        print(f"{Fore.YELLOW}Loading validators...")
        self.validator = DataValidator()

        print(f"{Fore.YELLOW}Setting up CSV exporter...")
        self.csv_exporter = CSVExporter()

        print(f"{Fore.GREEN}✓ System initialized successfully!\n")

    def process_invoice(self, invoice_path):
        """
        Process a single invoice
        """
        print(f"\n{Fore.CYAN}Processing invoice: {invoice_path.name}")

        try:
            # Step 1: OCR extraction
            print(f"  {Fore.YELLOW}[1/3] Extracting text with OCR...")
            ocr_result = self.ocr_extractor.extract_with_layout(invoice_path)

            if not ocr_result['success']:
                print(f"  {Fore.RED}✗ OCR extraction failed: {ocr_result.get('error')}")
                return None

            print(f"  {Fore.GREEN}✓ Text extracted successfully")

            # Step 2: AI-powered data extraction
            print(f"  {Fore.YELLOW}[2/3] Extracting structured data with AI...")
            ai_result = self.ai_processor.extract_invoice_data(ocr_result['full_text'])

            if not ai_result['success']:
                print(f"  {Fore.RED}✗ AI extraction failed: {ai_result.get('error')}")
                return None

            invoice_data = ai_result['data']
            print(f"  {Fore.GREEN}✓ Data extracted: Invoice #{invoice_data.get('invoice_number')}")

            # Step 3: Validation
            print(f"  {Fore.YELLOW}[3/3] Validating invoice data...")
            validation = self.validator.validate_invoice(invoice_data)

            if not validation['is_valid']:
                print(f"  {Fore.RED}✗ Validation failed:")
                for error in validation['errors']:
                    print(f"    - {error}")
                return None

            if validation['warnings']:
                print(f"  {Fore.YELLOW}⚠ Warnings:")
                for warning in validation['warnings']:
                    print(f"    - {warning}")

            print(f"  {Fore.GREEN}✓ Invoice validated successfully")

            # Store in database
            invoice_data['file_path'] = str(invoice_path)
            invoice_data['extracted_text'] = ocr_result['full_text']
            invoice_data['processing_status'] = 'processed'

            return invoice_data

        except Exception as e:
            print(f"  {Fore.RED}✗ Error processing invoice: {e}")
            return None

    def process_purchase_order(self, po_path):
        """
        Process a single purchase order
        """
        print(f"\n{Fore.CYAN}Processing PO: {po_path.name}")

        try:
            # Step 1: OCR extraction
            print(f"  {Fore.YELLOW}[1/3] Extracting text with OCR...")
            ocr_result = self.ocr_extractor.extract_with_layout(po_path)

            if not ocr_result['success']:
                print(f"  {Fore.RED}✗ OCR extraction failed: {ocr_result.get('error')}")
                return None

            print(f"  {Fore.GREEN}✓ Text extracted successfully")

            # Step 2: AI-powered data extraction
            print(f"  {Fore.YELLOW}[2/3] Extracting structured data with AI...")
            ai_result = self.ai_processor.extract_po_data(ocr_result['full_text'])

            if not ai_result['success']:
                print(f"  {Fore.RED}✗ AI extraction failed: {ai_result.get('error')}")
                return None

            po_data = ai_result['data']
            print(f"  {Fore.GREEN}✓ Data extracted: PO #{po_data.get('po_number')}")

            # Step 3: Validation
            print(f"  {Fore.YELLOW}[3/3] Validating PO data...")
            validation = self.validator.validate_po(po_data)

            if not validation['is_valid']:
                print(f"  {Fore.RED}✗ Validation failed:")
                for error in validation['errors']:
                    print(f"    - {error}")
                return None

            if validation['warnings']:
                print(f"  {Fore.YELLOW}⚠ Warnings:")
                for warning in validation['warnings']:
                    print(f"    - {warning}")

            print(f"  {Fore.GREEN}✓ PO validated successfully")

            # Store in database
            po_data['file_path'] = str(po_path)
            po_data['extracted_text'] = ocr_result['full_text']
            po_data['processing_status'] = 'processed'

            return po_data

        except Exception as e:
            print(f"  {Fore.RED}✗ Error processing PO: {e}")
            return None

    def match_invoice_to_po(self, invoice_data, po_data):
        """
        Match invoice against purchase order
        """
        print(f"\n{Fore.CYAN}Matching Invoice #{invoice_data.get('invoice_number')} to PO #{po_data.get('po_number')}")

        try:
            match_result = self.matcher.match_documents(invoice_data, po_data)

            # Display results
            status = match_result['match_status']
            score = match_result['match_score']

            if status == 'matched':
                print(f"  {Fore.GREEN}✓ MATCH SUCCESSFUL (Score: {score})")
            elif status == 'partial_match':
                print(f"  {Fore.YELLOW}⚠ PARTIAL MATCH (Score: {score})")
            else:
                print(f"  {Fore.RED}✗ MISMATCH (Score: {score})")

            # Display discrepancies
            discrepancies = match_result['discrepancies']
            if discrepancies:
                print(f"\n  {Fore.YELLOW}Discrepancies found: {len(discrepancies)}")
                for disc in discrepancies[:5]:  # Show first 5
                    severity_color = Fore.RED if disc['severity'] == 'high' else Fore.YELLOW
                    print(f"    {severity_color}[{disc['severity'].upper()}] {disc['message']}")

                if len(discrepancies) > 5:
                    print(f"    ... and {len(discrepancies) - 5} more")

            print(f"\n  {Fore.CYAN}Summary: {match_result['summary']}")

            # Prepare for export
            export_data = {
                'invoice_number': invoice_data.get('invoice_number'),
                'po_number': po_data.get('po_number'),
                'vendor_name': invoice_data.get('vendor_name'),
                'match_status': status,
                'match_score': score,
                'invoice_total': invoice_data.get('total_amount'),
                'po_total': po_data.get('total_amount'),
                'amount_difference': abs(invoice_data.get('total_amount', 0) - po_data.get('total_amount', 0)),
                'discrepancies': discrepancies,
                'summary': match_result['summary']
            }

            return export_data

        except Exception as e:
            print(f"  {Fore.RED}✗ Error during matching: {e}")
            return None

    def process_batch(self):
        """
        Process all invoices and POs in the data directories
        """
        print(f"\n{Fore.CYAN}{'=' * 80}")
        print(f"{Fore.CYAN}Starting Batch Processing")
        print(f"{Fore.CYAN}{'=' * 80}\n")

        # Get all invoice files
        invoice_files = list(config.INVOICE_DIR.glob('*.pdf')) + \
                        list(config.INVOICE_DIR.glob('*.jpg')) + \
                        list(config.INVOICE_DIR.glob('*.png'))

        # Get all PO files
        po_files = list(config.PO_DIR.glob('*.pdf')) + \
                   list(config.PO_DIR.glob('*.jpg')) + \
                   list(config.PO_DIR.glob('*.png'))

        print(f"{Fore.YELLOW}Found {len(invoice_files)} invoices and {len(po_files)} purchase orders\n")

        # Process invoices
        processed_invoices = []
        print(f"{Fore.CYAN}Processing Invoices:")
        for inv_file in tqdm(invoice_files, desc="Invoices"):
            inv_data = self.process_invoice(inv_file)
            if inv_data:
                processed_invoices.append(inv_data)

        # Process POs
        processed_pos = []
        print(f"\n{Fore.CYAN}Processing Purchase Orders:")
        for po_file in tqdm(po_files, desc="POs"):
            po_data = self.process_purchase_order(po_file)
            if po_data:
                processed_pos.append(po_data)

        print(f"\n{Fore.GREEN}✓ Processing complete:")
        print(f"  - Successfully processed {len(processed_invoices)}/{len(invoice_files)} invoices")
        print(f"  - Successfully processed {len(processed_pos)}/{len(po_files)} purchase orders")

        # Match invoices to POs
        print(f"\n{Fore.CYAN}{'=' * 80}")
        print(f"{Fore.CYAN}Matching Invoices to Purchase Orders")
        print(f"{Fore.CYAN}{'=' * 80}\n")

        match_results = []
        for inv_data in processed_invoices:
            # Find matching PO by vendor name
            best_po = None
            best_vendor_score = 0

            for po_data in processed_pos:
                from fuzzywuzzy import fuzz
                score = fuzz.ratio(
                    inv_data.get('vendor_name', '').lower(),
                    po_data.get('vendor_name', '').lower()
                )

                if score > best_vendor_score:
                    best_vendor_score = score
                    best_po = po_data

            if best_po and best_vendor_score >= config.FUZZY_MATCH_THRESHOLD:
                match_result = self.match_invoice_to_po(inv_data, best_po)
                if match_result:
                    match_results.append(match_result)
            else:
                print(f"\n{Fore.YELLOW}⚠ No matching PO found for Invoice #{inv_data.get('invoice_number')}")

        # Export results
        print(f"\n{Fore.CYAN}{'=' * 80}")
        print(f"{Fore.CYAN}Exporting Results")
        print(f"{Fore.CYAN}{'=' * 80}\n")

        if match_results:
            # Export match results
            match_csv = self.csv_exporter.export_match_results(match_results)
            print(f"{Fore.GREEN}✓ Match results exported to: {match_csv}")

            # Export discrepancies
            disc_csv = self.csv_exporter.export_discrepancies(match_results)
            if disc_csv:
                print(f"{Fore.GREEN}✓ Discrepancies exported to: {disc_csv}")

            # Export invoice data
            inv_csv = self.csv_exporter.export_invoice_data(processed_invoices)
            print(f"{Fore.GREEN}✓ Invoice data exported to: {inv_csv}")

        print(f"\n{Fore.CYAN}{'=' * 80}")
        print(f"{Fore.GREEN}Batch Processing Complete!")
        print(f"{Fore.CYAN}{'=' * 80}\n")

        return {
            'invoices_processed': len(processed_invoices),
            'pos_processed': len(processed_pos),
            'matches_found': len(match_results),
            'match_results': match_results
        }

    def process_from_email(self):
        """
        Process invoices from email (Bonus feature)
        """
        print(f"\n{Fore.CYAN}{'=' * 80}")
        print(f"{Fore.CYAN}Processing Invoices from Email")
        print(f"{Fore.CYAN}{'=' * 80}\n")

        email_processor = EmailProcessor()
        invoices = email_processor.fetch_invoice_emails(days=7)

        if not invoices:
            print(f"{Fore.YELLOW}No invoice emails found")
            return

        print(f"{Fore.GREEN}Found {len(invoices)} invoice emails")

        for email_data in invoices:
            print(f"\n{Fore.CYAN}Processing email from {email_data['sender']}")
            print(f"  Subject: {email_data['subject']}")

            for attachment in email_data['attachments']:
                invoice_path = Path(attachment['filepath'])
                self.process_invoice(invoice_path)


def main():
    """Main entry point"""
    print(f"\n{Fore.GREEN}Starting Invoice-PO Verification System...\n")

    # Initialize system
    system = InvoicePOVerificationSystem()

    # Check command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == 'email':
            # Process from email
            system.process_from_email()
        elif command == 'single':
            # Process single invoice and PO
            if len(sys.argv) < 4:
                print(f"{Fore.RED}Usage: python main.py single <invoice_path> <po_path>")
                return

            invoice_path = Path(sys.argv[2])
            po_path = Path(sys.argv[3])

            inv_data = system.process_invoice(invoice_path)
            po_data = system.process_purchase_order(po_path)

            if inv_data and po_data:
                system.match_invoice_to_po(inv_data, po_data)
        else:
            print(f"{Fore.RED}Unknown command: {command}")
            print(f"{Fore.YELLOW}Available commands: batch, email, single")
    else:
        # Default: batch processing
        system.process_batch()


if __name__ == '__main__':
    main()
