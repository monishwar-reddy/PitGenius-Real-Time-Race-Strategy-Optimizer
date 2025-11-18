import os
import requests
import zipfile
from pathlib import Path

# Direct download link to your Mega file (converted to a usable URL)
FILE_URL = "https://pixeldrain.com/api/file/HXtFKpF3"

ZIP_NAME = "COTA_lap_end_time_R1.zip"
EXTRACT_DIR = "race_data"

def download_dataset():
    print("📥 Downloading dataset...")

    response = requests.get(FILE_URL, stream=True)
    response.raise_for_status()

    with open(ZIP_NAME, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    print("✅ Downloaded dataset")
    return True

def extract_dataset():
    print("📦 Extracting dataset...")

    Path(EXTRACT_DIR).mkdir(exist_ok=True)

    with zipfile.ZipFile(ZIP_NAME, "r") as zip_ref:
        zip_ref.extractall(EXTRACT_DIR)

    os.remove(ZIP_NAME)
    print("🗑️ Removed ZIP file")
    return True

def verify_dataset():
    print("🔍 Verifying dataset...")

    race1 = Path(EXTRACT_DIR) / "Race 1"
    if race1.exists():
        print("✅ Race 1 found")
    else:
        print("❌ Race 1 NOT found")

def download_race_data():
    if Path(EXTRACT_DIR).exists() and len(list(Path(EXTRACT_DIR).glob("**/*.csv"))) > 0:
        print("✅ Dataset already exists")
        verify_dataset()
        return True

    download_dataset()
    extract_dataset()
    verify_dataset()
    return True


