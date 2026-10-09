# AI Crop Disease & Market Advisory

A React and FastAPI application for crop guidance, leaf-disease assessment, and market trends. It uses MongoDB for accounts and private prediction history.

| Folder | Technology / purpose |
|---|---|
| `frontend/` | React 18, Vite, React Router, Axios, Recharts |
| `backend/` | FastAPI, MongoDB via Motor, JWT authentication |
| `ai-model/` | TensorFlow/Keras MobileNetV2 training and inference |
| `data/` | Crop and disease guidance plus clearly labelled sample market records |

## Current data status

- **Disease predictions:** no trained `ai-model/models/crop_disease_model.keras` weights are included. The detection page reports this and does not generate fabricated predictions. The tracked `class_names.json` defines the current supported label set; train a model before using real inference.
- **Market prices:** `data/market/sample_market_data.json` is synthetic development data in INR per quintal, dated Aug 24 through Oct 7, 2026. The application labels it as sample data. No live government or commercial market provider is configured.
- **Weather:** crop weather advice calls the Open-Meteo service when coordinates are provided.
- **MongoDB:** registration, login, profile, and private disease history require a reachable MongoDB instance.

## Windows setup

Prerequisites: Python 3.11 (recommended for TensorFlow compatibility), Node.js 18+, and MongoDB Community Server or a MongoDB Atlas database.

### 1. Configure MongoDB and backend

Start the local MongoDB service, or create an Atlas database and allow your client IP in its network access settings. Then, from the repository root in PowerShell:

```powershell
Set-Location .\backend
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `backend\.env`: set `MONGODB_URI` to your local or Atlas connection string and replace `SECRET_KEY` with a unique value. Generate a key with:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Keep `.env` private. For local development without an explicit key, the backend generates a random key at startup; existing tokens will stop working after a restart. For stable sessions, set `SECRET_KEY` in `.env`.

Start the API from the `backend` directory:

```powershell
python -m uvicorn app.main:app --reload --host 127.0.0.1
```

API docs: http://127.0.0.1:8000/docs

### 2. Start the frontend

Open another PowerShell terminal at the repository root:

```powershell
Set-Location .\frontend
npm install
npm run dev -- --host 127.0.0.1
```

Open http://127.0.0.1:5173. The backend CORS defaults allow both `localhost:5173` and `127.0.0.1:5173`. If the frontend uses another origin, add it to `CORS_ORIGINS` in `backend\.env` as a comma-separated value.

## Train and install a disease model

Place labelled leaf images under `ai-model/dataset/raw/<Crop>___<Disease>/`. From PowerShell:

```powershell
Set-Location .\ai-model
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python preprocessing/data_split.py
python training/train.py --epochs 10 --fine-tune-epochs 5
python training/evaluate.py
```

Training writes `models/crop_disease_model.keras` and the class labels. For backend inference, the model runtime dependencies must be installed in the backend environment too; `backend/requirements.txt` includes `ai-model/requirements.txt`. Add disease descriptions and treatment guidance for each trained class in `data/diseases/`. See [ai-model/README.md](ai-model/README.md) for data layout and preprocessing details.

## Tests

Run backend tests from PowerShell at the repository root:

```powershell
$env:PYTHONPATH = (Resolve-Path .\backend).Path
python -m pytest -q .\backend\tests
```

The tests cover service logic, auth/password helpers, upload validation and selected API routes. They do not require MongoDB or trained weights; live database, end-to-end authentication, and model inference still need to be verified in a configured environment.

## Project structure

```text
frontend/      React pages, shared components and API clients
backend/app/   FastAPI routes, schemas, services, MongoDB and auth
backend/tests/ API and service tests
ai-model/      dataset preprocessing, training and inference
data/          crop, disease and sample market JSON
docs/api/      API reference
```

## Limitations and advisory notice

- Market recommendations are calculations over the bundled sample series, not a guarantee or a live sell/hold signal. No transport/storage costs are included.
- Sowing and harvest months are indicative; adapt them to the user's location and local agricultural advice.
- Disease outputs, once a trained model is installed, are advisory and can be wrong. Treatment text is general guidance and deliberately omits pesticide doses. Follow product labels and local agricultural authorities.
- Open-Meteo weather availability depends on network access and supplied coordinates.
