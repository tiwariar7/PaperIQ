import os
import re
import shutil
import tempfile
import cv2
import pdfplumber
import pytesseract
from pdf2image import convert_from_path
import pandas as pd
from fuzzywuzzy import fuzz
from collections import defaultdict
import logging
import json  # Added import

# --- CONFIGURATION ---
SIMILARITY_THRESHOLD = 85  # For fuzzy matching duplicate questions
CSV_PATH = "sorted_pdfs.csv"  # CSV file with headers: Department, Branch, Semester, Subject, FullPath
INPUT_DIR = "sorted_pdfs"     # Base directory where PDFs are located
OUTPUT_JSON_DIR = "sorted_json"  # Output directory for generated JSON files

# Tesseract configuration (customize if needed)
TESSERACT_CONFIG = "--oem 3 --psm 6"

# Set up logging
logging.basicConfig(filename='paperiq.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# --- HELPER FUNCTIONS ---
def extract_text_from_pdf(pdf_path):
    """
    Extract text using pdfplumber. For pages with minimal text,
    fall back to OCR using pdf2image and pytesseract.
    Also attempts to extract images (diagrams) from the PDF.
    """
    pass  

def extract_text_from_pdf(pdf_path):
    """
    Extract text using pdfplumber. For pages with minimal text,
    fall back to OCR using pdf2image and pytesseract.
    Also attempts to extract images (diagrams) from the PDF.
    """
    full_text = ""
    images_for_diagrams = []  # List to store temporary image file paths

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                # We'll decide next what to do with pages having little text
                if not page_text or len(page_text.strip()) < 20:
                    pass  # To be implemented in next part
                else:
                    full_text += "\n" + page_text
    except Exception as e:
        logging.error(f"Error processing {pdf_path}: {e}")
    return full_text, images_for_diagrams

