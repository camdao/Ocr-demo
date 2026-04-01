py -3.11 -m venv .venv

.\.venv\Scripts\activate.ps1

pip install -r requirements.txt

streamlit run .\main.py

# Optional: PaddleOCR support (can be heavy and OS/Python-version dependent)
# pip install paddleocr paddlepaddle