import os
import requests
import zipfile
from pathlib import Path

FILE_URL = "https://pixeldrain.com/u/HXtFKpF3"
ZIP_NAME = "COTA_lap_end_time_R1.zip"

# Extract into root folder "COTA"
EXTRACT_DIR = "COTA"


def download_dataset():
    print("📥 Downloading dataset...")

    try:
        response = requests.get(FILE_URL, stream=True, timeout=15)
        response.raise_for_status()
    except Exception as e:
        print("❌ Dataset download failed:", e)
        print("⚠️ Skipping download. Using local dataset if available.")
        return False

    if not response.ok:
        print("❌ Download returned non-OK status. Using local dataset.")
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

        with zipfile.ZipFile(ZIP_NAME, "r") as z:
            z.extractall(EXTRACT_DIR)

        os.remove(ZIP_NAME)
        print("🗑️ Removed ZIP file")

        return True

    except Exception as e:
        print("❌ Failed to extract ZIP:", e)
        return False


def verify_dataset():
    print("🔍 Verifying dataset...")

    race1 = Path(EXTRACT_DIR) / "Race1"   # ✔ correct folder name

    if not race1.exists():
        print("❌ Race1 folder NOT found")
        return False

    print(f"✅ Found dataset folder: {race1}")

    expected_files = [
        "R1_cota_telemetry_data.csv",
        "COTA_lap_time_R1.csv",
        "26_Weather_Race 1_Anonymized.CSV",
        "23_AnalysisEnduranceWithSections_Race 1_Anonymized.CSV",
        "99_Best 10 Laps By Driver_Race 1_Anonymized.CSV",
    ]

    print("\n🔍 Checking files inside Race1:")

    for fname in expected_files:
        fpath = race1 / fname
        if fpath.exists():
            print(f"✅ Found {fname}")
        else:
            print(f"❌ Missing {fname}")

    return True


def download_race_data():
    # If CSV files already exist, skip download
    if Path(EXTRACT_DIR).exists() and len(list(Path(EXTRACT_DIR).glob("Race1/*.csv"))) > 0:
        print("✅ Dataset already exists — skipping download")
        verify_dataset()
        return True

    print("⬇️ Dataset missing — attempting download...")

    ok = download_dataset()
    if not ok:
        print("⚠️ Download failed or skipped, using local files if available.")
        return False

    ok = extract_dataset()
    if not ok:
        print("⚠️ Extraction failed. Using local files.")
        return False

    verify_dataset()
    return True
