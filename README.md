# 🏥 Cura3.ai — AI-Powered Medical Diagnostics Platform

> **Multi-specialist AI diagnostic analysis** powered by OpenAI GPT-4.1

Cura3.ai uses a team of 10+ AI medical specialists to analyze patient reports in parallel, producing comprehensive diagnostic insights — all within a modern, secure web application.

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🔬 **Multi-Specialist Analysis** | 10+ AI specialists (Cardiologist, Neurologist, Oncologist, etc.) analyze each report |
| 🤖 **Auto-Specialist Selection** | AI recommends the best specialists for each report |
| 💬 **Follow-Up Chat** | Context-aware conversations about any diagnosis |
| 📄 **PDF Reports** | Download professionally formatted diagnosis PDFs |
| 📊 **Dashboard & Analytics** | Personal stats, time-series charts, and admin-level platform analytics |
| 🔐 **Google OAuth** | Secure authentication with role-based access control |
| 🛡️ **HIPAA-Aware** | Data sanitization, audit logging, secure storage, manual deletion controls |
| ⚡ **Rate Limiting** | Built-in API rate limiting for platform protection |
| 🍪 **httpOnly Secure Cookies** | JWT stored in httpOnly cookies (immune to XSS attacks) |
| 📡 **API Usage Monitoring** | Real-time endpoint tracking with Canvas bar charts |
| 📋 **Audit Logging** | HIPAA-compliant access trail for all sensitive operations |
| 🔒 **HTTPS Enforcement** | Automatic HTTP → HTTPS redirect in production |
| 🚀 **CI/CD Pipelines** | GitHub Actions for automated testing & Azure deployment |

---

## 🏗️ Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   Next.js 16    │────▶│  FastAPI Backend  │────▶│  MongoDB Atlas   │
│   Frontend      │     │  + AI Engine      │     │  (Database)      │
│   (React 19)    │     │                   │     │                  │
└─────────────────┘     └───────┬───────────┘     └──────────────────┘
                                │
                        ┌───────▼───────────┐
                        │  OpenAI GPT-4.1    │
                        │  API               │
                        └───────────────────┘
```

### Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Next.js 16 (App Router), React 19, TypeScript, CSS Modules |
| **Backend** | FastAPI, Python 3.12, Uvicorn |
| **AI Engine** | LangChain + OpenAI GPT-4.1 |
| **Database** | MongoDB Atlas (Motor async driver) |
| **Auth** | Google OAuth 2.0 + JWT (httpOnly cookies) |
| **Deployment** | Docker, Docker Compose, GitHub Actions CI/CD |
| **Monitoring** | Azure Application Insights (optional) |

---

## 📁 Project Structure

```
AI-Agents-for-Medical-Diagnostics/
├── backend/                     # FastAPI Backend
│   ├── app/
│   │   ├── api/v1/routes/       # API endpoints
│   │   │   ├── auth.py          # Google OAuth + httpOnly cookies
│   │   │   ├── reports.py       # File upload & management
│   │   │   ├── diagnosis.py     # AI diagnosis + PDF download
│   │   │   ├── chat.py          # Follow-up conversations
│   │   │   ├── admin.py         # User mgmt, audit logs, API usage
│   │   │   └── analytics.py     # Usage stats + time-series
│   │   ├── core/
│   │   │   ├── database.py      # MongoDB connection
│   │   │   ├── security.py      # JWT (dual-mode), RBAC
│   │   │   ├── rate_limiter.py  # Sliding window rate limiter
│   │   │   ├── audit_logger.py  # HIPAA-compliant access logging
│   │   │   ├── api_usage_tracker.py  # Endpoint usage analytics
│   │   │   ├── https_redirect.py  # HTTPS enforcement
│   │   │   └── monitoring.py    # Azure App Insights integration
│   │   ├── models/              # Pydantic data models
│   │   ├── services/
│   │   │   ├── agent_engine.py  # Multi-specialist AI engine
│   │   │   ├── specialist_selector.py  # Auto-selection AI
│   │   │   ├── report_parser.py # PDF/DOCX/TXT parsing
│   │   │   ├── chat_service.py  # Context-aware chat
│   │   │   └── pdf_generator.py # ReportLab PDF generation
│   │   ├── config.py            # Settings & env vars
│   │   └── main.py              # FastAPI app entry
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/                    # Next.js Frontend
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx         # Landing page
│   │   │   ├── dashboard/       # User dashboard + trend chart
│   │   │   ├── analyze/         # Upload & run diagnosis
│   │   │   ├── diagnosis/[id]/  # View diagnosis results
│   │   │   ├── history/         # Past diagnoses
│   │   │   ├── chat/            # Follow-up chat
│   │   │   ├── settings/        # Profile & preferences
│   │   │   ├── admin/           # Admin panel (4 tabs)
│   │   │   ├── auth/callback/   # OAuth callback
│   │   │   └── (legal)/         # Terms, Privacy, Disclaimer
│   │   ├── components/
│   │   │   ├── Sidebar/         # Navigation sidebar
│   │   │   ├── Charts/          # Canvas-based time-series chart
│   │   │   └── CookieConsent/   # GDPR cookie consent banner
│   │   ├── context/
│   │   │   └── AuthContext.tsx   # Auth state management
│   │   └── lib/
│   │       └── api.ts           # API client
│   ├── Dockerfile
│   └── package.json
│
├── .github/workflows/           # CI/CD Pipelines
│   ├── backend-ci-cd.yml        # Backend lint → test → deploy
│   └── frontend-ci-cd.yml       # Frontend lint → build → deploy
│
├── docker-compose.yml           # Full-stack orchestration
├── IMPLEMENTATION_PLAN.md       # Development roadmap
├── AZURE_DEPLOYMENT_GUIDE.md    # Step-by-step Azure deployment
├── .env.example                 # Environment variable template
└── README.md                    # This file
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.12+** (backend)
- **Node.js 22+** (frontend)
- **MongoDB Atlas** account (free tier works)
- **Google Cloud Console** project with:
  - OpenAI API key
  - OAuth 2.0 credentials

### 1. Clone & Setup Backend

```bash
# Clone the repo
git clone https://github.com/AaryanChandrakar/AI-Agents-for-Medical-Diagnostics.git
cd AI-Agents-for-Medical-Diagnostics

# Create virtual environment
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env        # Windows
# cp .env.example .env        # macOS/Linux
# Edit .env with your API keys
```

### 2. Setup Frontend

```bash
cd frontend
npm install

# Create environment file
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
```

### 3. Configure Environment Variables

Edit `backend/.env`:

```env
MONGODB_URI=mongodb+srv://your-cluster.mongodb.net
MONGODB_DB_NAME=cura3ai
OPENAI_API_KEY=your-openai-api-key
GOOGLE_CLIENT_ID=your-oauth-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-oauth-client-secret
JWT_SECRET_KEY=your-secure-random-string
FRONTEND_URL=http://localhost:3000
```

### 4. Run

```bash
# Terminal 1 — Backend
cd backend
uvicorn app.main:app --reload --port 8000

# Terminal 2 — Frontend  
cd frontend
npm run dev
```

Open **http://localhost:3000** in your browser.

### Docker (Alternative)

```bash
docker-compose up --build
```

---

## 🔬 AI Specialists

| Specialist | Focus Area |
|-----------|-----------|
| ❤️ Cardiologist | Heart, ECG, blood pressure |
| 🧠 Psychologist | Mental health, behavioral patterns |
| 🫁 Pulmonologist | Respiratory, lung function |
| 🧬 Neurologist | Brain, nervous system |
| ⚗️ Endocrinologist | Hormones, thyroid, diabetes |
| 🔬 Oncologist | Cancer screening, tumor markers |
| 🩺 Dermatologist | Skin conditions, allergies |
| 🏥 Gastroenterologist | Digestive system, liver |
| 🦴 Orthopedist | Bones, joints, musculoskeletal |
| 👨‍⚕️ General Practitioner | Overall health assessment |

---

## 📋 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/auth/login` | Initiate Google OAuth |
| `POST` | `/api/v1/auth/logout` | Clear session (httpOnly cookie) |
| `POST` | `/api/v1/reports/upload` | Upload medical report |
| `POST` | `/api/v1/reports/text` | Submit text report |
| `POST` | `/api/v1/diagnosis/run` | Run AI diagnosis |
| `GET` | `/api/v1/diagnosis/{id}/pdf` | Download PDF report |
| `POST` | `/api/v1/chat/{diagnosis_id}` | Send follow-up question |
| `GET` | `/api/v1/analytics/me` | Personal analytics |
| `GET` | `/api/v1/analytics/time-series` | Diagnosis trend data |
| `GET` | `/api/v1/admin/stats` | Admin system stats |
| `GET` | `/api/v1/admin/audit-logs` | HIPAA audit trail |
| `GET` | `/api/v1/admin/api-usage` | API usage monitoring |

Full API docs: **http://localhost:8000/docs**

---

## 🚀 Deployment

See **[AZURE_DEPLOYMENT_GUIDE.md](./AZURE_DEPLOYMENT_GUIDE.md)** for a complete step-by-step guide to deploying on Azure.

CI/CD is automated via GitHub Actions — push to `main` to trigger builds and deployments.

---

## ⚠️ Medical Disclaimer

> **This platform is for research and educational purposes ONLY.**  
> It is NOT a medical device, NOT intended for clinical use, and NOT a substitute for professional medical advice.  
> Always consult a qualified healthcare provider for medical decisions.

---

## 📄 License

This project is for educational and research purposes.

## 👤 Author

**Aaryan Chandrakar** — [GitHub](https://github.com/AaryanChandrakar)
