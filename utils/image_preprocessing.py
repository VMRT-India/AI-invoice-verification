"""
Image preprocessing utilities for better OCR accuracy
"""
import cv2
import numpy as np
from PIL import Image


class ImagePreprocessor:
    @staticmethod
    def preprocess_image(image_path):
        """
        Preprocess image for better OCR accuracy
        - Convert to grayscale
        - Apply adaptive thresholding
        - Denoise
        - Deskew
        """
        # Read image
        img = cv2.imread(str(image_path))

        if img is None:
            raise ValueError(f"Unable to read image: {image_path}")

        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Apply denoising
        denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)

        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )

        # Deskew
        deskewed = ImagePreprocessor.deskew(thresh)

        return deskewed

    @staticmethod
    def deskew(image):
        """Deskew image to correct rotation"""
        coords = np.column_stack(np.where(image > 0))
        if len(coords) == 0:
            return image
        angle = cv2.minAreaRect(coords)[-1]

        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle

        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(
            image, M, (w, h),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_REPLICATE
        )

        return rotated

    @staticmethod
    def enhance_contrast(image):
        """Enhance image contrast"""
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(image)
        return enhanced
