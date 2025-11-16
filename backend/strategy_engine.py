import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class PitWindow:
    lap_start: int
    lap_end: int
    time_loss: float
    predicted_position: int
    confidence: float
    reason: str

class StrategyEngine:
    def __init__(self):
        self.pit_stop_time = 45.0  # Average pit stop time in seconds
        self.tire_cliff_threshold = 0.5  # Degradation rate threshold
        
    def calculate_optimal_pit_window(
        self, 
        current_lap: int,
        total_laps: int,
        lap_times: List[float],
        degradation_rate: float,
        competitors: List[Dict],
        weather: Dict
    ) -> List[PitWindow]:
        """Calculate optimal pit stop windows"""
        
        windows = []
        
        # Strategy 1: Early pit (laps 5-8)
        if current_lap <= 5:
            early_window = self._evaluate_pit_window(
                pit_lap=6,
                current_lap=current_lap,
                total_laps=total_laps,
                lap_times=lap_times,
                degradation_rate=degradation_rate,
                competitors=competitors,
                strategy_name="Early Undercut"
            )
            windows.append(early_window)
        
        # Strategy 2: Mid-race pit (laps 9-12)
        if current_lap <= 9:
            mid_window = self._evaluate_pit_window(
                pit_lap=10,
                current_lap=current_lap,
                total_laps=total_laps,
                lap_times=lap_times,
                degradation_rate=degradation_rate,
                competitors=competitors,
                strategy_name="Standard Strategy"
            )
            windows.append(mid_window)
        
        # Strategy 3: Late pit (laps 13-15)
        if current_lap <= 13:
            late_window = self._evaluate_pit_window(
                pit_lap=14,
                current_lap=current_lap,
                total_laps=total_laps,
                lap_times=lap_times,
                degradation_rate=degradation_rate,
                competitors=competitors,
                strategy_name="Long First Stint"
            )
            windows.append(late_window)
        
        # Sort by predicted position
        windows.sort(key=lambda x: x.predicted_position)
        
        return windows
    
    def _evaluate_pit_window(
        self,
        pit_lap: int,
        current_lap: int,
        total_laps: int,
        lap_times: List[float],
        degradation_rate: float,
        competitors: List[Dict],
        strategy_name: str
    ) -> PitWindow:
        """Evaluate a specific pit window"""
        
        if len(lap_times) == 0:
            base_lap_time = 150.0
        else:
            base_lap_time = np.median(lap_times[-5:]) if len(lap_times) >= 5 else np.median(lap_times)
        
        # Calculate time to pit lap
        laps_to_pit = pit_lap - current_lap
        time_to_pit = 0
        
        for i in range(laps_to_pit):
            lap_deg = degradation_rate * (current_lap + i - 1)
            time_to_pit += base_lap_time + lap_deg
        
        # Add pit stop time
        total_time_with_pit = time_to_pit + self.pit_stop_time
        
        # Calculate remaining laps on fresh tires
        remaining_laps = total_laps - pit_lap
        time_after_pit = 0
        
        for i in range(remaining_laps):
            # Fresh tires, less degradation
            lap_deg = (degradation_rate * 0.3) * i  # 70% less degradation on new tires
            time_after_pit += base_lap_time - 2.0 + lap_deg  # 2 second advantage on fresh tires
        
        total_race_time = total_time_with_pit + time_after_pit
        
        # Estimate position based on competitors
        predicted_position = self._estimate_position(total_race_time, competitors)
        
        # Calculate confidence based on various factors
        confidence = self._calculate_confidence(
            pit_lap, current_lap, total_laps, degradation_rate
        )
        
        return PitWindow(
            lap_start=max(pit_lap - 1, current_lap + 1),
            lap_end=min(pit_lap + 1, total_laps - 3),
            time_loss=self.pit_stop_time,
            predicted_position=predicted_position,
            confidence=confidence,
            reason=strategy_name
        )
    
    def _estimate_position(self, race_time: float, competitors: List[Dict]) -> int:
        """Estimate finishing position based on race time"""
        position = 1
        for comp in competitors:
            if comp.get('estimated_time', race_time + 10) < race_time:
                position += 1
        return position
    
    def _calculate_confidence(
        self, 
        pit_lap: int, 
        current_lap: int, 
        total_laps: int,
        degradation_rate: float
    ) -> float:
        """Calculate confidence score for strategy"""
        
        # Base confidence
        confidence = 0.7
        
        # Higher confidence if degradation is high
        if degradation_rate > self.tire_cliff_threshold:
            confidence += 0.15
        
        # Lower confidence if too early in race
        if current_lap < 3:
            confidence -= 0.2
        
        # Lower confidence if pit too late
        if pit_lap > total_laps - 3:
            confidence -= 0.25
        
        return max(0.3, min(0.95, confidence))
    
    def should_pit_now(
        self,
        current_lap: int,
        lap_times: List[float],
        degradation_rate: float,
        gap_to_car_behind: float,
        weather_changing: bool
    ) -> Tuple[bool, str]:
        """Determine if car should pit immediately"""
        
        # Critical tire degradation
        if degradation_rate > self.tire_cliff_threshold * 1.5:
            return True, "CRITICAL: Tire degradation exceeding safe limits"
        
        # Undercut opportunity
        if gap_to_car_behind > self.pit_stop_time + 5:
            return True, "OPPORTUNITY: Gap sufficient for undercut"
        
        # Weather change incoming
        if weather_changing:
            return True, "WEATHER: Conditions changing, pit recommended"
        
        # Lap time falling off cliff
        if len(lap_times) >= 3:
            recent_avg = np.mean(lap_times[-3:])
            best_avg = np.mean(sorted(lap_times)[:5]) if len(lap_times) >= 5 else np.mean(lap_times)
            
            if recent_avg > best_avg + 3.0:
                return True, "PERFORMANCE: Lap times degrading significantly"
        
        return False, "Continue current stint"
    
    def calculate_fuel_strategy(
        self,
        current_lap: int,
        total_laps: int,
        fuel_consumption_per_lap: float,
        current_fuel: float
    ) -> Dict:
        """Calculate fuel strategy"""
        
        remaining_laps = total_laps - current_lap
        fuel_needed = remaining_laps * fuel_consumption_per_lap
        
        fuel_margin = current_fuel - fuel_needed
        
        return {
            'fuel_needed': fuel_needed,
            'current_fuel': current_fuel,
            'margin': fuel_margin,
            'laps_remaining': remaining_laps,
            'can_finish': fuel_margin > 0,
            'fuel_save_required': fuel_margin < fuel_consumption_per_lap
        }
