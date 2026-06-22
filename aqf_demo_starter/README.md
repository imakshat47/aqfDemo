# AQF Demo Starter

This repository is a clean starter scaffold for the AQF demo.

## What is included
- `aqf_runtime/`: paper-aligned runtime pipeline
- `aqf_backend/`: FastAPI wrapper
- `aqf_frontend/`: simple UI entry point
- `datasets/sample/`: tiny example dataset
- `docs/`: setup and usability notes

## Local setup on Windows
1. Open the folder in Visual Studio Code.
2. Create a virtual environment:
   ```powershell
   python -m venv .venv
   .venv\Scripts\activate
   ```
3. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
4. Run the backend:
   ```powershell
   uvicorn aqf_backend.main:app --reload
   ```

## Demo workflow
1. Load a sample dataset.
2. Generate AQF forms.
3. Build a query.
4. View query explanation and generated AQL.
5. Record usability metrics.
