# UI Components - các thành phần giao diện
import streamlit as st
import sys
from PIL import Image
from typing import Tuple, Optional, Union, Any
from ocr.tesseract_ocr import TesseractOCR

PADDLE_IMPORT_ERROR = None
try:
    from ocr.paddle_ocr import PaddleOCREngine
except Exception as exc:
    PaddleOCREngine = None
    PADDLE_IMPORT_ERROR = exc

class SidebarConfig:
    """Quản lý cấu hình sidebar"""
    
    @staticmethod
    def render() -> Union[TesseractOCR, Any]:
        """Render sidebar và trả về OCR instance"""
        st.sidebar.header("⚙️ Cấu hình")
        
        # Model selection
        model_options = ["Tesseract"]
        if PaddleOCREngine is not None:
            model_options.append("PaddleOCR")

        model = st.sidebar.selectbox(
            "Chọn model OCR:",
            model_options,
            format_func=lambda x: {
                "Tesseract": "📄 Tesseract OCR",
                "PaddleOCR": "🎯 PaddleOCR"
            }.get(x, x)
        )

        if PaddleOCREngine is None:
            if isinstance(PADDLE_IMPORT_ERROR, ModuleNotFoundError):
                st.sidebar.info("PaddleOCR chưa sẵn sàng trong môi trường Python hiện tại. Đang dùng Tesseract OCR.")
            else:
                st.sidebar.warning(f"Không thể khởi tạo PaddleOCR: {PADDLE_IMPORT_ERROR}")

            st.sidebar.caption(f"Python đang chạy: {sys.executable}")
        
        if model == "Tesseract":
            # Language selection for Tesseract
            language = st.sidebar.selectbox(
                "Chọn ngôn ngữ:",
                ["vie", "eng", "chi_sim", "jpn"],
                format_func=lambda x: {
                    "vie": "🇻🇳 Tiếng Việt",
                    "eng": "🇺🇸 English",
                    "chi_sim": "🇨🇳 Chinese (Simplified)",
                    "jpn": "🇯🇵 Japanese"
                }.get(x, x)
            )
            
            # PSM selection
            psm_option = st.sidebar.selectbox(
                "Chế độ phân tách trang (PSM):",
                ["6", "3", "4", "5", "11", "13"],
                format_func=lambda x: {
                    "3": "3 - Tự động phát hiện",
                    "4": "4 - Cột đơn",
                    "5": "5 - Khối xác định",
                    "6": "6 - Đoạn văn thống nhất (Mặc định)",
                    "11": "11 - Từng dòng",
                    "13": "13 - Từng từ"
                }.get(x, x)
            )
            
            return TesseractOCR(lang=language, config=f"--psm {psm_option}")
        
        else:  # PaddleOCR
            # Language selection for PaddleOCR
            language = st.sidebar.selectbox(
                "Chọn ngôn ngữ:",
                ["vi", "en", "ch", "ja"],
                format_func=lambda x: {
                    "vi": "🇻🇳 Vietnamese",
                    "ch": "🇨🇳 Chinese",
                    "en": "🇺🇸 English",
                    "ja": "🇯🇵 Japanese"
                }.get(x, x)
            )
            
            # Angle classification option
            use_angle_cls = st.sidebar.checkbox("Sử dụng nhận diện góc", value=True)
            
            return PaddleOCREngine(lang=language, use_angle_cls=use_angle_cls)


class InputSection:
    """Quản lý phần nhập dữ liệu"""
    
    @staticmethod
    def render() -> Tuple[str, Optional[Image.Image]]:
        """Render phần nhập và trả về (phương thức, ảnh)"""
        input_method = st.sidebar.radio(
            "Phương pháp nhập:",
            ["📤 Tải lên hình ảnh", "📷 Chụp từ camera"]
        )
        
        col1, col2 = st.columns(2, gap="large")
        image_data = None
        
        with col1:
            if input_method == "📤 Tải lên hình ảnh":
                st.subheader("Hình ảnh đầu vào")
                uploaded_file = st.file_uploader(
                    "Chọn hình ảnh",
                    type=["jpg", "jpeg", "png", "bmp", "tiff"],
                    label_visibility="collapsed"
                )
                
                if uploaded_file is not None:
                    image_data = Image.open(uploaded_file)
                    st.image(image_data, use_column_width=True)
            else:
                st.subheader("Capture từ camera")
                camera_image = st.camera_input(
                    "Chụp ảnh từ webcam",
                    label_visibility="collapsed"
                )
                
                if camera_image is not None:
                    image_data = Image.open(camera_image)
                    st.image(image_data, use_column_width=True)
        
        return col2, image_data


class ResultSection:
    """Quản lý phần kết quả"""
    
    @staticmethod
    def render(col, recognized_text: str):
        """Render phần kết quả"""
        with col:
            st.subheader("Kết quả nhận diện")
            st.success("✅ Nhận diện thành công!")
            
            # Text output
            st.text_area(
                "Văn bản nhận diện:",
                value=recognized_text,
                height=200,
                disabled=False,
                label_visibility="collapsed"
            )
            
            # Statistics
            st.markdown("---")
            col_stats1, col_stats2, col_stats3 = st.columns(3)
            
            char_count = len(recognized_text)
            word_count = len(recognized_text.split())
            line_count = len(recognized_text.split('\n'))
            
            with col_stats1:
                st.metric("📝 Số ký tự", char_count)
            
            with col_stats2:
                st.metric("📖 Số từ", word_count)
            
            with col_stats3:
                st.metric("📄 Số dòng", line_count)
            
            # Download section
            st.markdown("---")
            ResultSection.render_download_buttons(recognized_text)
    
    @staticmethod
    def render_download_buttons(text: str):
        """Render các nút tải xuất"""
        col_download1, col_download2 = st.columns(2)
        
        with col_download1:
            txt_data = text.encode('utf-8')
            st.download_button(
                label="📥 Tải văn bản (.txt)",
                data=txt_data,
                file_name="ocr_result.txt",
                mime="text/plain"
            )
        
        with col_download2:
            csv_data = "Recognized Text\n" + text.replace('\n', '\n')
            st.download_button(
                label="📥 Tải kết quả (.csv)",
                data=csv_data.encode('utf-8'),
                file_name="ocr_result.csv",
                mime="text/csv"
            )
    
    @staticmethod
    def render_empty_state(col):
        """Render trạng thái trống"""
        with col:
            st.info("👈 Vui lòng tải lên hoặc chụp một hình ảnh để bắt đầu")


class Header:
    """Quản lý phần header"""
    
    @staticmethod
    def render():
        """Render header"""
        st.set_page_config(
            page_title="OCR Demo",
            page_icon="📄",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        st.title("📄 OCR Demo")
        st.markdown("Ứng dụng demo nhận diện ký tự quang học (OCR) từ hình ảnh")


class Footer:
    """Quản lý phần footer"""
    
    @staticmethod
    def render():
        """Render footer"""
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: gray; font-size: 12px;">
            <p>Powered by Tesseract OCR | Streamlit Demo</p>
            <p>Hỗ trợ nhiều ngôn ngữ và chế độ xử lý khác nhau</p>
        </div>
        """, unsafe_allow_html=True)
