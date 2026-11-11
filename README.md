# FinAgent AI

FinAgent AI is an AI-powered personal finance analysis application built with a **Decoupled (Headless) Architecture**:
- **Backend:** Django 5.x, Django ORM, and Django REST Framework (DRF)
- **Frontend:** React, Vite, and TailwindCSS
- **Database:** Relational SQLite database (`db.sqlite3`) with Django ORM
- **AI Engine:** Google Gemini (`gemini-1.5-flash` via `google-genai` SDK)

---

## 🏗️ Architecture & Features

1. **Django ORM Data Layer:**
   - Relational models: `Transaction` and `Category` with Foreign Keys linked to Django's built-in `User` model.
   - Comprehensive Django migrations (`0001_initial.py`).
   - High-performance deterministic analytics engine using Django ORM aggregations (`Sum`, `Count`, `TruncMonth`).

2. **Django Admin Interface:**
   - Fully customized admin dashboard for data auditing, list filters by category/type/date, full-text search, and role-based access control (RBAC).

3. **RESTful API & Authentication:**
   - Stateless authentication powered by `djangorestframework-simplejwt` (Access & Refresh tokens).
   - DRF Serializers handling JSON schema validation and error reporting.

4. **Hybrid AI & Deterministic Retrieval:**
   - Exact mathematical calculations and monthly summaries are executed via Django ORM.
   - Natural language queries, financial insights, and spending explanations are processed via Google Gemini.

---

## 🚀 Getting Started Locally

### 1. Backend Setup (Django)

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables (optional for local dev):
   Copy `.env.example` to `.env`:
   ```bash
   copy .env.example .env
   ```

4. Apply migrations (pre-configured SQLite database included):
   ```bash
   python manage.py migrate
   ```

5. (Optional) Seed realistic demo transactions:
   ```bash
   python manage.py seed_transactions --months 6
   ```

6. Start the Django development server:
   ```bash
   python manage.py runserver
   ```
   - **Backend API:** `http://127.0.0.1:8000/api/v1/status/`
   - **Django Admin Panel:** `http://127.0.0.1:8000/admin/`
     - **Admin User:** `admin`
     - **Admin Password:** `admin123`

---

### 2. Frontend Setup (React + Vite)

1. In a new terminal, navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the Vite development server:
   ```bash
   npm run dev
   ```
   - Open your browser at: `http://localhost:5173`

---

## 🧪 Automated Testing

Run the Django unit test suite:
```bash
python manage.py test
```
All tests verify ORM model creation, foreign key relationships, merchant auto-normalization, and API endpoints.
