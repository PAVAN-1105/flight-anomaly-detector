# 🚀 Flight Anomaly Diagnostics PRO

An enterprise-grade, full-stack predictive maintenance dashboard that utilizes Deep Learning to detect jet engine degradation, perform root cause analysis, and calculate Remaining Useful Life (RUL) in real-time.

Built using the **NASA C-MAPSS (Commercial Modular Aero-Propulsion System Simulation)** dataset.

## ✨ Key Features

- **🧠 LSTM Autoencoder Core:** Utilizes a Long Short-Term Memory neural network to establish a baseline of "healthy" engine telemetry and flag deviations (anomalies) across 14 distinct sensor readings.
- **⏱️ Predictive RUL Algorithm:** Goes beyond simple threshold alerts by calculating the degradation trajectory of the engine to predict the exact cycle of catastrophic failure before it happens.
- **📊 Interactive Root Cause Analysis:** A dynamic UI that allows mechanics to click on any point in the flight timeline to view a bar chart isolating the exact physical component (e.g., Bypass Ratio, LPT Temp) driving the anomaly.
- **⚡ Apple Silicon (M-Series) Optimized:** Engineered with custom raw tensor execution (`self.model(X, training=False)`) to bypass standard Keras `.predict()` multi-threading deadlocks on M4 architecture, ensuring instant API response times.
- **🎨 State-Driven UI:** Built with Angular, featuring a clean, minimal "Command Center" aesthetic with dynamic Chart.js gradients, traffic-light warning zones, and CSS pulse animations.

## 🛠️ Tech Stack

**Frontend:**

- Angular (Standalone Components)
- TypeScript
- Chart.js & `ng2-charts` (with `chartjs-plugin-annotation`)
- Custom CSS (No external UI libraries)

**Backend:**

- Python 3.x
- FastAPI & Uvicorn (Web Server)
- TensorFlow / Keras (ML Framework)
- Pandas & NumPy (Data Processing)

## ⚙️ Local Setup & Installation

You will need two terminal windows to run the frontend and backend simultaneously.

### 1. Start the Machine Learning API (Backend)

Navigate to the root directory of the project:

```bash
# Activate the virtual environment (Use venv\Scripts\activate on Windows)
source venv/bin/activate

# Install requirements (if not already installed)
pip install -r requirements.txt

# Boot the FastAPI server
uvicorn api.main:app --reload


### 2. Start the Angular Dashboard (Frontend)
Open a new terminal window:
Bash
# Navigate to the frontend directory
cd frontend

# Install Node modules
npm install

# Start the development server
ng serve -o
```
