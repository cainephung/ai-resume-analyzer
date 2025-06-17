@echo off
REM Create virtual environment
python -m venv venv

REM Activate the virtual environment
call venv\Scripts\activate

REM Upgrade pip
python -m pip install --upgrade pip

REM Install required packages
pip install ^
    streamlit==1.45.1 ^
    fpdf==1.7.2 ^
    pdfplumber==0.11.7 ^
    python-docx==1.1.2 ^
    textstat==0.7.7 ^
    sentence-transformers==4.1.0 ^
    scikit-learn==1.7.0 ^
    numpy==2.3.0 ^
    scipy==1.15.3 ^
    torch==2.7.1 ^
    transformers==4.52.4 ^
    regex==2024.11.6 ^
    pandas==2.3.0

REM Optional: spaCy and English model
pip install spacy==3.7.4
python -m spacy download en_core_web_sm

echo ✅ Virtual environment setup complete. To activate again: call venv\Scripts\activate
pause
