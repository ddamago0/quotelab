# QuoteLab

QuoteLab is an AI engineering single-page application (SPA) platform built on a quote corpus for three distinct challenges: Semantic Vibe Search, Evidence-Backed Debate, and Budget & Batching Optimizer, supported by a Dataset inspection view.

## Core Technologies

- **Backend**: Python 3.11+, FastAPI, Pydantic v2, pytest, openpyxl, sentence-transformers, numpy
- **Frontend**: React 18, Vite, Vanilla CSS
- **Architecture**: Decoupled Layered Architecture (Ports & Adapters)
- **Dataset**: 100 real quotes loaded from `data/citas.xlsx` via `ExcelQuoteRepository`
- **Embedding Model**: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (local multilingual dense vectors, 384 dimensions)
- **Vector Store**: In-memory NumPy array store with dense cosine similarity vector search


## General Structure

```
quotelab/
├── backend/            # FastAPI REST API & Domain Core
│   ├── app/
│   │   ├── api/        # REST routers (/api/health, etc.)
│   │   ├── config.py   # Pydantic Settings
│   │   ├── domain/     # Core entities & abstract Ports
│   │   ├── infra/      # Infrastructure adapters
│   │   ├── services/   # Application services
│   │   └── main.py     # FastAPI application entry point
│   ├── tests/          # Pytest test suite
│   └── requirements.txt
├── frontend/           # React + Vite SPA
│   ├── src/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── styles/
│   └── package.json
└── README.md
```

## Running Locally

### Backend Setup & Execution

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Backend API will be running at `http://localhost:8000` with interactive docs at `http://localhost:8000/api/docs`.

### Running Backend Tests

```bash
cd backend
.venv/bin/pytest tests
```

### Frontend Setup & Execution

```bash
cd frontend
npm install
npm run dev
```

Frontend SPA will be running at `http://localhost:5173`.