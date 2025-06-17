#!/bin/bash

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install core dependencies
pip install \
  streamlit==1.45.1 \
  fpdf==1.7.2 \
  pdfplumber==0.11.7 \
  python-docx==1.1.2 \
  textstat==0.7.7 \
  sentence-transformers==4.1.0 \
  scikit-learn==1.7.0 \
  numpy==2.3.0 \
  scipy==1.15.3 \
  torch==2.7.1 \
  transformers==4.52.4 \
  regex==2024.11.6 \
  pandas==2.3.0

# Optional: If using spaCy
pip install spacy==3.7.4
python -m spacy download en_core_web_sm

echo "✅ Environment setup complete. Run with: source venv/bin/activate"
