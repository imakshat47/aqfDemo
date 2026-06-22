## Setup

### Backend
```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn aqf_backend.main:app --reload
```

### Test the AQF runtime quickly
- Load `datasets/sample/sample_dataset.json`
- Call `POST /aqf/generate`
- Call `POST /query/explain`
