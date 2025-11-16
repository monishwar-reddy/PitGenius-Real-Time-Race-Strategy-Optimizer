"""Quick test script to verify API functionality"""
import sys
from pathlib import Path

# Test imports
try:
    from data_processor import RaceDataProcessor
    from strategy_engine import StrategyEngine
    print("✅ All imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

# Test data loading
try:
    race_folder = Path("../COTA/Race 1")
    if not race_folder.exists():
        race_folder = Path("COTA/Race 1")
    
    if not race_folder.exists():
        print("❌ COTA data folder not found")
        sys.exit(1)
    
    processor = RaceDataProcessor(str(race_folder))
    processor.load_all_data()
    print("✅ Data loaded successfully")
    
    # Test driver data
    drivers = processor.get_all_drivers()
    print(f"✅ Found {len(drivers)} drivers")
    
    if len(drivers) > 0:
        test_driver = drivers[0]
        print(f"✅ Test driver: #{test_driver['number']}")
        
        # Test lap times
        vehicle_ids = processor.lap_times_df['vehicle_id'].unique()
        if len(vehicle_ids) > 0:
            test_vehicle = vehicle_ids[0]
            lap_times = processor.get_driver_lap_times(test_vehicle)
            print(f"✅ Lap times loaded: {len(lap_times)} laps")
            
            # Test tire degradation
            tire_deg = processor.get_tire_degradation(test_vehicle)
            print(f"✅ Tire degradation: {tire_deg['degradation_rate']:.3f}s/lap")
            
            # Test strategy engine
            engine = StrategyEngine()
            windows = engine.calculate_optimal_pit_window(
                current_lap=5,
                total_laps=17,
                lap_times=tire_deg['laps'],
                degradation_rate=tire_deg['degradation_rate'],
                competitors=[],
                weather={}
            )
            print(f"✅ Strategy calculation: {len(windows)} pit windows")
            
            for i, window in enumerate(windows, 1):
                print(f"   Window {i}: Laps {window.lap_start}-{window.lap_end}, "
                      f"P{window.predicted_position}, {window.confidence*100:.0f}% confidence")
    
    print("\n🏁 All tests passed! API is ready to run.")
    print("\nTo start the API server, run:")
    print("  python api.py")
    
except Exception as e:
    print(f"❌ Error during testing: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
