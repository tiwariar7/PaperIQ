import csv
import re

# Input and output file names
input_file = "ftp_tree.txt"
output_file = "sorted_question_papers.csv"

rows = []

with open(input_file, "r", encoding="utf-8") as f:
    for line in f:
        # Remove any leading/trailing whitespace (including tree symbols)
        line = line.strip()
        # Use regex to extract the full path starting with a "/"
        match = re.search(r'(/.*)', line)
        if match:
            path = match.group(1).strip()
            # Only consider lines that point to a PDF file
            if path.lower().endswith(".pdf"):
                # Split path into components and remove empty segments
                parts = [part for part in path.split("/") if part]
                if len(parts) >= 3:
                    # Assuming the first segment is the department and
                    # the second-to-last segment is the semester folder.
                    department = parts[0]
                    semester = parts[-2]
                    # The file name (last segment) contains the subject name.
                    subject = parts[-1]
                    if subject.lower().endswith(".pdf"):
                        subject = subject[:-4]  # remove ".pdf"
                    rows.append([department, semester, subject, path])

# Sort the records by department and then subject (both alphabetically)
rows.sort(key=lambda x: (x[0].lower(), x[2].lower()))

# Write the results to a CSV file
with open(output_file, "w", encoding="utf-8", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Department", "Semester", "Subject", "FullPath"])
    writer.writerows(rows)

print(f"CSV file '{output_file}' created with {len(rows)} records.")
