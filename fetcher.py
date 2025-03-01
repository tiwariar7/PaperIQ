import ftplib
import os

def custom_retrlines(ftp, cmd, callback):
    """
    Custom version of FTP.retrlines that decodes using errors='replace'.
    """
    conn = ftp.transfercmd(cmd)
    # Create a file object with the desired encoding and errors handling.
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
    It attempts to change directory into the path. On success, returns True.
    """
    original = ftp.pwd()
    try:
        ftp.cwd(path)
        ftp.cwd(original)
        return True
    except ftplib.error_perm:
        return False

def download_ftp_tree(ftp, remote_dir, local_dir):
    """
    Recursively downloads contents of remote_dir into the local folder local_dir.
    """
    os.makedirs(local_dir, exist_ok=True)
    items = safe_nlst(ftp, remote_dir)
    for item in items:
        base = os.path.basename(item.rstrip("/"))
        if base in ['.', '..'] or base == '':
            continue

        local_path = os.path.join(local_dir, base)
        if is_ftp_dir(ftp, item):
            print("Entering directory:", item)
            download_ftp_tree(ftp, item, local_path)
        else:
            print("Downloading file:", item)
            try:
                with open(local_path, 'wb') as f:
                    ftp.retrbinary("RETR " + item, f.write)
            except Exception as e:
                print(f"Failed to download {item}: {e}")

def main():
    ftp_server = "172.16.191.17"
    local_root = "RCOEM"  # Local folder for saving files

    ftp = ftplib.FTP(ftp_server)
    # Set encoding to 'latin-1' (or try 'cp1252' if needed)
    ftp.encoding = 'latin-1'
    ftp.login()  # Use credentials if required (e.g., ftp.login("user", "pass"))
    print("Connected to", ftp_server)

    download_ftp_tree(ftp, "/", local_root)
    ftp.quit()
    print("Download complete.")

if __name__ == "__main__":
    main()
