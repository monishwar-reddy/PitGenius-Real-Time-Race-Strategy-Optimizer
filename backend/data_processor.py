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
        
    def _find_file(self, patterns: List[str]):
        """Search for first matching file safely."""
        for p in patterns:
            files = list(self.race_folder.glob(p))
            if files:
                return files[0]
        print(f"❌ File not found for patterns: {patterns}")
        return None

    def load_all_data(self):
        print("🔍 Scanning dataset folder:", self.race_folder)

        # Telemetry
        telemetry_file = self._find_file([
            "*telemetry*.csv", "*Telemetry*.csv", "*TELEMETRY*.csv"
        ])
        if telemetry_file:
            self.telemetry_df = pd.read_csv(telemetry_file)
            print(f"✅ Telemetry loaded: {len(self.telemetry_df)} rows")

        # Lap times
        lap_time_file = self._find_file([
            "*lap*.csv", "*Lap*.csv", "*LAP*.csv"
        ])
        if lap_time_file:
            self.lap_times_df = pd.read_csv(lap_time_file)
            print(f"✅ Lap times loaded: {len(self.lap_times_df)} rows")

        # Weather
        weather_file = self._find_file([
            "*Weather*.csv", "*WEATHER*.csv", "*weather*.csv"
        ])
        if weather_file:
            self.weather_df = pd.read_csv(weather_file, sep=';')
            print(f"✅ Weather loaded: {len(self.weather_df)} rows")

        # Sector analysis
        sectors_file = self._find_file([
            "*Analysis*.csv", "*Sector*.csv", "*SECTOR*.csv"
        ])
        if sectors_file:
            self.sectors_df = pd.read_csv(sectors_file, sep=';')
            print(f"✅ Sector analysis loaded: {len(self.sectors_df)} rows")

        # Best laps / results
        results_file = self._find_file([
            "*Best*.csv", "*Result*.csv", "*RESULT*.csv"
        ])
        if results_file:
            self.results_df = pd.read_csv(results_file, sep=';')
            print(f"✅ Driver results loaded: {len(self.results_df)} rows")

        print("📦 Dataset loaded (missing files were skipped safely).")
        return self

    def get_driver_lap_times(self, vehicle_id: str) -> pd.DataFrame:
        if self.lap_times_df is None:
            return pd.DataFrame()

        driver_laps = self.lap_times_df[
            self.lap_times_df['vehicle_id'] == vehicle_id
        ].copy()

        if 'value' in driver_laps.columns:
            driver_laps['lap_time_seconds'] = driver_laps['value'] / 1000
        
        return driver_laps.sort_values('lap')

    def get_tire_degradation(self, vehicle_id: str) -> Dict:
        laps = self.get_driver_lap_times(vehicle_id)
        if len(laps) < 5:
            return {'degradation_rate': 0, 'laps': []}

        lap_times = laps['lap_time_seconds'].values
        median = np.median(lap_times)
        filtered = lap_times[(lap_times < median * 1.2) & (lap_times > median * 0.8)]

        if len(filtered) < 3:
            return {'degradation_rate': 0, 'laps': lap_times.tolist()}

        x = np.arange(len(filtered))
        coeffs = np.polyfit(x, filtered, 1)

        return {
            'degradation_rate': float(coeffs[0]),
            'laps': lap_times.tolist(),
            'trend': coeffs.tolist()
        }

    def get_sector_performance(self, vehicle_number: int) -> pd.DataFrame:
        if self.sectors_df is None:
            return pd.DataFrame()

        driver = self.sectors_df[self.sectors_df['NUMBER'] == vehicle_number].copy()

        for col in ['S1_SECONDS', 'S2_SECONDS', 'S3_SECONDS']:
            if col in driver.columns:
                driver[col] = pd.to_numeric(driver[col], errors='coerce')

        return driver.fillna('')

    def get_weather_at_time(self, timestamp: str) -> Dict:
        if self.weather_df is None or len(self.weather_df) == 0:
            return {}

        latest = self.weather_df.iloc[-1]

        def safe_float(val, default=0.0):
            try:
                v = float(val)
                return v if not pd.isna(v) else default
            except:
                return default

        return {
            'air_temp': safe_float(latest.get('AIR_TEMP', 25)),
            'track_temp': safe_float(latest.get('TRACK_TEMP', 35)),
            'humidity': safe_float(latest.get('HUMIDITY', 50)),
            'wind_speed': safe_float(latest.get('WIND_SPEED', 10)),
        }

    def get_all_drivers(self) -> List[Dict]:
        if self.results_df is None:
            return []

        drivers = []
        for _, row in self.results_df.iterrows():
            if 'TOTAL_DRIVER_LAPS' in row and row['TOTAL_DRIVER_LAPS'] > 0:

                best_lap = None
                lap_str = str(row.get('BESTLAP_1', ''))
                if ":" in lap_str:
                    try:
                        m, s = lap_str.split(":")
                        best_lap = int(m) * 60 + float(s)
                    except:
                        best_lap = None

                drivers.append({
                    'number': int(row.get('NUMBER', -1)),
                    'vehicle': row.get('VEHICLE', ''),
                    'class': row.get('CLASS', ''),
                    'total_laps': int(row.get('TOTAL_DRIVER_LAPS', 0)),
                    'best_lap': best_lap
                })
        return drivers

    def get_telemetry_summary(self, vehicle_id: str, lap: int) -> Dict:
        if self.telemetry_df is None:
            return {}

        df = self.telemetry_df[
            (self.telemetry_df['vehicle_id'] == vehicle_id) & 
            (self.telemetry_df['lap'] == lap)
        ]

        if len(df) == 0:
            return {}

        speed = df[df['telemetry_name'] == 'vcar_can']
        brake = df[df['telemetry_name'].str.contains("brake", na=False)]
        accel = df[df['telemetry_name'] == 'accx_can']

        return {
            'avg_speed': float(speed['telemetry_value'].mean()) if len(speed) else 0,
            'max_speed': float(speed['telemetry_value'].max()) if len(speed) else 0,
            'brake_applications': int(len(brake)),
            'avg_accel': float(accel['telemetry_value'].mean()) if len(accel) else 0
        }
