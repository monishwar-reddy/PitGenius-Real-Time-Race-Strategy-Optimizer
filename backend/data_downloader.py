"""
Data Downloader for PitGenius
Downloads the COTA race dataset from Google Drive
"""

import os
import requests
import zipfile
from pathlib import Path

# Dataset URL
DATASET_URL = "https://drive.google.com/uc?export=download&id=1WHxQ1a3hG7jvmeoDBB0dYvbwZDrqd3eF"
DATASET_ZIP = "cota_dataset.zip"
EXTRACT_DIR = "race_data"

def download_dataset():
    """Download the COTA dataset from Google Drive"""
    print("📥 Downloading COTA race dataset...")
    print(f"URL: {DATASET_URL}")
    
    try:
        # Download the file
        response = requests.get(DATASET_URL, stream=True)
        response.raise_for_status()
        
        # Save to file
        with open(DATASET_ZIP, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"✅ Downloaded: {DATASET_ZIP}")
        return True
    
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return False

def extract_dataset():
    """Extract the downloaded zip file"""
    print(f"📦 Extracting dataset to {EXTRACT_DIR}...")
    
    try:
        # Create extraction directory if it doesn't exist
        Path(EXTRACT_DIR).mkdir(parents=True, exist_ok=True)
        
        # Extract zip file
        with zipfile.ZipFile(DATASET_ZIP, 'r') as zip_ref:
            zip_ref.extractall(EXTRACT_DIR)
        
        print(f"✅ Extracted to: {EXTRACT_DIR}")
        
        # Clean up zip file
        os.remove(DATASET_ZIP)
        print(f"🗑️  Removed: {DATASET_ZIP}")
        
        return True
    
    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        return False

def verify_dataset():
    """Verify that the dataset was extracted correctly"""
    print("🔍 Verifying dataset...")
    
    cota_path = Path(EXTRACT_DIR)
    
    if not cota_path.exists():
        print("❌ COTA directory not found")
        return False
    
    race1_path = cota_path / "Race 1"
    race2_path = cota_path / "Race 2"
    
    if race1_path.exists():
        race1_files = list(race1_path.glob("*.csv")) + list(race1_path.glob("*.CSV"))
        print(f"✅ Race 1: {len(race1_files)} files found")
    else:
        print("⚠️  Race 1 directory not found")
    
    if race2_path.exists():
        race2_files = list(race2_path.glob("*.csv")) + list(race2_path.glob("*.CSV"))
        print(f"✅ Race 2: {len(race2_files)} files found")
    else:
        print("⚠️  Race 2 directory not found")
    
    return True

def download_race_data():
    """
    Main function to download and setup race data
    Used by api.py on startup
    """
    print("=" * 60)
    print("PitGenius - COTA Dataset Downloader")
    print("=" * 60)
    
    # Check if dataset already exists
    if Path(EXTRACT_DIR).exists():
        race1_path = Path(EXTRACT_DIR) / "Race 1"
        if race1_path.exists() and len(list(race1_path.glob("*.csv"))) > 0:
            print(f"✅ Dataset already exists: {EXTRACT_DIR}")
            verify_dataset()
            return True
    
    # Download dataset
    if not download_dataset():
        print("❌ Failed to download dataset")
        return False
    
    # Extract dataset
    if not extract_dataset():
        print("❌ Failed to extract dataset")
        return False
    
    # Verify dataset
    verify_dataset()
    
    print("=" * 60)
    print("✅ Dataset setup complete!")
    print("=" * 60)
    return True

def main():
    """CLI entry point"""
    download_race_data()

if __name__ == "__main__":
    main()
