import sys
import os
import shutil

def move_file(filename, source_dir=None, dest_dir=None):
    """Moves a file from inbox to completed."""
    # Base path is the tools/ folder (parent of paper-audit-tool)
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    paper_audit_root = os.path.join(base_path, "paper_audit")
    
    if source_dir is None:
        source_dir = os.path.join(paper_audit_root, "inbox")
    if dest_dir is None:
        dest_dir = os.path.join(paper_audit_root, "completed")
        
    notes_dir = os.path.join(paper_audit_root, "notes")
    
    # Ensure all required directories exist
    os.makedirs(source_dir, exist_ok=True)
    os.makedirs(dest_dir, exist_ok=True)
    os.makedirs(notes_dir, exist_ok=True)

    source_path = os.path.join(source_dir, filename)
    dest_path = os.path.join(dest_dir, filename)
    
    if not os.path.exists(source_path):
        return f"ERROR: File {source_path} does not exist."
        
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
