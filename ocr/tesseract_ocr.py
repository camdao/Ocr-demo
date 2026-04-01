import pytesseract

class TesseractOCR:
    def __init__(self, lang='vie', config='--psm 6'):
        self.lang = lang
        self.config = config
    
    def read_image(self, image):
        try:
            return pytesseract.image_to_string(
                image, 
                lang=self.lang, 
                config=self.config
            )
        except pytesseract.TesseractNotFoundError:
            print("Tesseract OCR not installed")
            raise
        except Exception as e:
            print(f"Tesseract OCR error: {e}")
            raise
