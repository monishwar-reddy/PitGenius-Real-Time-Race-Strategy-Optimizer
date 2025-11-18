import os
import requests
import zipfile
from pathlib import Path

FILE_URL = "https://pixeldrain.com/u/9EqAZsMc"
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


def find_race1_folder():
    """
    Automatically find folder even if user named it:
    Race 1 / race 1 / Race1 / race1 / RACE 1 / RACE1
    """

    base = Path(EXTRACT_DIR) / "COTA"

    if not base.exists():
        return None

    for folder in base.iterdir():
        name = folder.name.replace(" ", "").lower()
        if name == "race1":
            return folder

    return None


def verify_dataset():
    print("🔍 Verifying dataset...")

    race1 = find_race1_folder()

    if race1:
        print("✅ Found Race1 folder:", race1)
        return True

    print("❌ Race1 NOT found inside extracted folder")
    return False


def download_race_data():
    # If dataset already exists, skip downloading
    if Path(EXTRACT_DIR).exists():
        print("🟡 Local dataset folder exists, scanning...")
        if verify_dataset():
            print("✅ Using existing local dataset")
            return True
        else:
            print("⚠️ Local dataset invalid or incomplete. Attempting download...")

    ok = download_dataset()
    if not ok:
        print("⚠️ Download skipped due to error. Using local files (if any).")
        return False

    ok = extract_dataset()
    if not ok:
        print("⚠️ Extraction failed. Backend will still run using local files.")
        return False

    if not verify_dataset():
        print("❌ Dataset structure wrong. Backend cannot load dataset.")
        return False

    return True

