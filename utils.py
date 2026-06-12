import os
import zipfile
import tempfile
import subprocess
from io import BytesIO
                                            
ALLOWED_EXTENSIONS = {'.py', '.java', '.js', '.md', '.ts', '.tsx', '.jsx', '.html', '.css'}

def is_allowed_file(filename: str) -> bool:
    _, ext = os.path.splitext(filename)
    return ext.lower() in ALLOWED_EXTENSIONS

def extract_from_files(uploaded_files):
    """Extract code from directly uploaded Streamlit files."""
    code_dict = {}
    for file in uploaded_files:
        if is_allowed_file(file.name):
            try:
                code_dict[file.name] = file.getvalue().decode('utf-8')
            except Exception as e:
                code_dict[file.name] = f"Error reading file: {e}"
    return code_dict

def extract_from_zip(uploaded_zip):
    """Extract code from an uploaded ZIP file."""
    code_dict = {}
    try:
        with zipfile.ZipFile(uploaded_zip, 'r') as z:
            for file_info in z.infolist():
                if not file_info.is_dir() and is_allowed_file(file_info.filename):
                    with z.open(file_info.filename) as f:
                        try:
                            code_dict[file_info.filename] = f.read().decode('utf-8')
                        except Exception:
                            pass                                             
    except Exception as e:
        code_dict['error.txt'] = f"Error extracting ZIP: {e}"
    return code_dict

def extract_from_github(repo_url):
    """Clone a GitHub repo to a temporary directory and extract code."""
    code_dict = {}
    with tempfile.TemporaryDirectory() as temp_dir:
        try:                                 
            subprocess.run(
                ['git', 'clone', '--depth', '1', repo_url, temp_dir],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            for root, dirs, files in os.walk(temp_dir):         
                if '.git' in dirs:
                    dirs.remove('.git')
                for file in files:
                    if is_allowed_file(file):
                        full_path = os.path.join(root, file)
                        rel_path = os.path.relpath(full_path, temp_dir)
                                                                                                       
                        rel_path = rel_path.replace('\\', '/')
                        try:
                            with open(full_path, 'r', encoding='utf-8') as f:
                                code_dict[rel_path] = f.read()
                        except Exception:
                            pass                         
        except subprocess.CalledProcessError as e:
            code_dict['error.txt'] = f"Failed to clone repository: {e.stderr.decode('utf-8', errors='ignore')}"
        except Exception as e:
            code_dict['error.txt'] = f"An error occurred: {str(e)}"
    return code_dict
