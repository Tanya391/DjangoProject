# FinAgent AI — Personal Financial Intelligence Platform

FinAgent AI is a personal finance analysis platform built using an enterprise **Decoupled (Headless) Architecture**:
- **Backend:** Django 5.x, Django ORM, and Django REST Framework (DRF)
- **Frontend:** React, Vite, and TailwindCSS
- **Database:** Relational SQLite database (`db.sqlite3`) managed through Django ORM
- **AI Engine:** Google Gemini (`gemini-1.5-flash` via official `google-genai` SDK)

---

## 🏗️ Architecture & Core Features

### 1. Django ORM Data Layer & Migrations
- **Relational Models:**
  - `Category`: Categorization model supporting Foreign Key relationships.
  - `Transaction`: Core financial record with `ForeignKey(User)` and `ForeignKey(Category)`, merchant auto-normalization, and dual-indexing (`db_index=True`).
  - `QueryLog`: Audit log tracking natural language questions, routing intents, source counts, and AI-synthesized responses.
- **Migrations:** Managed version control of database schemas (`0001_initial.py`, `0002_querylog.py`).
- **Deterministic Analytics Engine:** Math and summaries are executed via Django ORM aggregations (`Sum`, `Count`, `TruncMonth`), guaranteeing 0% AI hallucination for financial calculations.

### 2. Django Admin Interface (`/admin/`)
- Fully customized back-office admin dashboard:
  - List displays, color-coded transaction amounts (`+₹` for credits, `-₹` for debits).
  - Multi-parameter filtering (by transaction type, category, subscription status, and date hierarchies).
  - Search fields across merchant names, descriptions, and transaction IDs.
  - User and Group Role-Based Access Control (RBAC).

### 3. Structured Database RAG Pipeline
- **Dual-Routing System:**
  - *Mathematical Queries* (e.g., *"What did I spend on dining?"*): Executed deterministically by Django ORM.
  - *Analytical Queries* (e.g., *"Analyze my spending patterns"*): Routed to Google Gemini with retrieved Django ORM records injected as grounding context.
- **In-Memory Caching:** MD5-hashed query cache in `llm_service.py` prevents duplicate API calls and eliminates latency for repeated queries.
- **Fuzzy Token Matching:** `difflib`-powered date parser resolves misspelled month names (e.g. `"octber"`, `"febrary"`) to correct date boundaries.

### 4. Live Frontend Data Seeding & Management
- Interactive **Data Management** panel (`/data`):
  - **Load Sample Transactions:** Seeds 6 months of realistic categorized transactions directly from the browser UI (`POST /api/v1/seed/`).
  - **Clear Data:** Wipes transaction records on demand (`DELETE /api/v1/seed/`) to demonstrate live empty-to-seeded transitions to evaluators.
  - **CSV Statement Upload:** Ingests and validates bank CSV statement files (`POST /api/v1/upload/`).

---

## 🔌 API Endpoints Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/auth/register/` | Register a new user |
| `POST` | `/api/v1/auth/login/` | Obtain JWT access and refresh token pair |
| `POST` | `/api/v1/auth/refresh/` | Refresh expired JWT access token |
| `GET` | `/api/v1/status/` | Service health check |
| `GET` | `/api/v1/transactions/` | Paginated list of transactions with search & category filters |
| `POST` | `/api/v1/ask/` | Ask financial questions to the AI Assistant (RAG Pipeline) |
| `GET` | `/api/v1/history/` | Audit history of past financial queries |
| `GET` | `/api/v1/monthly-summary/` | Aggregated monthly income, expenses, and net cash flow |
| `GET` | `/api/v1/spending-by-category/` | Spending totals grouped by category |
| `GET` | `/api/v1/top-merchants/` | Top 10 merchants ranked by total expenditure |
| `GET` | `/api/v1/cashflow/` | Total credits vs. debits breakdown |
| `GET` | `/api/v1/subscriptions/` | Recurring subscription detection |
| `POST` | `/api/v1/seed/` | Generate 6 months of realistic synthetic transactions |
| `DELETE` | `/api/v1/seed/` | Clear user transactions (for live demo resetting) |
| `POST` | `/api/v1/upload/` | Ingest CSV statement file |

---

## 🚀 Getting Started Locally

### 1. Backend Setup (Django)

1. Open a terminal and navigate to `backend/`:
   ```powershell
   cd backend
   ```

2. (Recommended) Create and activate a virtual environment:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   Copy `.env.example` to `.env`:
   ```powershell
   copy .env.example .env
   ```
   *Add your `GEMINI_API_KEY` (get a free key at [Google AI Studio](https://aistudio.google.com/app/apikey)).*

5. Apply database migrations:
   ```powershell
   python manage.py migrate
   ```

6. Start the Django server:
   ```powershell
   python manage.py runserver
   ```
   - **Backend API:** `http://127.0.0.1:8000/api/v1/status/`
   - **Django Admin Panel:** `http://127.0.0.1:8000/admin/`

---

### 2. Frontend Setup (React + Vite)

1. Open a **second terminal** and navigate to `frontend/`:
   ```powershell
   cd frontend
   ```

2. Install dependencies:
   ```powershell
   npm install
   ```

3. Start the Vite development server:
   ```powershell
   npm run dev
   ```
   - **Web Application:** `http://localhost:5173`

---

### 🔑 Demo Credentials

* **Django Admin Panel (`/admin/`):**
  * **Username:** `admin`
  * **Password:** `admin123`
* **Default App User:**
  * **Username:** `demouser`
  * **Password:** `Password@123`
  *(You can also register any new account directly through the frontend).*

---

## 🧪 Automated Testing

Run the Django test suite:
```powershell
python manage.py test
```
**Verification:** Runs 7 automated unit tests covering ORM models, foreign key lookups, merchant auto-normalization, and API endpoints (`OK`).
