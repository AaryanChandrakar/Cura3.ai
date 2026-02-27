# CURA3.AI — IMPLEMENTATION PLAN
# ==============================================================
# Full-Stack AI Medical Diagnostics Platform
# ==============================================================
#
# Based on decisions in: PROJECT_DECISIONS.md
# Created: 2026-02-25
#
# ==============================================================


# ────────────────────────────────────────────────────────────────
# DECISIONS SUMMARY
# ────────────────────────────────────────────────────────────────
#
# Frontend:      Next.js (complete web app), medical/clinical theme, mobile-responsive
# Backend:       FastAPI (Python)
# Database:      MongoDB Atlas
# Auth:          Google OAuth, role-based (Doctor / Patient / Admin)
# Reports:       Upload (.txt/.pdf/.docx) + paste text, user chooses to store or discard
# AI Agents:     Auto-select specialists based on report + manual override from expanded list
# Follow-Up:     Chat feature to ask questions about diagnosis
# Output:        On-screen display + PDF download + diagnosis history
# Hosting:       Azure (HTTPS enabled)
# API Key:       App-managed (owner bears cost)
# Security:      HIPAA-aware, disclaimer page, manual deletion (no auto-expire)
# Analytics:     Yes (usage stats, diagnosis tracking)
# Scale:         Real product (100+ users), also portfolio showcase
#
# ────────────────────────────────────────────────────────────────


# ==============================================================
# PROJECT ARCHITECTURE OVERVIEW
# ==============================================================
#
#   ┌──────────────────────────────────────────────────────┐
#   │                    FRONTEND (Next.js)                 │
#   │                                                      │
#   │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐  │
#   │  │  Login   │ │Dashboard │ │ Upload   │ │  Chat  │  │
#   │  │  (OAuth) │ │ & History│ │ & Analyze│ │Follow-Up│  │
#   │  └──────────┘ └──────────┘ └──────────┘ └────────┘  │
#   │  ┌──────────┐ ┌──────────┐ ┌──────────┐             │
#   │  │  Admin   │ │Analytics │ │ Settings │             │
#   │  │  Panel  │ │ Dashboard│ │ & Profile│             │
#   │  └──────────┘ └──────────┘ └──────────┘             │
#   └────────────────────┬─────────────────────────────────┘
#                        │ REST API + WebSocket (chat)
#   ┌────────────────────┴─────────────────────────────────┐
#   │                  BACKEND (FastAPI)                    │
#   │                                                      │
#   │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐  │
#   │  │  Auth    │ │  Report  │ │  Agent   │ │  Chat  │  │
#   │  │  Routes  │ │ Manager  │ │ Engine   │ │ Engine │  │
#   │  └──────────┘ └──────────┘ └──────────┘ └────────┘  │
#   │  ┌──────────┐ ┌──────────┐ ┌──────────┐             │
#   │  │  PDF     │ │ Analytics│ │  Admin   │             │
#   │  │Generator │ │ Service  │ │ Service  │             │
#   │  └──────────┘ └──────────┘ └──────────┘             │
#   └────────────────────┬─────────────────────────────────┘
#                        │
#   ┌────────────────────┴─────────────────────────────────┐
#   │               MONGODB ATLAS                          │
#   │                                                      │
#   │  Collections: users, reports, diagnoses,             │
#   │               chat_sessions, analytics               │
#   └──────────────────────────────────────────────────────┘
#
#   External Services:
#   - Google Gemini API (LLM)
#   - Google OAuth 2.0 (Authentication)
#   - Azure App Service (Hosting)
#


# ==============================================================
# PHASE 1: BACKEND FOUNDATION
# ==============================================================
# Priority: HIGH | Estimated effort: 2-3 days
# Goal: Transform CLI into a production-ready API server
# ==============================================================

## Phase 1.1 — Project Restructure
# [x] Create new folder structure:
#     /backend
#       /app
#         __init__.py
#         main.py              (FastAPI app entry point)
#         config.py            (Settings, env vars, constants)
#         /api
#           /v1
#             /routes
#               auth.py        (Google OAuth endpoints)
#               reports.py     (Upload, list, delete reports)
#               diagnosis.py   (Run diagnosis, get results)
#               chat.py        (Follow-up chat endpoints)
#               admin.py       (Admin-only endpoints)
#               analytics.py   (Usage stats endpoints)
#         /models
#           user.py            (User schema - Doctor/Patient/Admin)
#           report.py          (Medical report schema)
#           diagnosis.py       (Diagnosis result schema)
#           chat.py            (Chat session schema)
#         /services
#           agent_engine.py    (AI agent orchestration - from current Utils/Agents.py)
#           specialist_selector.py  (Auto-select specialists based on report content)
#           report_parser.py   (Parse .txt, .pdf, .docx files)
#           pdf_generator.py   (Generate downloadable PDF reports)
#           chat_service.py    (Follow-up chat with context)
#           analytics_service.py
#         /core
#           database.py        (MongoDB Atlas connection)
#           security.py        (Auth middleware, HIPAA helpers)
#           dependencies.py    (FastAPI dependency injection)
#       requirements.txt
#       Dockerfile
#
# [x] Migrate existing Agents.py logic into /services/agent_engine.py
# [x] Set up MongoDB Atlas connection with Motor (async MongoDB driver)
# [x] Create Pydantic models for all data schemas

## Phase 1.2 — Authentication System
# [x] Implement Google OAuth 2.0 flow
# [x] Create JWT token system for session management
# [x] Define roles: Doctor, Patient, Admin
# [x] Role-based route protection middleware
# [x] User profile endpoints (get/update profile)

## Phase 1.3 — Report Management API
# [x] POST /api/v1/reports/upload      (upload .txt/.pdf/.docx)
# [x] POST /api/v1/reports/text        (paste raw text)
# [x] GET  /api/v1/reports             (list user's reports)
# [x] GET  /api/v1/reports/{id}        (get specific report)
# [x] DELETE /api/v1/reports/{id}      (manual deletion)
# [x] Implement file parsers (txt, pdf via PyPDF2, docx via python-docx)

## Phase 1.4 — AI Agent Engine (Upgraded)
# [x] Expand specialist list:
#       - Cardiologist, Psychologist, Pulmonologist (existing)
#       - Neurologist, Endocrinologist, Oncologist
#       - Dermatologist, Gastroenterologist, Orthopedist
#       - General Practitioner (catch-all)
# [x] Build specialist_selector.py:
#       - Uses an LLM call to analyze the report content
#       - Returns recommended specialists (top 3-5)
#       - User can override / add more
# [x] Async parallel agent execution
# [x] Store individual specialist reports + final diagnosis in MongoDB


# ==============================================================
# PHASE 2: FRONTEND FOUNDATION
# ==============================================================
# Priority: HIGH | Estimated effort: 3-4 days
# Goal: Build a polished, medical-themed Next.js web application
# ==============================================================

## Phase 2.1 — Next.js Project Setup
# [x] Initialize Next.js project with App Router
# [x] Set up design system:
#       - Medical/clinical color palette
#         Primary:   #0A6EBD (medical blue)
#         Secondary: #12B886 (health green)
#         Accent:    #E8F4FD (light blue bg)
#         Dark:      #1A1A2E (dark panels)
#         Danger:    #E74C3C (alerts/warnings)
#         Text:      #2C3E50 (dark gray)
#       - Typography: Inter / Outfit (clean, professional)
#       - Component library setup (custom components)
# [x] Configure API client (axios/fetch wrapper)
# [x] Set up Google OAuth client-side flow

## Phase 2.2 — Core Pages
# [x] Landing Page
#       - Hero section with product overview
#       - How it works (3-step flow)
#       - Feature highlights
#       - Trust/security badges
#       - CTA to sign in
# [x] Login / Sign Up Page
#       - Google OAuth button
#       - Clean, minimal design
# [x] Dashboard (post-login)
#       - Welcome message + quick stats
#       - Recent diagnoses list
#       - Quick upload button
#       - Navigation sidebar
# [x] Upload & Analyze Page
#       - Drag-and-drop file upload zone
#       - Text paste area (tab switch)
#       - Auto-detected specialist chips
#       - "Run Diagnosis" button with loading animation
# [x] Diagnosis Results Page
#       - Structured diagnosis display (matches the new format)
#       - Individual specialist reports (expandable sections)
#       - Download as PDF button
#       - "Ask Follow-Up Questions" button → opens chat
#       - Save / Discard toggle
# [x] Chat / Follow-Up Page
#       - Chat interface with diagnosis context
#       - Message history
#       - Specialist-aware responses
# [x] History Page
#       - List of past diagnoses with search/filter
#       - Click to view full report
#       - Delete option per report
# [x] Settings / Profile Page
#       - User profile info
#       - Manage stored reports
#       - Delete account option

## Phase 2.3 — Admin Panel (Admin role only)
# [x] User management (view/deactivate users)
# [x] System-wide analytics dashboard
# [x] API usage monitoring


# ==============================================================
# PHASE 3: ADVANCED FEATURES
# ==============================================================
# Priority: MEDIUM | Estimated effort: 2-3 days
# Goal: Add the differentiating features
# ==============================================================

## Phase 3.1 — Smart Specialist Auto-Selection
# [x] Pre-analysis LLM call that reads report summary
# [x] Returns top 3-5 relevant specialists with confidence scores
# [x] UI: Show recommended specialists as pre-selected chips
# [x] User can add/remove specialists before running diagnosis

## Phase 3.2 — Follow-Up Chat System
# [x] WebSocket or SSE connection for real-time chat
# [x] Chat context includes: original report + all specialist reports + final diagnosis
# [x] User can ask clarification questions
# [x] Chat history stored in MongoDB per diagnosis

## Phase 3.3 — PDF Report Generator
# [x] Professional PDF layout with:
#       - Cura3.ai branding/header
#       - Patient report summary
#       - Each specialist's findings
#       - Final diagnosis (formatted)
#       - Disclaimer footer
# [x] Use ReportLab or WeasyPrint library

## Phase 3.4 — Analytics Dashboard
# [x] Track: total diagnoses, active users, popular specialists
# [x] Time-series charts (diagnoses per day/week/month)
# [x] Admin-only detailed view
# [x] User-facing: personal usage stats


# ==============================================================
# PHASE 4: SECURITY & COMPLIANCE
# ==============================================================
# Priority: HIGH | Estimated effort: 1-2 days
# Goal: HIPAA-aware security, proper disclaimers
# ==============================================================

## Phase 4.1 — Security Hardening
# [x] HTTPS enforcement (Azure handles TLS)
# [x] API rate limiting per user
# [x] Input sanitization on all endpoints
# [x] CORS configuration (frontend origin only)
# [x] Secure JWT token handling (httpOnly cookies)

## Phase 4.2 — HIPAA Awareness
# [x] No PHI logged to console or log files
# [x] User data encrypted at rest (MongoDB Atlas encryption)
# [x] Manual deletion endpoints (reports + account)
# [x] Data minimization (don't store more than needed)
# [x] Audit log for data access (admin view)

## Phase 4.3 — Legal Pages
# [x] Terms of Service page
# [x] Privacy Policy page
# [x] Medical Disclaimer (prominent on every diagnosis)
# [x] Cookie consent banner


# ==============================================================
# PHASE 5: DEPLOYMENT (AZURE)
# ==============================================================
# Priority: HIGH | Estimated effort: 1-2 days
# Goal: Deploy to Azure with CI/CD
# ==============================================================

## Phase 5.1 — Azure Setup
# [ ] Azure App Service for backend (Python)
# [ ] Azure Static Web Apps or App Service for frontend (Next.js)
# [ ] MongoDB Atlas cluster (cloud, separate from Azure)
# [ ] Environment variables configured in Azure
# [ ] Custom domain setup (when purchased)

## Phase 5.2 — CI/CD Pipeline
# [x] GitHub Actions workflow:
#       - On push to main → build & deploy backend
#       - On push to main → build & deploy frontend
# [x] Health check endpoints
# [x] Automated smoke tests

## Phase 5.3 — Containerization & Monitoring
# [x] Backend Dockerfile
# [x] Frontend Dockerfile (multi-stage)
# [x] Docker Compose (full-stack orchestration)
# [x] Azure Application Insights for monitoring
# [x] Error alerting
# [x] Performance tracking


# ==============================================================
# IMPLEMENTATION ORDER (RECOMMENDED)
# ==============================================================
#
# We will build this in the following order to have something
# working at each stage:
#
# STEP 1: Backend API (Phase 1.1 + 1.3 + 1.4)
#         → Working API that can accept reports and return diagnoses
#
# STEP 2: Frontend Shell (Phase 2.1 + 2.2 landing/upload/results)
#         → Users can upload reports and see results in browser
#
# STEP 3: Authentication (Phase 1.2 + 2.2 login)
#         → Users can log in with Google and have sessions
#
# STEP 4: Database Integration (MongoDB collections)
#         → Reports and diagnoses are persisted
#
# STEP 5: Advanced Features (Phase 3)
#         → Smart selection, chat, PDF download, history
#
# STEP 6: Security & Legal (Phase 4)
#         → Production-ready security
#
# STEP 7: Azure Deployment (Phase 5)
#         → Live on the internet!
#
# ==============================================================


# ==============================================================
# TECH STACK SUMMARY
# ==============================================================
#
# Frontend:
#   - Next.js 15 (App Router)
#   - Vanilla CSS (medical/clinical design system)
#   - Google OAuth (next-auth)
#   - Axios (API calls)
#   - Chart.js or Recharts (analytics)
#
# Backend:
#   - Python 3.11+
#   - FastAPI (async REST API)
#   - Motor (async MongoDB driver)
#   - LangChain + Google Gemini (LLM agents)
#   - PyPDF2 / python-docx (file parsing)
#   - ReportLab (PDF generation)
#   - python-jose (JWT tokens)
#   - Authlib (Google OAuth server-side)
#
# Database:
#   - MongoDB Atlas (cloud-hosted)
#
# Hosting:
#   - Azure App Service (backend)
#   - Azure Static Web Apps (frontend)
#   - GitHub Actions (CI/CD)
#
# ==============================================================

# Ready to start building? Let's go with STEP 1! 🚀
