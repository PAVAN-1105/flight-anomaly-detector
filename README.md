# Flight Engine Anomaly Detector

A full-stack machine learning dashboard that uses an LSTM Autoencoder to detect degradation in turbofan engines.

## 1. Start the FastAPI Backend
Open a terminal in the root folder and run:
```bash
python3 -m venv venv
source venv/bin/activate  # (On Windows use: venv\Scripts\activate)
pip install -r requirements.txt
uvicorn api.main:app --reload