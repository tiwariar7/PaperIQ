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
import json  


SIMILARITY_THRESHOLD = 85
CSV_PATH = "sorted_pdfs.csv"  
INPUT_DIR = "sorted_pdfs"   
OUTPUT_JSON_DIR = "sorted_json"  


TESSERACT_CONFIG = "--oem 3 --psm 6"

logging.basicConfig(filename='paperiq.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s'

def extract_text_from_pdf(pdf_path):
    """
    Extract text using pdfplumber. For pages with minimal text,
    fall back to OCR using pdf2image and pytesseract.
    Also attempts to extract images (diagrams) from the PDF.
    """
    full_text = ""
    images_for_diagrams = [] 

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                if not page_text or len(page_text.strip()) < 20:
                    logging.info(f"Performing OCR for page {i+1} of {pdf_path}")
                    pil_images = convert_from_path(pdf_path, first_page=i+1, last_page=i+1)
                    if pil_images:
                        img = pil_images[0]
                        tmp_img_path = os.path.join(tempfile.gettempdir(), f"page_{i+1}.png")
                        img.save(tmp_img_path, "PNG")
                        ocr_text = pytesseract.image_to_string(tmp_img_path, config=TESSERACT_CONFIG)
                        full_text += "\n" + ocr_text
                        images_for_diagrams.append(tmp_img_path)
                    else:
                        logging.warning(f"Failed to convert page {i+1} to image.")
                else:
                    full_text += "\n" + page_text
                    if "images" in page.objects:
                        for img_obj in page.images:
                            try:
                                cropped = page.crop((img_obj["x0"], img_obj["top"],
                                                     img_obj["x1"], img_obj["bottom"]))
                                tmp_img_path = os.path.join(
                                    tempfile.gettempdir(), 
                                    f"{os.path.basename(pdf_path)}_page_{i+1}_img.png"
                                )
                                cropped.to_image().save(tmp_img_path, format="PNG")
                                images_for_diagrams.append(tmp_img_path)
                            except Exception as e:
                                logging.error(f"Error extracting image on page {i+1}: {e}")
        logging.info(f"Extracted text from {pdf_path}:\n{full_text}")
    except Exception as e:
        logging.error(f"Error processing {pdf_path}: {e}")
    return full_text, images_for_diagrams

def extract_subquestions(question_block):
    """
    Split a question block into subquestions if markers such as (a), (b), etc. are present.
    The regex looks for markers at the beginning of a line.
    """
    subpattern = r'(?m)^\s*\(([a-zivx]+)\)'
    parts = re.split(subpattern, question_block)
    if len(parts) <= 1:
        return [question_block.strip()]
    else:
        subquestions = []    
        header = parts[0].strip()
        for i in range(1, len(parts), 2):
            marker = parts[i].strip()
            content = parts[i+1].strip() if (i+1) < len(parts) else ""
            full_text = f"({marker}) {content}"
            subquestions.append(full_text)
        if header:
            subquestions.insert(0, header)
        return subquestions

def extract_questions(text):
    """
    Extract full question blocks from the text and then further split into subquestions.
    It matches from a line that starts with a question number (e.g., "1.") until the next such line or end of text.
    """
    pattern = r'(?sm)^\s*\d+\.\s*(.*?)(?=^\s*\d+\.\s*|\Z)'
    blocks = re.findall(pattern, text)
    all_questions = []
    for block in blocks:
        subqs = extract_subquestions(block)
        all_questions.extend(subqs)
    logging.info(f"Extracted questions: {all_questions}")
    return all_questions

def deduplicate_questions_with_source(question_source_list):
    """
    Deduplicate questions using fuzzy matching while preserving source PDF names.
    Input: list of tuples (question_text, source_pdf_filename)
    Returns: list of dicts with keys 'question', 'sources', and 'count'.
    """
    unique_qs = []
    for question, source in question_source_list:
        merged = False
        for uq in unique_qs:
            similarity = fuzz.token_set_ratio(question, uq['question'])
            if similarity >= SIMILARITY_THRESHOLD:
                if source not in uq['sources']:
                    uq['sources'].append(source)
                uq['count'] += 1
                merged = True
                break
        if not merged:
            unique_qs.append({'question': question, 'sources': [source], 'count': 1})
    logging.info(f"Unique questions after deduplication: {unique_qs}")
    return unique_qs

def save_to_json(department, branch, semester, subject, unique_questions):
    """
    Save unique questions and their metadata to a JSON file.
    """
    out_dir = os.path.join(OUTPUT_JSON_DIR, department, branch, str(semester), subject)
    ensure_directory(out_dir)
    json_file_path = os.path.join(out_dir, f"{subject}_Questions.json")
    data = {
        "Department": department,
        "Branch": branch,
        "Semester": semester,
        "Subject": subject,
        "questions": unique_questions
    }
    with open(json_file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    logging.info(f"Saved JSON file for {subject} at {json_file_path}")

def process_pdf_record(pdf_record):
    """
    Process a single PDF record.
    Expected CSV columns: Department, Branch, Semester, Subject, FullPath.
    Returns a dict with metadata, list of (question, source_pdf_filename) tuples, and diagrams.
    """
    pdf_rel_path = pdf_record["FullPath"].replace("\\", os.sep)
    pdf_path = os.path.join(INPUT_DIR, pdf_rel_path)
    department = pdf_record["Department"]
    branch = pdf_record["Branch"]
    semester = pdf_record["Semester"]
    subject = pdf_record["Subject"]

    logging.info(f"Processing: {pdf_path}")
    text, diagrams = extract_text_from_pdf(pdf_path)
    questions = extract_questions(text)
    pdf_filename = os.path.basename(pdf_path)
    question_source_list = [(q, pdf_filename) for q in questions]
    
    return {
        "Department": department,
        "Branch": branch,
        "Semester": semester,
        "Subject": subject,
        "questions": question_source_list,
        "diagrams": diagrams,
        "pdf_path": pdf_path
    }

def ensure_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)

def main():
    df = pd.read_csv(CSV_PATH)
    subject_records = defaultdict(lambda: {"questions": [], "diagrams": []})
    for _, row in df.iterrows():
        record = process_pdf_record(row)
        key = (record["Department"], record["Branch"], record["Semester"], record["Subject"])
        subject_records[key]["questions"].extend(record["questions"])
        subject_records[key]["diagrams"].extend(record["diagrams"])
    
    for (dept, branch, sem, subject), data in subject_records.items():
        unique_questions = deduplicate_questions_with_source(data["questions"])
        unique_questions = sorted(unique_questions, key=lambda x: x['count'], reverse=True)
        save_to_json(dept, branch, sem, subject, unique_questions)
    
    logging.info("Processing complete.")

if __name__ == "__main__":
    main()
