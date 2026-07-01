import logging
logger = logging.getLogger(__name__)

class OCRProcessor:
    def extract_text(self, image_path: str) -> str:
        try:
            import pytesseract
            from PIL import Image
            return pytesseract.image_to_string(Image.open(image_path), lang="tur+eng").strip()
        except ImportError:
            return ""
        except Exception as e:
            logger.error(f"OCR error: {e}")
            return ""
