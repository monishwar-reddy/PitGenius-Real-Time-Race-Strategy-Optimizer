# 🏁 PitGenius - Real-Time Race Strategy Optimizer

**Toyota Racing Development - Hack the Track 2025**

PitGenius is an AI-powered real-time race strategy tool that helps race engineers and drivers make optimal pit stop decisions during GR Cup races. Using 17+ million telemetry data points, tire degradation analysis, and predictive algorithms, PitGenius calculates the perfect pit window to maximize track position.

![Workflow]<img width="1897" height="1024" alt="Screenshot 2025-11-19 090454" src="https://github.com/user-attachments/assets/a6ecb9fa-1c18-43ab-9463-635c2acc5b5b" />

## 🎯 Category: Real-Time Analytics

## 🚀 Quick Start (2 Minutes)

### Automated Setup (Windows)
```bash
start.bat
```

### Manual Setup
```bash
# Terminal 1 - Backend
cd backend
pip install -r requirements.txt
python api.py

# Terminal 2 - Frontend  
cd frontend
npm install
npm run dev
```

**Open browser**: http://localhost:3000

## 🚀 Key Features

### 1. **Dynamic Pit Window Calculator**
- Calculates optimal pit stop windows in real-time
- Evaluates multiple strategies: Early Undercut, Standard, Long First Stint
- Predicts finishing position for each strategy
- Confidence scoring based on track conditions and tire degradation

### 2. **Tire Degradation Predictor**
- Analyzes lap time trends to calculate degradation rate
- Alerts when tires reach critical degradation threshold
- Predicts performance drop-off for remaining laps

### 3. **Live Performance Metrics**
- Real-time lap time analysis with trend visualization
- Sector-by-sector performance breakdown
- Consistency metrics and delta analysis
- Best lap tracking and comparison

### 4. **Race Simulation**
- Simulate race progression lap-by-lap
- See how pit strategy recommendations change over time
- Test "what-if" scenarios

### 5. **Weather Impact Analysis**
- Track temperature and air temperature monitoring
- Humidity and wind speed tracking
- Track status alerts (Green/Hot conditions)

## 📊 Data Sources

Using official Circuit of the Americas (COTA) GR Cup race data:
- **Telemetry Data**: 100+ Hz sensor data (speed, acceleration, braking, throttle)
- **Lap Times**: Complete lap-by-lap timing data
- **Sector Times**: S1, S2, S3 performance breakdown
- **Weather Data**: Real-time track conditions
- **Race Results**: Driver performance and standings

## 🛠️ Technology Stack

### Backend
- **FastAPI**: High-performance Python API framework
- **Pandas & NumPy**: Data processing and analysis
- **Scikit-learn**: Predictive modeling
- **Python 3.11+**

### Frontend
- **React 18**: Modern UI framework
- **Vite**: Lightning-fast build tool
- **Recharts**: Interactive data visualization
- **Axios**: API communication

## 📦 Installation & Setup

### Prerequisites
- Python 3.11 or higher
- Node.js 18 or higher
- npm or yarn

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Run the API server
python api.py
```

The API will start on `http://localhost:8000`

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The app will open on `http://localhost:3000`

## 🎮 How to Use

1. **Select a Driver**: Choose from the driver list in the sidebar
2. **Set Current Lap**: Use the lap slider or click "Simulate Race" for automatic progression
3. **View Pit Windows**: See optimal pit stop windows with confidence scores
4. **Analyze Performance**: Review lap times, sector performance, and tire degradation
5. **Make Decision**: Use the recommendations to determine the best pit strategy

## 🏆 Why PitGenius Wins

### 1. **Directly Addresses Hackathon Goals**
The hackathon explicitly requested "a real-time analytics and strategy tool for the GR Cup Series" - PitGenius delivers exactly this.

### 2. **High Impact for Teams**
- Race engineers can make data-driven pit decisions
- Drivers get real-time performance feedback
- Teams can simulate strategies before race day

### 3. **Comprehensive Data Utilization**
- Uses ALL provided datasets (telemetry, lap times, weather, sectors)
- Combines multiple data sources for holistic analysis
- Extracts meaningful insights from raw sensor data

### 4. **Production-Ready Architecture**
- Scalable FastAPI backend
- Responsive React frontend
- Real-time data processing
- Clean, maintainable code

### 5. **Innovative Algorithms**
- Tire degradation prediction using polynomial regression
- Multi-strategy optimization with confidence scoring
- Position prediction based on race simulation
- Weather impact analysis

## 📈 Technical Highlights

### Tire Degradation Algorithm
```python
# Analyzes lap time trends to predict tire wear
degradation_rate = polyfit(lap_numbers, lap_times, degree=1)
predicted_lap_time = base_time + (degradation_rate * laps_on_tires)
```

### Pit Window Optimization
```python
# Evaluates multiple strategies and ranks by predicted position
strategies = [early_undercut, standard_strategy, long_first_stint]
optimal_window = min(strategies, key=lambda s: s.predicted_position)
```

### Real-Time Decision Engine
```python
# Determines if immediate pit stop is required
if degradation_rate > threshold or gap_sufficient or weather_changing:
    return "PIT NOW"
```

## 🎥 Demo Video

[Link to 3-minute demo video showcasing:]
- Live race simulation
- Pit window calculations
- Strategy recommendations
- Performance analysis
- Real-time decision making

## 📊 API Endpoints

- `GET /drivers` - List all drivers
- `GET /driver/{number}/performance` - Get driver performance data
- `POST /strategy/calculate` - Calculate optimal pit windows
- `POST /strategy/pit-now` - Get immediate pit decision
- `GET /weather/current` - Get current weather conditions
- `GET /race/summary` - Get race overview

## 🔮 Future Enhancements

- **Machine Learning Models**: Train on historical race data for better predictions
- **Multi-Car Strategy**: Optimize team strategy across multiple cars
- **Fuel Management**: Integrate fuel consumption optimization
- **Live Telemetry Integration**: Connect to real-time race data feeds
- **Mobile App**: iOS/Android apps for pit crew
- **Voice Commands**: Hands-free operation for race engineers

## 🏁 Impact

### For Drivers
- Identify performance gaps in real-time
- Understand tire degradation patterns
- Make informed decisions on track

### For Race Engineers
- Optimize pit stop timing
- Predict race outcomes
- React to competitor strategies

### For Teams
- Gain competitive advantage through data
- Reduce strategic errors
- Improve race-day decision making

### For Fans
- Understand race strategy complexity
- Follow real-time decision making
- Deeper engagement with the sport

## 👥 Team

Built with passion for motorsports and data science.

## 📄 License

MIT License - Built for Toyota Racing Development Hackathon

## 🙏 Acknowledgments

- Toyota Racing Development for providing the datasets
- GR Cup Series for the racing data
- Circuit of the Americas for hosting the races

---

**Built for Hack the Track 2025** 🏁
**Category: Real-Time Analytics**
**Dataset: Circuit of the Americas GR Cup Race Data**
