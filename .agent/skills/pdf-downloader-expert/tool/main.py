import sys
import os
import requests
from urllib.parse import urlparse

def download_pdf(url, output_dir):
    try:
        # Create directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Parse filename from URL
        path = urlparse(url).path
        filename = os.path.basename(path)
        
        # Clean up filename (remove query params if any)
        if '?' in filename:
            filename = filename.split('?')[0]
            
        if not filename:
            filename = "downloaded_file.pdf"
            
        if not filename.lower().endswith('.pdf'):
            filename += '.pdf'
            
        target_path = os.path.join(output_dir, filename)
        
        print(f"Downloading {url} to {target_path}...")
        
        # Add basic headers to avoid some anti-bot measures
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, stream=True, timeout=30, headers=headers)
        response.raise_for_status()
        
        # Check Content-Type if possible
        content_type = response.headers.get('Content-Type', '').lower()
        if 'application/pdf' not in content_type and not filename.lower().endswith('.pdf'):
             print(f"Warning: Content-Type is {content_type}, might not be a PDF.")

        with open(target_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                
        print(f"Successfully downloaded: {target_path}")
        return target_path
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <url>")
        sys.exit(1)
        
    url = sys.argv[1]
    
    # script_dir is /.../pdf-downloader-tool
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # root_dir is /...
    root_dir = os.path.dirname(script_dir)
    output_dir = os.path.join(root_dir, "paper_audit", "inbox")
    
    download_pdf(url, output_dir)
