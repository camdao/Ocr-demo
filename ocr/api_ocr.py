import base64
import os
import requests
from PIL import Image
import io
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class APILayoutParsingOCR:
    """OCR dùng API layout parsing từ Baidu"""
    
    def __init__(self, api_url=None, token=None):
        self.api_url = api_url or os.getenv("API_URL", "https://20ec2cibw7n8y5m8.aistudio-app.com/layout-parsing")
        self.token = token or os.getenv("API_TOKEN", "")
        self.headers = {
            "Authorization": f"token {self.token}",
            "Content-Type": "application/json"
        }
    
    def read_image(self, image):
        """Gửi ảnh tới API và nhận diện text"""
        try:
            # Convert PIL Image to bytes
            if isinstance(image, Image.Image):
                # Convert to RGB if needed
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                
                # Save to bytes
                img_bytes = io.BytesIO()
                image.save(img_bytes, format='PNG')
                img_bytes.seek(0)
                file_data = base64.b64encode(img_bytes.read()).decode("ascii")
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
            
            response = requests.post(self.api_url, json=payload, headers=self.headers, timeout=60)
            
            if response.status_code != 200:
                raise Exception(f"API error: {response.status_code}")
            
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
