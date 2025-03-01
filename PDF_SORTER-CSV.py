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
                    # Extract department (1st segment)
                    department = parts[0]
                    # Extract branch (2nd segment)
                    branch = parts[1] if len(parts) > 1 else "Unknown"
                    # Extract semester (second-to-last segment)
                    semester = parts[-2]
                    # Extract subject name (last segment without ".pdf")
                    subject = parts[-1]
                    if subject.lower().endswith(".pdf"):
                        subject = subject[:-4]  # remove ".pdf"
                    # Append the row
                    rows.append([department, branch, semester, subject, path])

# Sort the records by department, branch, and subject (all alphabetically)
rows.sort(key=lambda x: (x[0].lower(), x[1].lower(), x[3].lower()))

# Write the results to a CSV file
with open(output_file, "w", encoding="utf-8", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Department", "Branch", "Semester", "Subject", "FullPath"])
    writer.writerows(rows)

print(f"CSV file '{output_file}' created with {len(rows)} records.")
