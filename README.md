# 🏥 AI Hospital OS — AI Triage Assistant

An intelligent, LLM-powered emergency department triage system built on the **MIMIC-IV-ED** dataset. It automates ESI (Emergency Severity Index) acuity prediction, surfaces similar historical cases via RAG, detects disease outbreaks through surveillance, and exposes everything through a real-time dashboard and REST API.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🤖 **AI Triage** | Fine-tuned LLaMA-8B (`ali009eng/llama-8b-mimic-ed-triage`) for ESI-level prediction |
| 🔍 **RAG System** | Retrieval-Augmented Generation using FAISS + Sentence Transformers for similar case lookup |
| 🦠 **Surveillance** | Real-time outbreak & anomaly detection using TF-IDF clustering |
| 📊 **Dashboard** | Live patient monitoring dashboard with auto-refresh |
| 🔗 **LangChain Agent** | Conversational triage agent with tool use and LangSmith tracing |
| 🔐 **Auth** | JWT-based authentication (optional) |
| 🐳 **Docker** | Fully containerised with Docker Compose |

---

## 🗂️ Project Structure

```
AI-Hospital-OS/
├── api/                    # FastAPI REST endpoints
├── auth/                   # JWT authentication
├── dashboard/              # Real-time monitoring UI (HTML + JS)
├── data/                   # MIMIC-IV-ED dataset (not tracked in git)
├── data_processing/        # MIMIC data loading & preprocessing
├── deployment/             # Deployment configs & scripts
├── docs/                   # Technical reports & assessment docs
├── experiments/            # Research & alternative approach experiments
├── langchain_integration/  # LangChain triage agent
├── langsmith_integration/  # LangSmith observability
├── rag/                    # FAISS vector DB + RAG pipeline
├── scripts/                # Utility & setup scripts
├── surveillance/           # Outbreak detection system
├── tests/                  # Unit & integration tests
├── utils/                  # Shared utilities
├── config.py               # Centralised configuration
├── Dockerfile              # Container definition
├── docker-compose.yml      # Multi-service orchestration
└── requirements.txt        # Python dependencies
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Docker & Docker Compose (recommended)
- MIMIC-IV-ED access (place CSVs in `data/mimic_iv_ed/`)

### 1. Clone & configure

```bash
git clone https://github.com/ali009-eng/AI-Hospital-OS-.git
cd AI-Hospital-OS-
cp env.example .env
# Edit .env with your API keys and config
```

### 2. Run with Docker (recommended)

```bash
docker-compose up --build
```

### 3. Run locally

```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt

# Start the API
uvicorn api.server:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Access the dashboard

Open `http://localhost:8000` in your browser.

---

## ⚙️ Configuration

All settings are controlled via environment variables. Copy `env.example` to `.env` and edit:

| Variable | Default | Description |
|---|---|---|
| `MODEL_NAME` | `ali009eng/llama-8b-mimic-ed-triage` | HuggingFace model ID |
| `MODEL_DEVICE` | `auto` | `auto`, `cuda`, or `cpu` |
| `API_PORT` | `8000` | API server port |
| `MIMIC_DATA_PATH` | `./data/mimic_iv_ed` | Path to MIMIC-IV-ED CSVs |
| `VECTOR_DB_PATH` | `./data/vector_db` | FAISS vector store path |
| `LANGCHAIN_API_KEY` | — | LangSmith API key (optional) |
| `LANGCHAIN_TRACING` | `false` | Enable LangSmith tracing |
| `ENABLE_AUTH` | `false` | Enable JWT authentication |

---

## 🧠 ESI Triage Levels

| Level | Severity | Description |
|---|---|---|
| **1** | 🔴 Immediate | Life-threatening |
| **2** | 🟠 High Risk | Urgent |
| **3** | 🟡 Medium | Stable but needs evaluation |
| **4** | 🟢 Lower Medium | Stable with minor issues |
| **5** | ⚪ Minor | Non-urgent |

---

## 🧪 Testing

```bash
pytest tests/ -v
```

---

## 🐳 Docker Services

```bash
docker-compose up           # Start all services
docker-compose down         # Stop all services
docker-compose logs -f api  # Stream API logs
```

---

## 📄 License

This project is for research and educational purposes. MIMIC-IV-ED data requires a PhysioNet credentialed access agreement.

---

## 👤 Author

**ali009-eng** — [GitHub](https://github.com/ali009-eng)