# Utilities - các hàm tiện ích
from PIL import Image
from typing import Optional

def validate_image(image: Optional[Image.Image]) -> bool:
    """Kiểm tra ảnh có hợp lệ không"""
    return image is not None and isinstance(image, Image.Image)

def get_image_info(image: Image.Image) -> dict:
    """Lấy thông tin chi tiết của ảnh"""
    return {
        "size": image.size,
        "format": image.format,
        "mode": image.mode,
        "width": image.width,
        "height": image.height
    }

def format_statistics(char_count: int, word_count: int, line_count: int) -> dict:
    """Định dạng thống kê"""
    return {
        "characters": char_count,
        "words": word_count,
        "lines": line_count,
        "avg_word_length": round(char_count / max(word_count, 1), 2)
    }
