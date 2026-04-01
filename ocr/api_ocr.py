import base64
import os
import requests
from PIL import Image
from PIL import ImageOps
import io
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class APILayoutParsingOCR:
    """OCR dùng API layout parsing từ Baidu"""
    
    def __init__(self, api_url=None, token=None):
        self.api_url = api_url or os.getenv("API_URL", "https://20ec2cibw7n8y5m8.aistudio-app.com/layout-parsing")
        self.token = token or os.getenv("API_TOKEN", "")
        self.headers = {"Content-Type": "application/json"}
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"

    @staticmethod
    def _prepare_image_bytes(image: Image.Image) -> bytes:
        # Fix orientation metadata from camera captures before OCR.
        image = ImageOps.exif_transpose(image)

        if image.mode != 'RGB':
            image = image.convert('RGB')

        # Camera images are often very large; downscale to reduce API payload and timeout risk.
        max_side = 1920
        w, h = image.size
        longest = max(w, h)
        if longest > max_side:
            scale = max_side / float(longest)
            new_size = (int(w * scale), int(h * scale))
            image = image.resize(new_size, Image.Resampling.LANCZOS)

        img_bytes = io.BytesIO()
        image.save(img_bytes, format='JPEG', quality=88, optimize=True)
        return img_bytes.getvalue()
    
    def read_image(self, image):
        """Gửi ảnh tới API và nhận diện text"""
        try:
            # Convert PIL Image to bytes
            if isinstance(image, Image.Image):
                prepared = self._prepare_image_bytes(image)
                file_data = base64.b64encode(prepared).decode("ascii")
            else:
                raise ValueError("Input phải là PIL Image")
            
            # Chuẩn bị payload
            payload = {
                "file": file_data,
                "fileType": 1,  # 1 = image, 0 = PDF
                "useDocOrientationClassify": True,
                "useDocUnwarping": True,
                "useChartRecognition": False,
            }
            
            response = requests.post(self.api_url, json=payload, headers=self.headers, timeout=90)
            
            if response.status_code != 200:
                raise Exception(f"API error: {response.status_code} - {response.text[:300]}")
            
            result = response.json()
            
            if "result" not in result:
                raise Exception("Invalid API response")
            
            result_data = result["result"]
            
            if "layoutParsingResults" not in result_data:
                raise Exception("Invalid API response format")
            
            layout_results = result_data["layoutParsingResults"]
            
            # Extract text từ markdown
            text = ""
            for res in layout_results:
                if "markdown" in res and "text" in res["markdown"]:
                    md_text = res["markdown"]["text"]
                    text += md_text + "\n"
            
            return text.strip() if text else "Không tìm thấy văn bản"
            
        except Exception as e:
            raise
