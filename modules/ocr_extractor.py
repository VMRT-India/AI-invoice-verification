"""
OCR extraction using PaddleOCR
"""
from paddleocr import PaddleOCR
import cv2
import re
from pathlib import Path
import config
from utils.image_preprocessing import ImagePreprocessor

class OCRExtractor:
    def __init__(self):
        """Initialize PaddleOCR"""
        # Fixed: Removed use_gpu parameter (deprecated in newer PaddleOCR versions)
        # GPU usage is now controlled by PaddlePaddle backend configuration
        self.ocr = PaddleOCR(
            use_angle_cls=True,
            lang=config.OCR_LANG,
            show_log=False
        )
        self.preprocessor = ImagePreprocessor()

    def extract_text(self, image_path):
        """
        Extract text from image using PaddleOCR
        Returns: raw text and structured OCR results
        """
        try:
            # Preprocess image
            preprocessed = self.preprocessor.preprocess_image(image_path)

            # Run OCR
            result = self.ocr.ocr(preprocessed, cls=True)

            # Extract text and bounding boxes
            extracted_data = []
            full_text = []

            if result and result[0]:
                for line in result[0]:
                    bbox = line[0]  # Bounding box coordinates
                    text = line[1][0]  # Text content
                    confidence = line[1][1]  # Confidence score

                    extracted_data.append({
                        'text': text,
                        'bbox': bbox,
                        'confidence': confidence
                    })
                    full_text.append(text)

            return {
                'full_text': ' '.join(full_text),
                'structured_data': extracted_data,
                'success': True
            }

        except Exception as e:
            return {
                'full_text': '',
                'structured_data': [],
                'success': False,
                'error': str(e)
            }

    def extract_with_layout(self, image_path):
        """
        Extract text preserving layout structure
        Groups text by spatial proximity
        """
        result = self.extract_text(image_path)

        if not result['success']:
            return result

        # Group by Y-coordinate (lines)
        lines = {}
        for item in result['structured_data']:
            bbox = item['bbox']
            y_coord = (bbox[0][1] + bbox[2][1]) / 2  # Middle Y coordinate
            y_key = int(y_coord / 20) * 20  # Group by 20-pixel bands

            if y_key not in lines:
                lines[y_key] = []
            lines[y_key].append(item)

        # Sort each line by X-coordinate
        structured_lines = []
        for y_key in sorted(lines.keys()):
            line_items = sorted(lines[y_key], key=lambda x: x['bbox'][0][0])
            line_text = ' '.join([item['text'] for item in line_items])
            structured_lines.append(line_text)

        result['structured_lines'] = structured_lines
        return result
