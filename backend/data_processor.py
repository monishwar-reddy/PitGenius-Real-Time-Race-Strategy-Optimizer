import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple

class RaceDataProcessor:
    def __init__(self, race_folder: str):
        self.race_folder = Path(race_folder)
        self.telemetry_df = None
        self.lap_times_df = None
        self.weather_df = None
        self.sectors_df = None
        self.results_df = None
        
    def load_all_data(self):
        """Load all race data files"""
        print("Loading race data...")
        
        # Telemetry data
        telemetry_file = list(self.race_folder.glob("*telemetry_data.csv"))[0]
        self.telemetry_df = pd.read_csv(telemetry_file)
        print(f"Loaded {len(self.telemetry_df)} telemetry records")
        
        # Lap times
        lap_time_file = list(self.race_folder.glob("*lap_time*.csv"))[0]
        self.lap_times_df = pd.read_csv(lap_time_file)
        print(f"Loaded {len(self.lap_times_df)} lap time records")
        
        # Weather
        weather_file = list(self.race_folder.glob("*Weather*.CSV"))[0]
        self.weather_df = pd.read_csv(weather_file, sep=';')
        print(f"Loaded {len(self.weather_df)} weather records")
        
        # Sector analysis
        sectors_file = list(self.race_folder.glob("*AnalysisEndurance*.CSV"))[0]
        self.sectors_df = pd.read_csv(sectors_file, sep=';')
        print(f"Loaded {len(self.sectors_df)} sector records")
        
        # Best laps
        best_laps_file = list(self.race_folder.glob("*Best 10 Laps*.CSV"))[0]
        self.results_df = pd.read_csv(best_laps_file, sep=';')
        print(f"Loaded {len(self.results_df)} driver records")
        
        return self
    
    def get_driver_lap_times(self, vehicle_id: str) -> pd.DataFrame:
        """Get lap times for specific driver"""
        driver_laps = self.lap_times_df[
            self.lap_times_df['vehicle_id'] == vehicle_id
        ].copy()
        driver_laps['lap_time_seconds'] = driver_laps['value'] / 1000
        driver_laps = driver_laps.sort_values('lap')
        return driver_laps
    
    def get_tire_degradation(self, vehicle_id: str) -> Dict:
        """Calculate tire degradation from lap times"""
        laps = self.get_driver_lap_times(vehicle_id)
        
        if len(laps) < 5:
            return {'degradation_rate': 0, 'laps': []}
        
        # Filter out outliers (pit laps, incidents)
        lap_times = laps['lap_time_seconds'].values
        median = np.median(lap_times)
        filtered = lap_times[(lap_times < median * 1.2) & (lap_times > median * 0.8)]
        
        if len(filtered) < 3:
            return {'degradation_rate': 0, 'laps': lap_times.tolist()}
        
        # Calculate degradation rate (seconds per lap)
        x = np.arange(len(filtered))
        coeffs = np.polyfit(x, filtered, 1)
        degradation_rate = coeffs[0]
        
        return {
            'degradation_rate': float(degradation_rate),
            'laps': lap_times.tolist(),
            'trend': coeffs.tolist()
        }
    
    def get_sector_performance(self, vehicle_number: int) -> pd.DataFrame:
        """Get sector times for driver"""
        driver_sectors = self.sectors_df[
            self.sectors_df['NUMBER'] == vehicle_number
        ].copy()
        
        # Convert sector times to float and fill NaN with None
        for col in ['S1_SECONDS', 'S2_SECONDS', 'S3_SECONDS']:
            if col in driver_sectors.columns:
                driver_sectors[col] = pd.to_numeric(driver_sectors[col], errors='coerce')
        
        # Replace NaN with None for JSON serialization
        driver_sectors = driver_sectors.fillna('')
        
        return driver_sectors
    
    def get_weather_at_time(self, timestamp: str) -> Dict:
        """Get weather conditions at specific time"""
        if len(self.weather_df) == 0:
            return {}
        
        # Return latest weather data
        latest = self.weather_df.iloc[-1]
        
        def safe_float(val, default=0.0):
            try:
                result = float(val)
                return result if not pd.isna(result) else default
            except:
                return default
        
        return {
            'air_temp': safe_float(latest['AIR_TEMP'], 25.0),
            'track_temp': safe_float(latest['TRACK_TEMP'], 35.0),
            'humidity': safe_float(latest['HUMIDITY'], 50.0),
            'wind_speed': safe_float(latest['WIND_SPEED'], 10.0)
        }
    
    def get_all_drivers(self) -> List[Dict]:
        """Get list of all drivers"""
        drivers = []
        for _, row in self.results_df.iterrows():
            if row['TOTAL_DRIVER_LAPS'] > 0:
                # Parse lap time in format "2:31.035" to seconds
                best_lap = None
                if pd.notna(row['BESTLAP_1']) and row['BESTLAP_1']:
                    try:
                        lap_str = str(row['BESTLAP_1'])
                        if ':' in lap_str:
                            parts = lap_str.split(':')
                            minutes = int(parts[0])
                            seconds = float(parts[1])
                            best_lap = minutes * 60 + seconds
                        else:
                            best_lap = float(lap_str)
                    except:
                        best_lap = None
                
                drivers.append({
                    'number': int(row['NUMBER']),
                    'vehicle': row['VEHICLE'],
                    'class': row['CLASS'],
                    'total_laps': int(row['TOTAL_DRIVER_LAPS']),
                    'best_lap': best_lap
                })
        return drivers
    
    def get_telemetry_summary(self, vehicle_id: str, lap: int) -> Dict:
        """Get telemetry summary for specific lap"""
        lap_telemetry = self.telemetry_df[
            (self.telemetry_df['vehicle_id'] == vehicle_id) & 
            (self.telemetry_df['lap'] == lap)
        ]
        
        if len(lap_telemetry) == 0:
            return {}
        
        # Calculate key metrics
        speed_data = lap_telemetry[lap_telemetry['telemetry_name'] == 'vcar_can']
        brake_data = lap_telemetry[lap_telemetry['telemetry_name'].str.contains('brake', na=False)]
        accel_data = lap_telemetry[lap_telemetry['telemetry_name'] == 'accx_can']
        
        return {
            'avg_speed': float(speed_data['telemetry_value'].mean()) if len(speed_data) > 0 else 0,
            'max_speed': float(speed_data['telemetry_value'].max()) if len(speed_data) > 0 else 0,
            'brake_applications': int(len(brake_data)),
            'avg_accel': float(accel_data['telemetry_value'].mean()) if len(accel_data) > 0 else 0
        }
