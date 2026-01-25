import sys
import os
import shutil

def move_file(filename, source_dir="../paper_audit/inbox", dest_dir="../paper_audit/completed"):
    """Moves a file from inbox to completed."""
    source_path = os.path.join(source_dir, filename)
    dest_path = os.path.join(dest_dir, filename)
    
    if not os.path.exists(source_path):
        return f"ERROR: File {source_path} does not exist."
    
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
        
    try:
        shutil.move(source_path, dest_path)
        return f"SUCCESS: Moved {filename} to {dest_dir}"
    except Exception as e:
        return f"ERROR: Failed to move file: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <filename>")
        sys.exit(1)
        
    filename = sys.argv[1]
    # Simple logic for now: if the request contains "move" or is just a filename
    print(move_file(filename))
