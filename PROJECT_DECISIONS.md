# PROJECT DECISIONS & TASK TRACKER
# Cura3.ai — AI Agents for Medical Diagnostics
# =============================================================
# 
# Instructions:
#   - Write your answer next to "Answer:" for each question
#   - Use: yes / no / don't care / or a specific preference
#   - Once a feature is implemented, the status will be marked [x]
#
# Status Legend:
#   [ ] = Not started
#   [~] = In progress
#   [x] = Completed
#   [-] = Skipped / Not needed
#
# =============================================================


# ---------------------------------------------------------
# SECTION 1: TECH STACK & ARCHITECTURE
# ---------------------------------------------------------

## 1.1 Frontend Framework
# Question: Do you want a single-page web app (React/Next.js/Vite) 
#           or a simpler HTML/CSS/JS approach?
# Options:  React | Next.js | Vite | Plain HTML/CSS/JS
# Answer:   complete web app
# Status:   [ ]

## 1.2 Design Theme
# Question: Any design preference for the UI?
# Options:  Dark theme | Light theme | Medical/clinical look | 
#           Modern glassmorphism | Other (specify)
# Answer:   medical/clinical look
# Status:   [ ]

## 1.3 Mobile Responsive
# Question: Should the app be mobile-responsive (works on phones)?
# Options:  yes / no / don't care
# Answer:   yes
# Status:   [ ]

## 1.4 Backend Framework
# Question: Which Python backend framework should we use?
# Options:  FastAPI | Flask | Django
# Answer:   FastAPI
# Status:   [ ]

## 1.5 Database Needed
# Question: Do you need a database to store past diagnoses, 
#           user accounts, or uploaded reports?
# Options:  yes / no
# Answer:   yes
# Status:   [ ]

## 1.6 Database Choice (if yes to 1.5)
# Question: Which database do you prefer?
# Options:  PostgreSQL | MongoDB | SQLite | Other (specify)
# Answer:   MongoDB Atlas
# Status:   [ ]


# ---------------------------------------------------------
# SECTION 2: USER MANAGEMENT & ACCESS
# ---------------------------------------------------------

## 2.1 Authentication Required
# Question: Should users need to sign up / log in to use the app?
#           Or should it be open access (anyone with the URL)?
# Options:  Login required | Open access | Optional login
# Answer:   Login required
# Status:   [ ]

## 2.2 Authentication Method (if login required)
# Question: What login method should be supported?
# Options:  Google OAuth | Email-Password | Both | Other
# Answer:   Google OAuth
# Status:   [ ]

## 2.3 Role-Based Access
# Question: Do you need role-based access 
#           (e.g., Doctor vs Patient vs Admin)?
# Options:  yes / no / don't care
# Answer:   yes
# Status:   [ ]


# ---------------------------------------------------------
# SECTION 3: REPORT HANDLING
# ---------------------------------------------------------

## 3.1 User Report Upload
# Question: Should users be able to upload their own medical 
#           reports (.txt, .pdf, .docx)?
# Options:  yes / no
# Answer:   yes
# Status:   [ ]

## 3.2 Text Input
# Question: Should users be able to paste/type report text 
#           directly into a text box?
# Options:  yes / no
# Answer:   yes
# Status:   [ ]

## 3.3 Upload + Text (if yes to both 3.1 and 3.2)
# Question: Support both file upload AND text paste?
# Options:  yes / no / don't care
# Answer:   yes
# Status:   [ ]

## 3.4 Report Storage
# Question: Should the system store uploaded reports for future 
#           reference, or process and discard them?
# Options:  Store | Discard after processing | User chooses
# Answer:   User chooses
# Status:   [ ]


# ---------------------------------------------------------
# SECTION 4: AI AGENTS & FEATURES
# ---------------------------------------------------------

## 4.1 Number of Specialists
# Question: Currently there are 3 agents (Cardiologist, 
#           Psychologist, Pulmonologist). What do you want?
# Options:  Keep only 3 | Add more now (specify which) | 
#           Let users select from a bigger list
# Answer:   Let users select from a bigger list and also automatic selection of specialists based on the report
# Status:   [ ]

## 4.2 Additional Specialists (if adding more)
# Question: Which additional specialists should be added?
# Options:  Neurologist | Endocrinologist | Oncologist | 
#           Dermatologist | Gastroenterologist | Orthopedist |
#           Other (specify)
# Answer:   Auto select based on the report
# Status:   [ ]

## 4.3 User Selects Specialists
# Question: Should users be able to choose which specialists 
#           analyze their report?
# Options:  yes / no / don't care
# Answer:   Auto select based on the report
# Status:   [ ]

## 4.4 Show Individual Reports
# Question: Should the user see individual specialist reports 
#           in addition to the final combined diagnosis?
# Options:  yes / no / don't care
# Answer:   dont care
# Status:   [ ]

## 4.5 Follow-Up Chat
# Question: Do you want a chat/follow-up feature where users 
#           can ask questions about the diagnosis?
# Options:  yes / no / maybe later
# Answer:   yes
# Status:   [ ]


# ---------------------------------------------------------
# SECTION 5: OUTPUT & RESULTS
# ---------------------------------------------------------

## 5.1 On-Screen Display
# Question: Should diagnosis results be displayed on-screen 
#           in a nicely formatted UI?
# Options:  yes / no
# Answer:   yes
# Status:   [ ]

## 5.2 Downloadable Report
# Question: Should users be able to download the diagnosis 
#           report as a file?
# Options:  PDF | TXT | Both | No download needed
# Answer:   PDF
# Status:   [ ]

## 5.3 Diagnosis History
# Question: Should there be a history page where users can 
#           view their past diagnoses?
# Options:  yes / no / maybe later
# Answer:   yes
# Status:   [ ]


# ---------------------------------------------------------
# SECTION 6: HOSTING & DEPLOYMENT
# ---------------------------------------------------------

## 6.1 Hosting Platform
# Question: Where do you want to host this?
# Options:  Render (free) | Railway | Vercel + Render | 
#           AWS | Google Cloud | Azure | DigitalOcean | 
#           Other (specify)
# Answer:   Azure
# Status:   [ ]

## 6.2 Custom Domain
# Question: Do you have a domain name, or use the default 
#           URL from the hosting provider?
# Options:  Custom domain (specify) | Default URL | Buy one later
# Answer:   Buy one later
# Status:   [ ]

## 6.3 Cost Concern
# Question: Are you concerned about hosting cost?
# Options:  Free tier only | Low budget OK | Budget not a concern
# Answer:   Budget not a concern
# Status:   [ ]


# ---------------------------------------------------------
# SECTION 7: API KEY MANAGEMENT
# ---------------------------------------------------------

## 7.1 API Key Strategy
# Question: For a public product, how should the Gemini API 
#           key be handled?
# Options:  App uses your key (you bear cost) | 
#           Each user provides their own key |
#           Hybrid (free limited + bring your own key)
# Answer:   App uses your key (you bear cost)
# Status:   [ ]


# ---------------------------------------------------------
# SECTION 8: SECURITY & COMPLIANCE
# ---------------------------------------------------------

## 8.1 HTTPS
# Question: Enable HTTPS for secure connections?
# Note:     This is strongly recommended for any production app.
# Options:  yes / no
# Answer:   yes
# Status:   [ ]

## 8.2 Data Retention Policy
# Question: Should uploaded reports and diagnoses be 
#           auto-deleted after a certain period?
# Options:  yes (specify days) | no | don't care
# Answer:   no - manual deletion must be there
# Status:   [ ]

## 8.3 Disclaimer / Terms Page
# Question: Do you want a Terms of Service / Disclaimer page 
#           on the website?
# Options:  yes / no / don't care
# Answer:   yes
# Status:   [ ]

## 8.4 HIPAA Awareness
# Question: Should the app be HIPAA-aware (minimize storing 
#           sensitive patient data)?
# Options:  yes / no / don't care
# Answer:   yes
# Status:   [ ]


# ---------------------------------------------------------
# SECTION 9: SCALE & FUTURE
# ---------------------------------------------------------

## 9.1 Expected Users
# Question: How many users do you expect initially?
# Options:  Just demo/portfolio | Small group (<100) | 
#           Real product (100+)
# Answer:   Real product (100+)
# Status:   [ ]

## 9.2 Project Purpose
# Question: Is this primarily for a college project / portfolio 
#           showcase, or a real product?
# Options:  College project | Portfolio | Real product | All
# Answer:   portfolio and real product
# Status:   [ ]

## 9.3 Analytics Dashboard
# Question: Do you want analytics (track number of diagnoses, 
#           popular reports, usage stats, etc.)?
# Options:  yes / no / maybe later
# Answer:   yes
# Status:   [ ]


# =============================================================
# END OF DECISIONS
# =============================================================
# 
# Once all answers are filled in, we will create a detailed
# implementation plan and begin building feature by feature.
# Each completed feature will be marked [x] above.
# =============================================================
