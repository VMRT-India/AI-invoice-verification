"""
AI-powered document processing using Google Gemini
"""
import google.generativeai as genai
import json
import re
from datetime import datetime
import config

class AIProcessor:
    def __init__(self):
        """Initialize Gemini AI"""
        genai.configure(api_key=config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(config.AI_MODEL)

    def extract_invoice_data(self, text):
        """
        Extract structured data from invoice text using AI
        """
        prompt = f"""
You are an expert at extracting information from invoices. 
Extract the following information from the invoice text below and return it as a JSON object.

Required fields:
- invoice_number: The invoice number
- vendor_name: The vendor/supplier name
- invoice_date: The invoice date (format: YYYY-MM-DD)
- total_amount: The total amount (number only)
- subtotal: The subtotal before tax (number only)
- tax_amount: The tax amount (number only)
- currency: The currency code (e.g., USD, EUR, INR)
- line_items: Array of items with fields:
  - item_description: Description of the item
  - quantity: Quantity ordered (number only)
  - unit_price: Price per unit (number only)
  - line_total: Total for this line (number only)
  - item_code: Product/item code if available

Invoice Text:
{text}

Return ONLY a valid JSON object, no additional text.
"""

        try:
            response = self.model.generate_content(
                prompt,
                generation_config={
                    'temperature': config.AI_TEMPERATURE,
                    'max_output_tokens': config.AI_MAX_TOKENS,
                }
            )

            # Extract JSON from response
            response_text = response.text.strip()

            # Remove markdown code blocks if present
            response_text = re.sub(r'^```json\s*', '', response_text)
            response_text = re.sub(r'^```\s*', '', response_text)
            response_text = re.sub(r'\s*```$', '', response_text)

            # Parse JSON
            data = json.loads(response_text)

            # Validate and clean data
            data = self._validate_invoice_data(data)

            return {
                'success': True,
                'data': data
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'data': None
            }

    def extract_po_data(self, text):
        """
        Extract structured data from purchase order text using AI
        """
        prompt = f"""
You are an expert at extracting information from purchase orders. 
Extract the following information from the purchase order text below and return it as a JSON object.

Required fields:
- po_number: The purchase order number
- vendor_name: The vendor/supplier name
- po_date: The purchase order date (format: YYYY-MM-DD)
- total_amount: The total amount (number only)
- currency: The currency code (e.g., USD, EUR, INR)
- line_items: Array of items with fields:
  - item_description: Description of the item
  - quantity: Quantity ordered (number only)
  - unit_price: Price per unit (number only)
  - line_total: Total for this line (number only)
  - item_code: Product/item code if available

Purchase Order Text:
{text}

Return ONLY a valid JSON object, no additional text.
"""

        try:
            response = self.model.generate_content(
                prompt,
                generation_config={
                    'temperature': config.AI_TEMPERATURE,
                    'max_output_tokens': config.AI_MAX_TOKENS,
                }
            )

            # Extract JSON from response
            response_text = response.text.strip()

            # Remove markdown code blocks if present
            response_text = re.sub(r'^```json\s*', '', response_text)
            response_text = re.sub(r'^```\s*', '', response_text)
            response_text = re.sub(r'\s*```$', '', response_text)

            # Parse JSON
            data = json.loads(response_text)

            # Validate and clean data
            data = self._validate_po_data(data)

            return {
                'success': True,
                'data': data
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'data': None
            }

    def _validate_invoice_data(self, data):
        """Validate and clean invoice data"""
        # Ensure required fields exist
        required_fields = ['invoice_number', 'vendor_name', 'invoice_date', 'total_amount']
        for field in required_fields:
            if field not in data:
                data[field] = 'N/A' if field != 'total_amount' else 0.0

        # Clean numeric fields
        numeric_fields = ['total_amount', 'subtotal', 'tax_amount']
        for field in numeric_fields:
            if field in data:
                data[field] = self._clean_number(data[field])

        # Clean line items
        if 'line_items' in data and isinstance(data['line_items'], list):
            cleaned_items = []
            for item in data['line_items']:
                cleaned_item = {
                    'item_description': item.get('item_description', 'N/A'),
                    'quantity': self._clean_number(item.get('quantity', 0)),
                    'unit_price': self._clean_number(item.get('unit_price', 0)),
                    'line_total': self._clean_number(item.get('line_total', 0)),
                    'item_code': item.get('item_code', '')
                }
                cleaned_items.append(cleaned_item)
            data['line_items'] = cleaned_items

        return data

    def _validate_po_data(self, data):
        """Validate and clean PO data"""
        # Ensure required fields exist
        required_fields = ['po_number', 'vendor_name', 'po_date', 'total_amount']
        for field in required_fields:
            if field not in data:
                data[field] = 'N/A' if field != 'total_amount' else 0.0

        # Clean numeric fields
        numeric_fields = ['total_amount']
        for field in numeric_fields:
            if field in data:
                data[field] = self._clean_number(data[field])

        # Clean line items
        if 'line_items' in data and isinstance(data['line_items'], list):
            cleaned_items = []
            for item in data['line_items']:
                cleaned_item = {
                    'item_description': item.get('item_description', 'N/A'),
                    'quantity': self._clean_number(item.get('quantity', 0)),
                    'unit_price': self._clean_number(item.get('unit_price', 0)),
                    'line_total': self._clean_number(item.get('line_total', 0)),
                    'item_code': item.get('item_code', '')
                }
                cleaned_items.append(cleaned_item)
            data['line_items'] = cleaned_items

        return data

    @staticmethod
    def _clean_number(value):
        """Clean and convert number strings to float"""
        if isinstance(value, (int, float)):
            return float(value)

        if isinstance(value, str):
            # Remove currency symbols, commas, and whitespace
            cleaned = re.sub(r'[^\d.-]', '', value)
            try:
                return float(cleaned)
            except:
                return 0.0

        return 0.0
