from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import sys
from pathlib import Path

from backend.data_processor import RaceDataProcessor
from backend.strategy_engine import StrategyEngine
from backend.data_downloader import download_race_data


app = FastAPI(title="PitGenius API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global data processor
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
    """Load race data on startup"""
    global processor

    print("⚠️ Skipping dataset download — using local files only.")

    # -----------------------------
    # FIXED FOLDER PATH HANDLING
    # -----------------------------
    possible_paths = [
        Path("race_data/COTA/Race1"),
        Path("race_data/COTA/Race 1"),
        Path("race_data/Race1"),
        Path("COTA/Race1"),
        Path("COTA/Race 1"),
        Path("../COTA/Race1"),
        Path("../COTA/Race 1"),
    ]

    race_folder = None
    for path in possible_paths:
        if path.exists():
            race_folder = path
            print(f"✅ Using dataset folder: {path}")
            break

    if race_folder is None:
        print("❌ Could not find Race1 folder. Backend cannot load dataset.")
        raise Exception("Race1 folder not found. Check your folder structure.")

    # Initialize processor
    processor = RaceDataProcessor(str(race_folder))
    processor.load_all_data()
    print("✅ Race data loaded successfully")


@app.get("/")
async def root():
    return {
        "message": "PitGenius API - Real-Time Race Strategy Optimizer",
        "version": "1.0.0",
        "status": "operational"
    }


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
        import math

        vehicle_ids = processor.lap_times_df['vehicle_id'].unique()
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

        lap_times_clean = lap_times.replace({float('nan'): None, float('inf'): None, float('-inf'): None})
        sectors_clean = sectors.replace({float('nan'): None, float('inf'): None, float('-inf'): None})

        tire_deg_clean = {
            'degradation_rate': tire_deg['degradation_rate'] if not math.isnan(tire_deg['degradation_rate']) and not math.isinf(tire_deg['degradation_rate']) else 0.0,
            'laps': [x if not math.isnan(x) and not math.isinf(x) else 0.0 for x in tire_deg.get('laps', [])],
            'trend': [x if not math.isnan(x) and not math.isinf(x) else 0.0 for x in tire_deg.get('trend', [])]
        }

        return {
            "vehicle_id": matching_vehicle,
            "vehicle_number": vehicle_number,
            "lap_times": lap_times_clean.to_dict('records'),
            "tire_degradation": tire_deg_clean,
            "sector_performance": sectors_clean.to_dict('records')[:10]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/strategy/calculate")
async def calculate_strategy(request: StrategyRequest):
    try:
        lap_times_df = processor.get_driver_lap_times(request.vehicle_id)
        lap_times = lap_times_df['lap_time_seconds'].tolist()

        tire_deg = processor.get_tire_degradation(request.vehicle_id)
        weather = processor.get_weather_at_time("")

        all_drivers = processor.get_all_drivers()
        competitors = [d for d in all_drivers if d.get('best_lap')]

        windows = strategy_engine.calculate_optimal_pit_window(
            current_lap=request.current_lap,
            total_laps=request.total_laps,
            lap_times=lap_times,
            degradation_rate=tire_deg['degradation_rate'],
            competitors=competitors,
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
            ],
            "tire_degradation_rate": tire_deg['degradation_rate'],
            "weather": weather
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/strategy/pit-now")
async def should_pit_now(request: PitDecisionRequest):
    try:
        lap_times_df = processor.get_driver_lap_times(request.vehicle_id)
        lap_times = lap_times_df['lap_time_seconds'].tolist()

        tire_deg = processor.get_tire_degradation(request.vehicle_id)

        should_pit, reason = strategy_engine.should_pit_now(
            current_lap=request.current_lap,
            lap_times=lap_times,
            degradation_rate=tire_deg['degradation_rate'],
            gap_to_car_behind=request.gap_to_behind,
            weather_changing=request.weather_changing
        )

        return {
            "should_pit": should_pit,
            "reason": reason,
            "degradation_rate": tire_deg['degradation_rate'],
            "current_lap": request.current_lap
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/weather/current")
async def get_current_weather():
    try:
        weather = processor.get_weather_at_time("")
        return weather
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/race/summary")
async def get_race_summary():
    try:
        drivers = processor.get_all_drivers()
        weather = processor.get_weather_at_time("")

        all_deg_rates = []
        for driver in drivers:
            vehicle_ids = processor.lap_times_df['vehicle_id'].unique()
            for vid in vehicle_ids:
                if str(driver['number']) in vid:
                    deg = processor.get_tire_degradation(vid)
                    if deg['degradation_rate'] > 0:
                        all_deg_rates.append(deg['degradation_rate'])
                    break

        avg_degradation = sum(all_deg_rates) / len(all_deg_rates) if all_deg_rates else 0

        return {
            "total_drivers": len(drivers),
            "weather": weather,
            "average_tire_degradation": avg_degradation,
            "track_status": "Green" if weather.get('track_temp', 0) < 50 else "Hot"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
