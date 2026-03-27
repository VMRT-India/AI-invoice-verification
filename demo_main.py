"""
DEMO VERSION - Invoice-PO Verification System (No Database Required)
Simplified version for testing without database
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
from modules.ocr_extractor import OCRExtractor
from modules.ai_processor import AIProcessor
from modules.matcher import InvoicePOMatcher
from modules.validator import DataValidator
from modules.csv_exporter import CSVExporter
import config

class SimplifiedVerificationSystem:
    def __init__(self):
        """Initialize the verification system (no database)"""
        print(f"{Fore.CYAN}{'='*80}")
        print(f"{Fore.CYAN}AI-Powered Invoice & Purchase Order Verification System (DEMO)")
        print(f"{Fore.CYAN}{'='*80}\n")

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

        # Storage for processed data (in-memory instead of database)
        self.processed_invoices = []
        self.processed_pos = []

    def process_invoice(self, invoice_path):
        """Process a single invoice"""
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

            if validation['warnings']:
                print(f"  {Fore.YELLOW}⚠ Warnings:")
                for warning in validation['warnings']:
                    print(f"    - {warning}")

            print(f"  {Fore.GREEN}✓ Invoice processed successfully")

            # Store in memory
            invoice_data['file_path'] = str(invoice_path)
            invoice_data['extracted_text'] = ocr_result['full_text']
            self.processed_invoices.append(invoice_data)

            return invoice_data

        except Exception as e:
            print(f"  {Fore.RED}✗ Error processing invoice: {e}")
            return None

    def process_purchase_order(self, po_path):
        """Process a single purchase order"""
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

            if validation['warnings']:
                print(f"  {Fore.YELLOW}⚠ Warnings:")
                for warning in validation['warnings']:
                    print(f"    - {warning}")

            print(f"  {Fore.GREEN}✓ PO processed successfully")

            # Store in memory
            po_data['file_path'] = str(po_path)
            po_data['extracted_text'] = ocr_result['full_text']
            self.processed_pos.append(po_data)

            return po_data

        except Exception as e:
            print(f"  {Fore.RED}✗ Error processing PO: {e}")
            return None

    def match_invoice_to_po(self, invoice_data, po_data):
        """Match invoice against purchase order"""
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
                for disc in discrepancies[:5]:
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

    def run_batch_processing(self):
        """Process all invoices and POs"""
        print(f"\n{Fore.CYAN}{'='*80}")
        print(f"{Fore.CYAN}Starting Batch Processing")
        print(f"{Fore.CYAN}{'='*80}\n")

        # Get all files
        invoice_files = list(config.INVOICE_DIR.glob('*.pdf')) + \
                       list(config.INVOICE_DIR.glob('*.jpg')) + \
                       list(config.INVOICE_DIR.glob('*.png'))

        po_files = list(config.PO_DIR.glob('*.pdf')) + \
                  list(config.PO_DIR.glob('*.jpg')) + \
                  list(config.PO_DIR.glob('*.png'))

        if not invoice_files and not po_files:
            print(f"{Fore.RED}✗ No files found!")
            print(f"{Fore.YELLOW}\nTo generate sample data, run:")
            print(f"  pip install reportlab")
            print(f"  python generate_sample_data.py")
            return

        print(f"{Fore.YELLOW}Found {len(invoice_files)} invoices and {len(po_files)} purchase orders\n")

        # Process invoices
        print(f"{Fore.CYAN}Processing Invoices:")
        for inv_file in invoice_files:
            self.process_invoice(inv_file)

        # Process POs
        print(f"\n{Fore.CYAN}Processing Purchase Orders:")
        for po_file in po_files:
            self.process_purchase_order(po_file)

        print(f"\n{Fore.GREEN}✓ Processing complete:")
        print(f"  - Successfully processed {len(self.processed_invoices)} invoices")
        print(f"  - Successfully processed {len(self.processed_pos)} purchase orders")

        # Match invoices to POs
        if self.processed_invoices and self.processed_pos:
            print(f"\n{Fore.CYAN}{'='*80}")
            print(f"{Fore.CYAN}Matching Invoices to Purchase Orders")
            print(f"{Fore.CYAN}{'='*80}")

            match_results = []
            for inv_data in self.processed_invoices:
                from fuzzywuzzy import fuzz

                best_po = None
                best_score = 0

                for po_data in self.processed_pos:
                    score = fuzz.ratio(
                        inv_data.get('vendor_name', '').lower(),
                        po_data.get('vendor_name', '').lower()
                    )

                    if score > best_score:
                        best_score = score
                        best_po = po_data

                if best_po and best_score >= config.FUZZY_MATCH_THRESHOLD:
                    match_result = self.match_invoice_to_po(inv_data, best_po)
                    if match_result:
                        match_results.append(match_result)
                else:
                    print(f"\n{Fore.YELLOW}⚠ No matching PO found for Invoice #{inv_data.get('invoice_number')}")

            # Export results
            if match_results:
                print(f"\n{Fore.CYAN}{'='*80}")
                print(f"{Fore.CYAN}Exporting Results")
                print(f"{Fore.CYAN}{'='*80}\n")

                match_csv = self.csv_exporter.export_match_results(match_results)
                print(f"{Fore.GREEN}✓ Match results exported to: {match_csv}")

                disc_csv = self.csv_exporter.export_discrepancies(match_results)
                if disc_csv:
                    print(f"{Fore.GREEN}✓ Discrepancies exported to: {disc_csv}")

                inv_csv = self.csv_exporter.export_invoice_data(self.processed_invoices)
                print(f"{Fore.GREEN}✓ Invoice data exported to: {inv_csv}")

        print(f"\n{Fore.CYAN}{'='*80}")
        print(f"{Fore.GREEN}Batch Processing Complete!")
        print(f"{Fore.CYAN}{'='*80}\n")

def main():
    """Main entry point"""
    print(f"\n{Fore.GREEN}Starting Invoice-PO Verification System (DEMO)...\n")

    system = SimplifiedVerificationSystem()
    system.run_batch_processing()

if __name__ == '__main__':
    main()
