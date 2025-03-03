import os
import csv
import shutil

def get_unique_filename(directory, base_name, ext):
    """
    Returns a unique filename by appending a number if needed.
    For example, if 'Subject_Timeline.pdf' exists, it will try 
    'Subject_Timeline_1.pdf', 'Subject_Timeline_2.pdf', etc.
    """
    filename = f"{base_name}{ext}"
    counter = 1
    while os.path.exists(os.path.join(directory, filename)):
        filename = f"{base_name}_{counter}{ext}"
        counter += 1
    return filename

# Configurable paths
csv_file = "sorted_question_papers.csv"
local_root = "RCOEM"         # Folder where the original PDFs are downloaded
target_root = "sorted_pdfs"  # Destination folder

# Read CSV and process each row
with open(csv_file, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        # Extract details from CSV row (trimming whitespace)
        department = row["Department"].strip()
        branch = row["Branch"].strip()
        timeline = row["Timeline"].strip()      # e.g. "SUMMER -2024"
        semester = row["Semester"].strip()
        subject = row["Subject"].strip()
        full_path = row["FullPath"].strip()       # e.g. "/B. E/ARTIFICIAL INTELLGENCE AND MACHINE LEARNING/..."

        # Construct the source file path (remove leading slash)
        relative_path = full_path.lstrip("/")
        source_path = os.path.join(local_root, relative_path)
        
        # Build target directory:
        # sorted_pdfs/Department/Branch/Semester/Subject/
        target_dir = os.path.join(target_root, department, branch, semester, subject)
        os.makedirs(target_dir, exist_ok=True)
        
        # Create a new file name using subject and timeline (e.g. "Subject_Timeline.pdf")
        base_name = f"{subject}_{timeline}"
        ext = ".pdf"
        new_filename = get_unique_filename(target_dir, base_name, ext)
        dest_path = os.path.join(target_dir, new_filename)
        
        # Instead of moving, we copy the file (preserving metadata)
        if os.path.exists(source_path):
            try:
                shutil.copy2(source_path, dest_path)
                print(f"Copied: {source_path} -> {dest_path}")
            except Exception as e:
                print(f"Error copying {source_path}: {e}")
        else:
            print(f"Source file does not exist: {source_path}")