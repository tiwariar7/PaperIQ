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
                if len(parts) >= 4:  # Ensure it has enough elements to extract branch & timeline
                    # Extract Department
                    department = parts[0]
                    # Extract Branch (Second element in the path)
                    branch = parts[1]  
                    # Extract Timeline (Assumed to be before the Semester folder)
                    timeline = parts[-3] if len(parts) >= 4 else "Unknown"
                    # Extract Semester (Second-to-last folder)
                    semester = parts[-2]
                    # Extract Subject (Last segment)
                    subject = parts[-1].replace(".pdf", "")

                    rows.append([department, branch, timeline, semester, subject, path])

# Sort the records by Department, then Branch, then Timeline, then Subject
rows.sort(key=lambda x: (x[0].lower(), x[1].lower(), x[2].lower(), x[4].lower()))

# Write the results to a CSV file
with open(output_file, "w", encoding="utf-8", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Department", "Branch", "Timeline", "Semester", "Subject", "FullPath"])
    writer.writerows(rows)

print(f"CSV file '{output_file}' created with {len(rows)} records.")
