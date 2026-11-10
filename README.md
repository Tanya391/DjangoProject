# FinAgent AI

FinAgent AI is an AI-powered personal finance dashboard that allows users to upload their transaction data and ask open-ended questions about their spending habits using Google Gemini.

## 🏗️ Recent Architecture Modifications (Backend Hardening)
This project has recently undergone a major architectural simplification and backend hardening:
- **Vector Database (Qdrant) Removed:** Replaced with a lightweight, deterministic MongoDB document retrieval system.
- **LLM Consolidation:** Removed Groq, HuggingFace, and local `sentence-transformers`. The application now exclusively uses the modern `google-genai` SDK with `gemini-3.5-flash` for all AI features.
- **Deterministic Analytics:** Complex analytics and categorization are now 100% deterministic, meaning no AI hallucinations for precise financial calculations. AI is strictly reserved for natural language understanding and open-ended analysis.
- **Removed Legacy "Anomalies":** The outdated anomalies detection feature has been removed.
- **New Data Management:** Added endpoints to seed demo data (`/api/v1/seed/`) and upload CSV files (`/api/v1/upload/`).
- **Query History:** User queries are now securely logged and can be fetched via `/api/v1/history/`.

## 💻 Tech Stack
- **Backend**: Django, Django REST Framework, PyMongo, Google GenAI SDK
- **Frontend**: React, Vite, TailwindCSS, Zustand
- **Database**: MongoDB
- **Deployment**: Docker, Docker Compose (Ready for Render/GitHub Actions)

## 🚀 Getting Started Locally

1. Clone the repository.
2. Start the services using Docker:
   ```bash
   docker-compose up --build -d
   ```
3. The backend runs on `localhost:8000` and the frontend runs on `localhost:80`.

### Environment Variables
For the backend to work, provide the following in `backend/.env`:
```env
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-3.5-flash
MONGO_URI=mongodb://mongodb:27017
SECRET_KEY=your_django_secret
DEBUG=true
ALLOWED_HOSTS=localhost,127.0.0.1
```

## 🧪 Testing
The backend has been rigorously tested across a 30-phase verification checklist covering deterministic routing, data isolation, exact analytics output, file ingestion, error handling, and robust AI grounding without hallucinations.
