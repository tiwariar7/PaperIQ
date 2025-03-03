import ftplib

def custom_retrlines(ftp, cmd, callback):
    """
    Custom version of FTP.retrlines that decodes using errors='replace'.
    """
    conn = ftp.transfercmd(cmd)
    fp = conn.makefile('r', encoding=ftp.encoding, errors='replace')
    while True:
        line = fp.readline()
        if not line:
            break
        callback(line.rstrip('\r\n'))
    fp.close()
    ftp.voidresp()

def safe_nlst(ftp, remote_dir):
    """
    Retrieves a directory listing from remote_dir using our custom retrlines.
    """
    lines = []
    try:
        custom_retrlines(ftp, 'NLST ' + remote_dir, lines.append)
    except ftplib.error_perm as e:
        print(f"Error listing {remote_dir}: {e}")
    return lines

def is_ftp_dir(ftp, path):
    """
    Checks if a given FTP path is a directory.
    Attempts to change directory into the path.
    """
    original = ftp.pwd()
    try:
        ftp.cwd(path)
        ftp.cwd(original)
        return True
    except ftplib.error_perm:
        return False

def join_ftp_path(current_dir, item):
    """
    Joins FTP paths. If item is already absolute, it returns item.
    Otherwise, it joins current_dir and item.
    """
    if item.startswith('/'):
        return item
    if current_dir == "/":
        return "/" + item
    return f"{current_dir}/{item}"

def write_tree(ftp, remote_dir, prefix, out_file):
    """
    Recursively writes the tree structure of remote_dir into out_file.
    """
    items = safe_nlst(ftp, remote_dir)
    # Remove '.' and '..' entries
    items = [item for item in items if item not in ['.', '..'] and item != '']
    items.sort()  # sort alphabetically for consistency

    for index, item in enumerate(items):
        full_path = join_ftp_path(remote_dir, item)
        is_dir = is_ftp_dir(ftp, full_path)
        connector = "└── " if index == len(items) - 1 else "├── "
        out_file.write(prefix + connector + item + ("/" if is_dir else "") + "\n")
        if is_dir:
            new_prefix = prefix + ("    " if index == len(items) - 1 else "│   ")
            write_tree(ftp, full_path, new_prefix, out_file)

def main():
    ftp_server = "172.16.191.17"
    output_file_name = "ftp_tree.txt"

    ftp = ftplib.FTP(ftp_server)
    # Set encoding (adjust if needed)
    ftp.encoding = 'latin-1'
    ftp.login()  # Supply credentials if necessary

    with open(output_file_name, "w", encoding="utf-8") as f:
        f.write(f"FTP Directory Tree for {ftp_server}\n")
        f.write("=" * 40 + "\n")
        write_tree(ftp, "/", "", f)

    ftp.quit()
    print(f"FTP tree structure written to {output_file_name}")

if __name__ == "__main__":
    main()
