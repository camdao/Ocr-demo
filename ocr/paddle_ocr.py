from paddleocr import PaddleOCR

class PaddleOCREngine:
    def __init__(self, lang='ch', use_angle_cls=True):
        self.lang = lang
        self.use_angle_cls = use_angle_cls
        self.ocr = PaddleOCR(use_angle_cls=use_angle_cls, lang=lang)
    
    def read_image(self, image):
        try:
            result = self.ocr.ocr(image, cls=self.use_angle_cls)
            
            # Extract text from result
            text = ""
            for line in result:
                if line:
                    for word_info in line:
                        text += word_info[1][0] + " "
                    text += "\n"
            
            return text.strip()
        except Exception as e:
            print(f"PaddleOCR error: {e}")
            raise
