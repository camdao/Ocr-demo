# Main application
import streamlit as st
from PIL import Image
from ui.components import Header, SidebarConfig, InputSection, ResultSection, Footer

def main():

    Header.render()
    
    ocr = SidebarConfig.render()
    
    result_col, image_data = InputSection.render()
    
    if image_data is not None:
        try:
            with st.spinner("⏳ Đang xử lý..."):
                recognized_text = ocr.read_image(image_data)
                
                ResultSection.render(result_col, recognized_text)
        
        except Exception as e:
            with result_col:
                st.error(f"❌ Lỗi trong quá trình nhận diện: {str(e)}")
    else:
        ResultSection.render_empty_state(result_col)
    
    Footer.render()

if __name__ == "__main__":
    main()
