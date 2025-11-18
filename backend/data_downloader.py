import os
import requests
import zipfile
from pathlib import Path

# (Doesn't matter now because download is optional)
FILE_URL = "https://pixeldrain.com/u/HXtFKpF3"

ZIP_NAME = "COTA_lap_end_time_R1.zip"
EXTRACT_DIR = "race_data"


def download_dataset():
    print("📥 Downloading dataset...")

    try:
        response = requests.get(FILE_URL, stream=True, timeout=15)
        response.raise_for_status()
    except Exception as e:
        print("❌ Dataset download failed:", e)
        print("⚠️ Skipping download. Using local dataset if available.")
        return False

    # If response is not OK
    if not response.ok:
        print("❌ Download returned non-OK status. Using local dataset.")
        return False

    # Save ZIP
    try:
        with open(ZIP_NAME, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print("✅ Downloaded dataset")
        return True
    except Exception as e:
        print("❌ Failed to save dataset ZIP:", e)
        return False


def extract_dataset():
    print("📦 Extracting dataset...")

    try:
        Path(EXTRACT_DIR).mkdir(exist_ok=True)

        with zipfile.ZipFile(ZIP_NAME, "r") as zip_ref:
            zip_ref.extractall(EXTRACT_DIR)

        os.remove(ZIP_NAME)
        print("🗑️ Removed ZIP file")

        return True
    except Exception as e:
        print("❌ Failed to extract ZIP:", e)
        return False


def verify_dataset():
    print("🔍 Verifying dataset...")

    race1 = Path(EXTRACT_DIR) / "COTA" / "Race1"

    if race1.exists():
        print("✅ Found dataset folder:", race1)
    else:
        print("❌ Race1 NOT found inside extracted folder")


def download_race_data():
    # If dataset already exists, skip downloading
    if Path(EXTRACT_DIR).exists() and len(list(Path(EXTRACT_DIR).glob("**/*.csv"))) > 0:
        print("✅ Dataset already exists")
        verify_dataset()
        return True

    print("⬇️ Dataset missing — attempting download...")

    ok = download_dataset()
    if not ok:
        print("⚠️ Download skipped due to error. Using existing local files.")
        return False

    ok = extract_dataset()
    if not ok:
        print("⚠️ Extraction failed. Backend will still run using local files.")
        return False

    verify_dataset()
    return True
