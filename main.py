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
