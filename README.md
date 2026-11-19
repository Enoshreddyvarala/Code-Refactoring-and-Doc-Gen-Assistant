# CodeMate AI — AI-Powered Code Refactoring & Documentation Assistant

> **v2.0** — Migrated from Streamlit to React.js + FastAPI

An AI-powered developer productivity tool for Python code analysis, refactoring, explanation, and documentation generation — powered by **Google Gemini**.

---

## Project Structure

```
codemate-ai/
├── frontend/                   ← React.js (Vite + Tailwind CSS v4)
│   ├── src/
│   │   ├── components/         ← Reusable UI components
│   │   │   ├── Sidebar.jsx
│   │   │   ├── PageHeader.jsx
│   │   │   ├── MetricCard.jsx
│   │   │   ├── IssueBadge.jsx
│   │   │   ├── IssueCard.jsx
│   │   │   ├── HealthBanner.jsx
│   │   │   ├── LoadingSpinner.jsx
│   │   │   ├── ErrorMessage.jsx
│   │   │   ├── DownloadButton.jsx
│   │   │   └── CodeEditor.jsx   ← Monaco Editor wrapper
│   │   ├── pages/              ← 7 application pages
│   │   │   ├── Dashboard.jsx
│   │   │   ├── Workspace.jsx
│   │   │   ├── Analysis.jsx
│   │   │   ├── Refactoring.jsx
│   │   │   ├── Explanation.jsx
│   │   │   ├── Documentation.jsx
│   │   │   └── About.jsx
│   │   ├── services/
│   │   │   └── api.js          ← All FastAPI calls
│   │   ├── App.jsx             ← Router + layout
│   │   └── index.css           ← Tailwind v4 + custom CSS
│   ├── package.json
│   ├── vite.config.js
│   └── postcss.config.js
│
├── backend/                    ← FastAPI Python server
│   ├── main.py                 ← App entry + CORS
│   ├── routes/                 ← API route handlers
│   │   ├── health.py           ← GET  /api/health
│   │   ├── analyze.py          ← POST /api/analyze
│   │   ├── refactor.py         ← POST /api/refactor
│   │   ├── explain.py          ← POST /api/explain
│   │   ├── document.py         ← POST /api/document
│   │   ├── validate.py         ← POST /api/validate
│   │   └── samples.py          ← GET  /api/samples
│   ├── services/               ← Business logic
│   │   ├── gemini_service.py
│   │   ├── code_analyzer.py
│   │   ├── refactoring_service.py
│   │   ├── explanation_service.py
│   │   ├── documentation_service.py
│   │   └── validation_service.py
│   ├── prompts/                ← Gemini prompt templates
│   ├── schemas/models.py       ← Pydantic request/response models
│   ├── utils/                  ← file_handler, sample_codes
│   ├── tests/                  ← Pytest tests
│   └── requirements.txt
│
├── legacy_streamlit/           ← Original Streamlit app (preserved)
├── .env                        ← Gemini API key (do not commit)
├── .env.example                ← Template for environment setup
├── .gitignore
└── README.md
```

---

## Features

| Feature | Description |
|---------|-------------|
| **Code Analysis** | Python AST quality analysis, health scoring (0–100), issue detection |
| **AI Refactoring** | Gemini rewrites code to PEP 8 standards while preserving functionality |
| **Code Explanation** | Beginner-friendly breakdown with real-world analogy and step-by-step guide |
| **Documentation** | Auto-generate README.md and PEP 257 docstrings |
| **Syntax Validation** | AST parse check + Black formatting validation |
| **File Upload** | Upload .py files directly in the browser |
| **Sample Programs** | Built-in example Python programs to explore |
| **Download Outputs** | Export refactored code, README, explanation as files |

---

## Technology Stack

| Layer | Technologies |
|-------|-------------|
| Frontend | React.js 18, Vite, Tailwind CSS v4, React Router, Monaco Editor, Lucide React |
| Backend | Python 3.11+, FastAPI, Uvicorn, Pydantic, python-dotenv |
| AI | Google Gemini API (google-genai SDK), configurable model via env var |
| Analysis | Python AST, Black formatter, difflib |
| Testing | Pytest, FastAPI TestClient |

---

## Setup & Running

### 1. Environment Variables

Copy `.env.example` to `.env` and fill in your Gemini API key:

```bash
cp .env.example .env
```

```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-3.8-flash
```

### 2. Backend (FastAPI)

```bash
# From the project root
pip install -r backend/requirements.txt

# Start the server
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

API docs available at: http://localhost:8000/docs

### 3. Frontend (React)

```bash
cd frontend
npm install
npm run dev
```

App available at: http://localhost:5173

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Backend health + Gemini config status |
| POST | `/api/analyze` | AST code analysis + health scoring |
| POST | `/api/refactor` | AI-powered code refactoring |
| POST | `/api/explain` | Beginner-friendly code explanation |
| POST | `/api/document` | README.md + docstring generation |
| POST | `/api/validate` | Syntax validation / Black formatting / test runner |
| GET | `/api/samples` | List of sample programs |
| GET | `/api/samples/{name}` | Get a specific sample |
| POST | `/api/upload` | Upload a .py file |

---

## Security

- **API keys stay on the backend** — never sent to or bundled in the React frontend
- **Code is never executed** directly in the server process — only parsed by AST/Black
- Test execution runs in an **isolated subprocess** with a strict timeout
- No user data is stored beyond the current session

---

## Running Tests

```bash
# Backend tests (from project root)
python -m pytest backend/tests -v

# Legacy Streamlit tests
python -m pytest tests -v
```

---

## Legacy Streamlit App

The original Streamlit implementation is preserved in `legacy_streamlit/`:

```bash
cd legacy_streamlit
pip install -r requirements.txt
streamlit run app.py
```

---

*Built as a learning project for beginner Python developers. Code is intentionally readable, modular, and well-commented.*
