import os
import re
import shutil
import logging
import json 
# --- CONFIGURATION ---
SIMILARITY_THRESHOLD = 85  
CSV_PATH = "sorted_pdfs.csv" 
INPUT_DIR = "sorted_pdfs"    
OUTPUT_JSON_DIR = "sorted_json"  
