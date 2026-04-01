import os

# Stabilize Paddle runtime on some Windows CPU setups.
os.environ.setdefault("FLAGS_use_mkldnn", "0")
os.environ.setdefault("FLAGS_enable_pir_api", "0")

from paddleocr import PaddleOCR
import numpy as np
from PIL import Image

class PaddleOCREngine:
    def __init__(self, lang='vi', use_angle_cls=True):
        self.lang = lang
        self.use_angle_cls = use_angle_cls
        mapped_lang = self.map_language(lang)

        # Important: disable MKLDNN to avoid OneDNN/PIR runtime crash on some Windows CPU setups.
        try:
            # PaddleOCR >= 3.x style
            self.ocr = PaddleOCR(
                lang=mapped_lang,
                use_textline_orientation=use_angle_cls,
                enable_mkldnn=False,
            )
        except TypeError:
            # Backward compatibility for PaddleOCR 2.x style
            self.ocr = PaddleOCR(
                use_angle_cls=use_angle_cls,
                lang=mapped_lang,
                enable_mkldnn=False,
            )
    
    @staticmethod
    def map_language(lang):
        """Map ngôn ngữ sang format PaddleOCR"""
        lang_map = {
            "vi": "vi",
            "ch": "ch",
            "en": "en",
            "ja": "ja"
        }
        return lang_map.get(lang, "ch")
    
    def read_image(self, image):
        try:
            # Convert PIL Image to numpy array if needed
            if isinstance(image, Image.Image):
                # Convert RGBA to RGB if needed
                if image.mode == 'RGBA':
                    rgb_image = Image.new('RGB', image.size, (255, 255, 255))
                    rgb_image.paste(image, mask=image.split()[3])
                    image = rgb_image
                elif image.mode != 'RGB':
                    image = image.convert('RGB')
                
                image = np.array(image)
            
            # Ensure image is uint8
            if image.dtype != np.uint8:
                image = (image * 255).astype(np.uint8) if image.max() <= 1 else image.astype(np.uint8)
            
            result = self.ocr.ocr(image)
            
            # Extract text from result
            text = ""
            if result and isinstance(result, list) and len(result) > 0:
                # Check if result contains OCRResult objects
                first_item = result[0]
                
                # If it's a dict with 'rec_texts' (new PaddleOCR version)
                if isinstance(first_item, dict) and 'rec_texts' in first_item:
                    rec_texts = first_item['rec_texts']
                    if rec_texts:
                        text = "\n".join(rec_texts)
                # If it's a list of lists (old format: [[bbox], [text, confidence]])
                elif isinstance(first_item, (list, tuple)):
                    for line in result:
                        if line and isinstance(line, list):
                            line_text = []
                            for word_info in line:
                                try:
                                    if isinstance(word_info, (list, tuple)) and len(word_info) >= 2:
                                        text_content = word_info[1]
                                        
                                        if isinstance(text_content, (list, tuple)) and len(text_content) > 0:
                                            line_text.append(str(text_content[0]))
                                        elif isinstance(text_content, str):
                                            line_text.append(text_content)
                                except (IndexError, TypeError, AttributeError):
                                    continue
                            
                            if line_text:
                                text += " ".join(line_text) + "\n"
            
            return text.strip() if text else "Không tìm thấy văn bản"
            
        except Exception as e:
            err_msg = str(e)
            if "ConvertPirAttribute2RuntimeAttribute" in err_msg:
                raise RuntimeError(
                    "PaddleOCR runtime incompatibility on current environment. "
                    "Please switch to Tesseract OCR in sidebar or reinstall compatible Paddle versions."
                ) from e
            raise

