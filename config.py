"""
Configuration settings for Invoice-PO Verification System
"""
import os
from pathlib import Path

# Base directory
"""
Configuration settings for Invoice-PO Verification System
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# API Keys (use environment variables in production)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "your-gemini-api-key-here")

# Directory paths
DATA_DIR = BASE_DIR / "data"
INVOICE_DIR = DATA_DIR / "invoices"
PO_DIR = DATA_DIR / "purchase_orders"
OUTPUT_DIR = DATA_DIR / "output"
DATABASE_PATH = DATA_DIR / "database.db"

# Create directories if they don't exist
for directory in [DATA_DIR, INVOICE_DIR, PO_DIR, OUTPUT_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# OCR Settings
OCR_LANG = "en"  # Language for OCR
# Note: GPU usage is auto-detected by PaddlePaddle backend in newer versions

# Matching thresholds
FUZZY_MATCH_THRESHOLD = 85  # For vendor name matching (0-100)
QUANTITY_TOLERANCE = 0.02   # 2% tolerance for quantity
PRICE_TOLERANCE = 0.05      # 5% tolerance for price
AMOUNT_TOLERANCE = 0.05     # 5% tolerance for total amount

# AI Model Settings
AI_MODEL = "gemini-1.5-flash"  # or "gemini-1.5-pro"
AI_TEMPERATURE = 0.1  # Low temperature for consistent extraction
AI_MAX_TOKENS = 2048

# Email Settings (for bonus feature)
EMAIL_SERVER = "imap.gmail.com"
EMAIL_PORT = 993
EMAIL_USERNAME = os.getenv("EMAIL_USERNAME", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")

# CSV Export Settings
CSV_DELIMITER = ","
CSV_ENCODING = "utf-8"
BASE_DIR = Path(__file__).resolve().parent

# API Keys (use environment variables in production)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "your-gemini-api-key-here")

# Directory paths
DATA_DIR = BASE_DIR / "data"
INVOICE_DIR = DATA_DIR / "invoices"
PO_DIR = DATA_DIR / "purchase_orders"
OUTPUT_DIR = DATA_DIR / "output"
DATABASE_PATH = DATA_DIR / "database.db"

# Create directories if they don't exist
for directory in [DATA_DIR, INVOICE_DIR, PO_DIR, OUTPUT_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# OCR Settings
OCR_LANG = "en"  # Language for OCR
OCR_USE_GPU = False  # Set to True if GPU available

# Matching thresholds
FUZZY_MATCH_THRESHOLD = 85  # For vendor name matching (0-100)
QUANTITY_TOLERANCE = 0.02   # 2% tolerance for quantity
PRICE_TOLERANCE = 0.05      # 5% tolerance for price
AMOUNT_TOLERANCE = 0.05     # 5% tolerance for total amount

# AI Model Settings
AI_MODEL = "gemini-1.5-flash"  # or "gemini-1.5-pro"
AI_TEMPERATURE = 0.1  # Low temperature for consistent extraction
AI_MAX_TOKENS = 2048

# Email Settings (for bonus feature)
EMAIL_SERVER = "imap.gmail.com"
EMAIL_PORT = 993
EMAIL_USERNAME = os.getenv("EMAIL_USERNAME", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")

# CSV Export Settings
CSV_DELIMITER = ","
CSV_ENCODING = "utf-8"
