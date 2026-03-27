# AI-Powered Invoice & Purchase Order Verification System

An intelligent automation system that extracts, validates, and matches invoices against purchase orders using OCR and Google Gemini AI — detecting discrepancies at both the header and line-item level.

---

## What It Does

In most organizations, finance teams manually compare invoices against purchase orders to catch errors — wrong prices, missing items, vendor mismatches. This system automates that process end-to-end:

1. Takes invoice and PO documents (PDF, JPG, PNG)
2. Extracts text using OCR (PaddleOCR)
3. Converts raw text into structured JSON using Google Gemini AI
4. Validates the data against business rules
5. Matches invoices to POs and calculates a match score
6. Flags discrepancies with severity levels
7. Exports results to CSV reports

---

## Tech Stack

| Technology | Purpose |
|---|---|
| Python 3 | Core language |
| PaddleOCR | Text extraction from documents |
| Google Gemini API (`gemini-1.5-flash`) | AI-powered structured data extraction |
| FuzzyWuzzy | Fuzzy string matching for vendor names |
| SQLAlchemy + SQLite | Persistent storage of invoices, POs, and match results |
| OpenCV + Pillow | Image preprocessing (denoising, deskewing, thresholding) |
| Pandas | CSV report generation |
| Colorama + TQDM | Colored terminal output and progress bars |

---

## Project Structure

```
AI-invoice-verification/
├── main.py                    # Entry point (full version with database)
├── demo_main.py               # Simplified version (in-memory, no DB)
├── config.py                  # All settings and thresholds
├── generate_sample_data.py    # Script to generate test PDFs
│
├── modules/
│   ├── ocr_extractor.py       # PaddleOCR text extraction with layout preservation
│   ├── ai_processor.py        # Google Gemini integration for JSON extraction
│   ├── matcher.py             # Invoice-PO matching and discrepancy detection
│   ├── validator.py           # Business rule validation
│   ├── csv_exporter.py        # CSV report export
│   └── email_processor.py    # Gmail IMAP integration (bonus feature)
│
├── models/
│   └── database_models.py    # SQLAlchemy ORM models
│
├── utils/
│   └── image_preprocessing.py # Image cleanup for better OCR accuracy
│
└── data/
    ├── invoices/              # Input invoice files
    ├── purchase_orders/       # Input PO files
    └── output/                # Generated CSV reports
```

---

## How It Works

### Processing Pipeline (per document)

**Step 1 — Image Preprocessing**
Before OCR, the image is cleaned up:
- Grayscale conversion
- Denoising (`fastNlMeansDenoising`)
- Adaptive thresholding (handles uneven lighting)
- Deskewing (corrects rotation using `minAreaRect`)

**Step 2 — OCR Extraction**
PaddleOCR reads text with layout awareness. Text is grouped by Y-coordinate in 20-pixel bands to reconstruct the row structure of the document (e.g., keeping "Item | Qty | Price" as one line).

**Step 3 — AI Extraction**
The raw OCR text is sent to Google Gemini with a structured prompt. The AI returns a clean JSON object with fields like `invoice_number`, `vendor_name`, `total_amount`, `line_items`, etc. Temperature is set to `0.1` for consistent, deterministic output.

**Step 4 — Validation**
Business rules are checked:
- Required fields present
- Total amount > 0
- `subtotal + tax == total` (within 1 cent)
- Date sanity checks (not future-dated, not too old)
- Line item math: `quantity × unit_price == line_total`

**Step 5 — Matching**
Each invoice is matched against its best-candidate PO using vendor fuzzy matching. The match score is calculated as:

| Check | Max Score | Threshold |
|---|---|---|
| Vendor name (fuzzy) | 20 pts | ≥ 85% similarity |
| Total amount | 30 pts | ≤ 5% difference |
| Line items (qty + price) | 50 pts | ≤ 2% qty, ≤ 5% price |

**Match Status:**
- `matched` — score ≥ 90 → Ready for approval
- `partial_match` — score 70–89 → Needs review
- `mismatch` — score < 70 → Rejected

---

## Setup

### Prerequisites
- Python 3.8+
- Google Gemini API key ([get one here](https://makersuite.google.com/app/apikey))

### Installation

```bash
git clone https://github.com/VMRT-India/AI-invoice-verification.git
cd AI-invoice-verification

pip install paddleocr paddlepaddle opencv-python pillow
pip install google-generativeai fuzzywuzzy python-Levenshtein
pip install sqlalchemy pandas colorama tqdm reportlab
```

### Environment Variables

```bash
export GEMINI_API_KEY="your-gemini-api-key"

# Optional: for email integration
export EMAIL_USERNAME="your-email@gmail.com"
export EMAIL_PASSWORD="your-app-password"
```

### Generate Sample Data

```bash
python generate_sample_data.py
```

---

## Usage

```bash
# Batch mode — process all files in data/invoices/ and data/purchase_orders/
python main.py

# Single pair
python main.py single data/invoices/invoice_1.pdf data/purchase_orders/po_1.pdf

# Email mode — fetch invoices from Gmail automatically
python main.py email

# Demo mode (no database required)
python demo_main.py
```

---

## Output

Three CSV files are generated in `data/output/`:

| File | Contents |
|---|---|
| `match_results_<timestamp>.csv` | Summary: invoice #, PO #, match status, score, amount difference |
| `discrepancies_<timestamp>.csv` | Detailed discrepancies with field, severity, and values |
| `invoices_<timestamp>.csv` | All extracted invoice data |

---

## Configuration

All thresholds are configurable in `config.py`:

```python
FUZZY_MATCH_THRESHOLD = 85   # Vendor name similarity required (0-100)
QUANTITY_TOLERANCE    = 0.02 # 2% quantity variance allowed
PRICE_TOLERANCE       = 0.05 # 5% unit price variance allowed
AMOUNT_TOLERANCE      = 0.05 # 5% total amount variance allowed
AI_MODEL              = "gemini-1.5-flash"
AI_TEMPERATURE        = 0.1  # Low = consistent extraction
```

---

## Database Schema

| Table | Description |
|---|---|
| `invoices` | Processed invoice records with extracted text |
| `purchase_orders` | Processed PO records |
| `invoice_line_items` | Line-by-line items from invoices |
| `po_line_items` | Line-by-line items from POs |
| `match_results` | Match outcomes with score and discrepancy JSON |

---

## License

MIT License
