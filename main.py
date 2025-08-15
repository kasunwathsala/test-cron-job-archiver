import requests
import json
from pathlib import Path
from datetime import datetime

# Configuration
BASE_FOLDER = Path("doc-archive")
LOG_FILE = Path("README.md")

# Your document dataset - put your actual data here
DOCUMENTS_DATA = [
    {
        "doc_id": "2156-01",
        "doc_date": "2019-12-30",
        "folder_path": "2019/12/30/2156-01",
        "file_name": "2156-01_english.pdf",
        "download_url": "https://drive.google.com/uc?id=1IjZR0E5RC8K6XexhzkJIMBCmw9Pu_HMo&export=download"
    },
    {
        "doc_id": "2156-03",
        "doc_date": "2019-12-30",
        "folder_path": "2019/12/30/2156-03",
        "file_name": "2156-03_english.pdf",
        "download_url": "https://drive.google.com/uc?id=1Ew-oE7yscyNbvsJfa1is7ELGkyCj9DGw&export=download"
    },
    {
        "doc_id": "2156-14",
        "doc_date": "2019-12-31",
        "folder_path": "2019/12/31/2156-14",
        "file_name": "2156-14_english.pdf",
        "download_url": "https://drive.google.com/uc?id=1EDWYrYP_cXbhtSJ3jcTS5DJkrMoOAP-k&export=download"
    },
    {
        "doc_id": "2156-15",
        "doc_date": "2019-12-31",
        "folder_path": "2019/12/31/2156-15",
        "file_name": "2156-15_english.pdf",
        "download_url": "https://drive.google.com/uc?id=1SYhP7uJ3Xk9OFiNosXsd3PNOE3O36SG3&export=download"
    },
    {
        "doc_id": "2194-69",
        "doc_date": "2020-09-25",
        "folder_path": "2020/09/25/2194-69",
        "file_name": "2194-69_english.pdf",
        "download_url": "https://drive.google.com/uc?id=1Rfy0_FF1qC7T3RID1DKvau08qPeiyCy1&export=download"
    },
    {
        "doc_id": "2194-70",
        "doc_date": "2020-09-25",
        "folder_path": "2020/09/25/2194-70",
        "file_name": "2194-70_english.pdf",
        "download_url": "https://drive.google.com/uc?id=1iqtA22b7B3feoL_ch18vH6N36FnFy3WE&export=download"
    }
    # Add more documents here...
]

def ensure_folder_exists(folder_path):
    """Create folder structure if it doesn't exist"""
    folder_path.mkdir(parents=True, exist_ok=True)

def get_folder_structure(doc):
    """Create folder structure from document date and ID"""
    # Parse date: 2019-12-30
    date_parts = doc['doc_date'].split('-')
    year, month, day = date_parts[0], date_parts[1], date_parts[2]
    doc_id = doc['doc_id']
    
    # Create path: doc-archive/2019/12/30/2156-01/
    folder_path = BASE_FOLDER / year / month / day / doc_id
    return folder_path

def download_document(doc):
    """Download a single document to the structured folder"""
    try:
        doc_id = doc['doc_id']
        filename = doc['file_name']
        download_url = doc['download_url']
        
        print(f"📥 Processing: {doc_id} - {filename}")
        
        # Create folder structure
        folder_path = get_folder_structure(doc)
        ensure_folder_exists(folder_path)
        file_path = folder_path / filename
        
        # Check if file already exists
        if file_path.exists():
            print(f"⏭️  Skipping: {filename} (already exists)")
            return True, doc_id, 0, "Already exists"
        
        # Download the file
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(download_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Save the file
        file_path.write_bytes(response.content)
        file_size = len(response.content)
        
        print(f"✅ Downloaded: {filename} ({file_size:,} bytes)")
        return True, doc_id, file_size, "Downloaded"
        
    except Exception as e:
        print(f"❌ Error downloading {doc.get('doc_id', 'unknown')}: {str(e)}")
        return False, doc.get('doc_id', 'unknown'), 0, str(e)

def update_log(downloads):
    """Update the download log"""
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    date_str = now.strftime("%B %d, %Y")
    
    if LOG_FILE.exists():
        content = LOG_FILE.read_text(encoding="utf-8")
    else:
        content = """# 📄 Document Archive Log

Automated document archiving

## 📊 Archive Statistics
- **Total Downloads:** 0
- **Last Run:** Never
- **Status:** 🟢 Active

## 📝 Recent Archive Runs
"""
    
    # Count results
    successful_downloads = sum(1 for success, _, _, status in downloads if success and status == "Downloaded")
    skipped_files = sum(1 for success, _, _, status in downloads if success and status == "Already exists")
    failed_downloads = sum(1 for success, _, _, _ in downloads if not success)
    total_size = sum(size for success, _, size, status in downloads if success and status == "Downloaded")
    
    # Update statistics
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('- **Last Run:**'):
            lines[i] = f'- **Last Run:** {timestamp}'
        elif line.startswith('- **Total Downloads:**'):
            try:
                current_count = int(line.split('**')[2].strip())
                new_total = current_count + successful_downloads
                lines[i] = f'- **Total Downloads:** {new_total}'
            except:
                lines[i] = f'- **Total Downloads:** {successful_downloads}'
    
    content = '\n'.join(lines)
    
    # Add new log entry
    log_entry = f"""
### 🔄 Archive Run - {timestamp}
- **Date:** {date_str}
- **Time:** {now.strftime("%I:%M:%S %p")} UTC
- **Documents Processed:** {len(downloads)}
- **New Downloads:** {successful_downloads}
- **Skipped (Existing):** {skipped_files}
- **Failed:** {failed_downloads}
- **Total Size:** {total_size:,} bytes

"""
    
    if successful_downloads > 0:
        log_entry += "**Downloaded:**\n"
        for success, doc_id, size, status in downloads:
            if success and status == "Downloaded":
                log_entry += f"- ✅ {doc_id} ({size:,} bytes)\n"
        log_entry += "\n"
    
    if skipped_files > 0:
        log_entry += "**Skipped:**\n"
        for success, doc_id, _, status in downloads:
            if success and status == "Already exists":
                log_entry += f"- ⏭️  {doc_id}\n"
        log_entry += "\n"
    
    if failed_downloads > 0:
        log_entry += "**Failed:**\n"
        for success, doc_id, _, error in downloads:
            if not success:
                log_entry += f"- ❌ {doc_id}: {error}\n"
        log_entry += "\n"
    
    # Insert log entry
    if "## 📝 Recent Archive Runs" in content:
        content = content.replace("## 📝 Recent Archive Runs", f"## 📝 Recent Archive Runs{log_entry}")
    else:
        content += log_entry
    
    LOG_FILE.write_text(content, encoding="utf-8")

def main():
    """Main function - processes all documents in the dataset"""
    print("📄 Starting Document Archiver...")
    print(f"⏰ Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📊 Processing {len(DOCUMENTS_DATA)} documents")
    
    # Create base folder
    ensure_folder_exists(BASE_FOLDER)
    
    downloads = []
    
    # Process all documents
    for i, doc in enumerate(DOCUMENTS_DATA, 1):
        print(f"\n[{i}/{len(DOCUMENTS_DATA)}] {doc['doc_id']}")
        success, doc_id, size, status = download_document(doc)
        downloads.append((success, doc_id, size, status))
    
    # Update log
    update_log(downloads)
    
    # Summary
    successful_downloads = sum(1 for success, _, _, status in downloads if success and status == "Downloaded")
    skipped_files = sum(1 for success, _, _, status in downloads if success and status == "Already exists")
    failed_downloads = sum(1 for success, _, _, _ in downloads if not success)
    
    print(f"\n🎉 Archive job completed!")
    print(f"✅ Downloaded: {successful_downloads} new files")
    print(f"⏭️  Skipped: {skipped_files} existing files")
    print(f"❌ Failed: {failed_downloads} files")

if __name__ == "__main__":
    main()