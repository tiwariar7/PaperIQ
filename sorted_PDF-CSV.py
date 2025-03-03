import os
import csv

def extract_details(full_path):
    """
    Extracts department, branch, semester, and subject from the given file path.
    Assumes the folder structure: Department -> Branch -> Semester -> Subject -> PDF files.
    """
    parts = full_path.split(os.sep)
    parts = [p for p in parts if p]  # Remove empty parts
    
    if len(parts) < 4:
        return None  # Ensure valid folder structure
    
    department, branch, semester, subject_file = parts[:4]
    subject = os.path.splitext(subject_file)[0]  # Remove .pdf extension safely
    
    return [department, branch, semester, subject, full_path]

def write_csv(base_dir, output_file):
    """
    Scans the sorted_pdfs directory and writes the extracted details into a CSV file.
    """
    rows = []
    
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.lower().endswith(".pdf"):
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_path, base_dir)  # Get relative path
                details = extract_details(relative_path)
                if details:
                    rows.append(details)
    
    # Sort the records by Department, then Branch, then Semester, then Subject
    rows.sort(key=lambda x: (x[0].lower(), x[1].lower(), x[2].lower(), x[3].lower()))
    
    with open(output_file, "w", encoding="utf-8", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Department", "Branch", "Semester", "Subject", "FullPath"])
        writer.writerows(rows)
    
    print(f"CSV file '{output_file}' created with {len(rows)} records.")

def main():
    base_dir = "sorted_pdfs"  # Root directory containing the PDFs
    output_file = "sorted_pdfs.csv"
    write_csv(base_dir, output_file)

if __name__ == "__main__":
    main()
