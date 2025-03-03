import os

def write_tree(local_dir, prefix, out_file):
    """
    Recursively writes the tree structure of local_dir into out_file.
    """
    try:
        items = sorted(os.listdir(local_dir))  # Sort items for consistency
    except PermissionError:
        return  # Skip directories without permission

    for index, item in enumerate(items):
        full_path = os.path.join(local_dir, item)
        is_dir = os.path.isdir(full_path)
        connector = "└── " if index == len(items) - 1 else "├── "
        out_file.write(prefix + connector + item + ("/" if is_dir else "") + "\n")
        
        if is_dir:
            new_prefix = prefix + ("    " if index == len(items) - 1 else "│   ")
            write_tree(full_path, new_prefix, out_file)

def main():
    local_root = "sorted_pdfs"
    output_file_name = "folder_structure.txt"

    with open(output_file_name, "w", encoding="utf-8") as f:
        f.write(f"Folder Structure for {local_root}\n")
        f.write("=" * 40 + "\n")
        write_tree(local_root, "", f)

    print(f"Folder structure written to {output_file_name}")

if __name__ == "__main__":
    main()
