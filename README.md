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


## Desafío 2 — Debate Basado en Evidencia (Fase 4A)

### Propósito de `DebateService`
El servicio `DebateService` (`backend/app/services/debate_service.py`) gestiona la generación estructurada de debates filosóficos y argumentativos fundamentados estrictamente en evidencias recuperadas del corpus de citas.

### Abstracción de Proveedor LLM (`LLMProviderPort`)
El puerto `LLMProviderPort` (`backend/app/domain/ports.py`) define el contrato agnóstico para la generación de texto y argumentos estructurados (`generate` y `generate_debate_arguments`). Está completamente desacoplado de APIs en la nube (OpenAI, Anthropic, Gemini) y SDKs propietarios, garantizando que el sistema opere de forma local y permita conectar inferencia local en futuras fases.

### Proveedor de Desarrollo / Prueba (`MockLLMProvider`)
Se implementó `MockLLMProvider` (`backend/app/infra/llm/mock_llm_provider.py`), un proveedor determinista para desarrollo y pruebas locales. No requiere llaves de API ni conexión a Internet, garantizando la trazabilidad exacta de los identificadores de citas recuperadas (`evidence_quote_ids`) y respuestas estructuradas reproducibles.

### Fundamentación en Evidencia y Prevención de Alucinaciones
- **Filtrado por Umbral**: Las citas recuperadas por `SemanticRetriever` se filtran usando un umbral de similitud semántica configurable (`settings.DEBATE_RELEVANCE_THRESHOLD`).
- **Rechazo Controlado**: Si ninguna cita alcanza el umbral de relevancia, `DebateService` retorna `sufficient_evidence=False` junto con un mensaje explícito de rechazo (`refusal_message`).
- **Cero Fabricación**: El sistema jamás inventa citas ni atribuciones que no existan en el dataset.

### Limitaciones Actuales
- La Fase 4A abarca la arquitectura de dominio, servicios y proveedor simulado. No expone aún el endpoint REST de debate ni la interfaz de usuario en el frontend.
- La generación de argumentos utiliza el proveedor simulado determinista `MockLLMProvider`.

### Integración Futura de LLM Local
Gracias al diseño desacoplado (Clean Architecture), la integración futura de un LLM local (por ejemplo, Ollama ejecutando Llama 3 o Mistral) se realizará creando un nuevo adaptador `OllamaLLMProvider` en `infra/llm/` que implemente `LLMProviderPort`, sin modificar `DebateService` ni las capas de dominio.


## Desafío 2 — REST API del Debate (Fase 4B)

### Endpoint REST
`POST /api/debate`

### Formato de Solicitud (JSON)
```json
{
  "topic": "Is failure necessary for success?",
  "min_evidence_score": 0.65
}
```

### Estructura de Respuesta (JSON)
```json
{
  "topic": "Is failure necessary for success?",
  "sufficient_evidence": true,
  "arguments": [
    {
      "position": "Perspectiva A (A favor)",
      "argument_text": "[DESARROLLO MOCK] En relación con el debate 'Is failure necessary for success?', J.K. Rowling ofrece evidencia clave: \"...\"",
      "evidence_quote_ids": ["q_28"]
    }
  ],
  "evidence_quotes": [
    {
      "id": "q_28",
      "text": "It is impossible to live without failing at something...",
      "author": "J.K. Rowling",
      "tags": ["life", "failure"]
    }
  ],
  "refusal_message": null
}
```

### Fundamentación en Evidencia y Manejo de Evidencia Insuficiente
- Si ninguna cita supera el umbral de similitud semántica configurable (`settings.DEBATE_RELEVANCE_THRESHOLD`), la API responde con un estado HTTP 200 y una respuesta estructurada conteniendo `sufficient_evidence: false`, `arguments: []`, `evidence_quotes: []` y un mensaje explícito de rechazo en `refusal_message`.
- No se exponen trazas internas de error al cliente ni se fabrican IDs de citas.

### Estado Actual del Proveedor LLM
- Se mantiene el uso de `MockLLMProvider` determinista para desarrollo y pruebas en la API principal.
- No se requieren llaves de API, servicios en la nube ni la ejecución activa de Ollama para la ejecución por defecto.


## Adaptador de Proveedor LLM Local con Ollama (Fase 4C-1)

### Adaptador `OllamaLLMProvider`
Se implementó el adaptador `OllamaLLMProvider` en `backend/app/infra/llm/ollama_llm_provider.py` que satisface el contrato `LLMProviderPort`.
- **Comunicación HTTP**: Utiliza `httpx` para conectarse a la API REST de Ollama (`POST /api/chat`, por defecto en `http://localhost:11434`).
- **Configuración Desacoplada**: Soporta `OLLAMA_BASE_URL`, `OLLAMA_MODEL` y `OLLAMA_TIMEOUT` configurables desde `backend/app/config.py`.
- **Parseo Defensivo**: Maneja respuestas estructuradas JSON y limpia automáticamente bloques envueltos en sintaxis Markdown (```json ... ```).
- **Atribución Estricta**: Valida y garantiza que los `evidence_quote_ids` retornados correspondan exclusivamente a las citas de evidencia suministradas.
- **Sin SDKs Propietarios ni Nube**: Cero dependencias de SDKs de terceros ni APIs en la nube.

> [!NOTE]
> **Estado de Activación**: La Fase 4C-1 crea y prueba de forma aislada el adaptador `OllamaLLMProvider`. **NO activa aún Ollama como el proveedor activo en la inyección de dependencias** (`dependencies.py`). `MockLLMProvider` se mantiene como el proveedor activo por defecto.