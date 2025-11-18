from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
from typing import List, Optional, Dict
import math

from backend.data_processor import RaceDataProcessor
from backend.strategy_engine import StrategyEngine


app = FastAPI(title="PitGenius API", version="1.0.0")

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Globals
processor = None
strategy_engine = StrategyEngine()


class StrategyRequest(BaseModel):
    vehicle_id: str
    current_lap: int
    total_laps: int = 17


class PitDecisionRequest(BaseModel):
    vehicle_id: str
    current_lap: int
    gap_to_behind: float
    weather_changing: bool = False



@app.on_event("startup")
async def startup_event():
    """
    Auto-detect the Race1 dataset folder anywhere in the project.
    Works locally and inside Docker/Render.
    """
    global processor

    print("\n⚠️ Using LOCAL DATASETS only.\n")

    # List all possible dataset folder names
    possible_names = ["Race1", "Race 1"]

    # Start search from project root (/app/)
    project_root = Path(__file__).resolve().parents[1]

    print(f"🔍 Searching for Race1 folder under: {project_root}")

    race_folder = None

    # Walk entire project directory
    for path in project_root.rglob("*"):
        if path.is_dir() and path.name in possible_names:
            race_folder = path
            break

    if race_folder is None:
        raise Exception(
            "❌ Race1 folder NOT FOUND anywhere in the project.\n"
            "Put your files inside ANY of these paths:\n"
            "- race_data/COTA/Race1\n"
            "- backend/race_data/COTA/Race1\n"
            "- COTA/Race1\n"
            "- ANYWHERE/Race1 (auto-detected)\n"
        )

    print(f"✅ FOUND DATASET FOLDER: {race_folder}")

    processor = RaceDataProcessor(str(race_folder))
    processor.load_all_data()

    print("✅ Race data loaded successfully!\n")




@app.get("/")
async def root():
    return {"message": "PitGenius API Running", "version": "1.0.0"}



@app.get("/drivers")
async def get_drivers():
    try:
        drivers = processor.get_all_drivers()
        return {"drivers": drivers, "count": len(drivers)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/driver/{vehicle_number}/performance")
async def get_driver_performance(vehicle_number: int):
    try:
        # Try matching partial vehicle IDs (your CSV uses strings)
        vehicle_ids = processor.lap_times_df["vehicle_id"].unique()
        matching_vehicle = None

        for vid in vehicle_ids:
            if str(vehicle_number) in vid:
                matching_vehicle = vid
                break

        if not matching_vehicle:
            raise HTTPException(status_code=404, detail="Driver not found")

        lap_times = processor.get_driver_lap_times(matching_vehicle)
        tire_deg = processor.get_tire_degradation(matching_vehicle)
        sectors = processor.get_sector_performance(vehicle_number)

        # Cleanup
        lap_times_clean = lap_times.replace({math.nan: None, math.inf: None, -math.inf: None})
        sectors_clean = sectors.replace({math.nan: None, math.inf: None, -math.inf: None})

        # Clean tire degradation
        deg_rate = tire_deg["degradation_rate"]
        if math.isnan(deg_rate) or math.isinf(deg_rate):
            deg_rate = 0.0

        tire_deg_clean = {
            "degradation_rate": deg_rate,
            "laps": [x if x == x and not math.isinf(x) else 0.0 for x in tire_deg.get("laps", [])],
            "trend": [x if x == x and not math.isinf(x) else 0.0 for x in tire_deg.get("trend", [])]
        }

        return {
            "vehicle_id": matching_vehicle,
            "vehicle_number": vehicle_number,
            "lap_times": lap_times_clean.to_dict("records"),
            "tire_degradation": tire_deg_clean,
            "sector_performance": sectors_clean.to_dict("records")[:10]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/strategy/calculate")
async def calculate_strategy(request: StrategyRequest):
    try:
        lap_times_df = processor.get_driver_lap_times(request.vehicle_id)
        lap_times = lap_times_df["lap_time_seconds"].tolist()

        tire_deg = processor.get_tire_degradation(request.vehicle_id)
        weather = processor.get_weather_at_time("")

        all_drivers = processor.get_all_drivers()

        windows = strategy_engine.calculate_optimal_pit_window(
            current_lap=request.current_lap,
            total_laps=request.total_laps,
            lap_times=lap_times,
            degradation_rate=tire_deg["degradation_rate"],
            competitors=all_drivers,
            weather=weather
        )

        return {
            "vehicle_id": request.vehicle_id,
            "current_lap": request.current_lap,
            "pit_windows": [
                {
                    "lap_start": w.lap_start,
                    "lap_end": w.lap_end,
                    "time_loss": w.time_loss,
                    "predicted_position": w.predicted_position,
                    "confidence": w.confidence,
                    "reason": w.reason
                }
                for w in windows
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/strategy/pit-now")
async def should_pit_now(request: PitDecisionRequest):
    try:
        lap_times_df = processor.get_driver_lap_times(request.vehicle_id)
        lap_times = lap_times_df["lap_time_seconds"].tolist()

        tire_deg = processor.get_tire_degradation(request.vehicle_id)

        should_pit, reason = strategy_engine.should_pit_now(
            current_lap=request.current_lap,
            lap_times=lap_times,
            degradation_rate=tire_deg["degradation_rate"],
            gap_to_car_behind=request.gap_to_behind,
            weather_changing=request.weather_changing
        )

        return {
            "should_pit": should_pit,
            "reason": reason,
            "degradation_rate": tire_deg["degradation_rate"]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/weather/current")
async def get_current_weather():
    try:
        return processor.get_weather_at_time("")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/race/summary")
async def get_race_summary():
    try:
        drivers = processor.get_all_drivers()
        weather = processor.get_weather_at_time("")

        rates = []
        for d in drivers:
            for vid in processor.lap_times_df["vehicle_id"].unique():
                if str(d["number"]) in vid:
                    deg = processor.get_tire_degradation(vid)
                    if deg["degradation_rate"] > 0:
                        rates.append(deg["degradation_rate"])
                    break

        avg_deg = sum(rates) / len(rates) if rates else 0

        return {
            "total_drivers": len(drivers),
            "weather": weather,
            "average_tire_degradation": avg_deg
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.get("/debug/files")
async def debug_files():
    import os

    tree = []
    for root, dirs, files in os.walk("/app", topdown=True):
        path = root.replace("/app", "")
        tree.append({
            "path": path if path else "/",
            "dirs": dirs,
            "files": files
        })

    return tree




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


