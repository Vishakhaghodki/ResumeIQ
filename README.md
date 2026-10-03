# ResumeIQ – AI Resume Analyzer

Upload a PDF resume, paste a job description, and get a match score, ATS analysis, missing skills,
personalised suggestions and AI feedback, with history, a dashboard and downloadable reports.

## Features
- PDF upload with validation (type, magic bytes, 5 MB limit) and text extraction (`pypdf`)
- Resume parsing: name, email, phone, skills, education, experience, projects, certifications
- Resume vs job description: match score (skills 50%, keywords 30%, text similarity 20%)
- Missing skills and keywords, personalised suggestions
- ATS compatibility score (11 weighted checks, 100 points)
- AI feedback via a pluggable provider (Anthropic, OpenAI-compatible) with an offline **demo mode**
- SQLite history, delete, searchable history table
- Analytics dashboard (Chart.js): ATS gauge, skill match, missing skills, score history, distribution
- Downloadable HTML report (print to PDF from the browser)
- Responsive UI with automatic dark mode

## Tech stack
Python 3.10+, Flask, SQLite, pypdf, Pandas/NumPy, requests, HTML/CSS/JavaScript, Chart.js (CDN).

## Architecture
```
Browser (Jinja pages + fetch/Chart.js)
   │
Flask app factory (app.py)
   ├── routes/pages.py   → HTML pages
   ├── routes/api.py     → REST API (/api/...)
   ├── services/pipeline.py  orchestrates:
   │      pdf_extractor → parser → analyzer → ats → suggestions → ai/
   ├── database/repository.py → all SQL (SQLite, Pandas for stats)
   └── utils/            validators + AppError
```
AI providers live in `services/ai/`. To add one, subclass `AIProvider` (`base.py`) and return it from
`get_provider()` in `services/ai/__init__.py`. If the live call fails, the app falls back to demo mode.

## Installation (Windows, PowerShell)
```powershell
cd resumeiq
py -m venv venv
venv\Scripts\Activate.ps1        # if blocked: Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
pip install -r requirements.txt
```
(macOS/Linux: `python3 -m venv venv && source venv/bin/activate`.)

## Environment variables
```powershell
copy .env.example .env
```
Edit `.env`. Keys are read only from the environment, never hardcoded.

| Variable | Purpose |
|---|---|
| `SECRET_KEY` | Flask secret |
| `AI_PROVIDER` | `auto`, `anthropic`, `openai` or `demo` |
| `ANTHROPIC_API_KEY`, `ANTHROPIC_MODEL` | Anthropic provider |
| `OPENAI_API_KEY`, `OPENAI_MODEL`, `OPENAI_BASE_URL` | OpenAI-compatible provider |

With no key set, the app runs in **demo mode** (labelled in the UI).

## Database setup
Tables are created automatically on startup. To create them explicitly:
```powershell
python init_db.py
```
Tables: `users`, `resumes`, `extracted_info`, `job_descriptions`, `analyses`, `analysis_history`.
The database file is `instance/resumeiq.db`. Uploaded PDFs are not stored, only the extracted text.

## Run
```powershell
python app.py
```
Open http://127.0.0.1:5000. Run the tests with `python tests/smoke_test.py`.

## API endpoints
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/health` | Status and AI mode |
| POST | `/api/analyze` | multipart: `resume` (PDF), `job_title`, `job_description` → 201 with analysis |
| GET | `/api/analyses?limit=N` | List analyses |
| GET | `/api/analyses/<id>` | Full analysis JSON |
| DELETE | `/api/analyses/<id>` | Delete an analysis |
| GET | `/api/analyses/<id>/report` | Download HTML report |
| GET | `/api/stats` | Dashboard statistics |

Errors return `{"error": "message"}` with a 4xx/5xx status.

Pages: `/`, `/analyze`, `/result/<id>`, `/dashboard`, `/history`.

Example:
```powershell
curl -F "resume=@resume.pdf" -F "job_title=Backend Dev" -F "job_description=<text, 50+ chars>" http://127.0.0.1:5000/api/analyze
```

## Screenshots
_Add your screenshots to `docs/screenshots/` and link them here._
- Landing page: `docs/screenshots/landing.png`
- Analyze page: `docs/screenshots/analyze.png`
- Result page: `docs/screenshots/result.png`
- Dashboard: `docs/screenshots/dashboard.png`
- History: `docs/screenshots/history.png`

## Limitations
- Scanned/image-only PDFs aren't supported (no OCR).
- Parsing is rule-based and works best on standard single-column resumes.
- Skill detection uses a fixed taxonomy (`services/skills_data.py`); extend it for your domain.

## Future improvements
User accounts and login, OCR for scanned PDFs, DOCX support, embedding-based semantic matching,
PDF report export, multi-resume comparison, rewrite suggestions per bullet, Docker deployment.
