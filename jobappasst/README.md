# Job Application Assistant 🤖

An intelligent automation tool that helps streamline the job application process using AI-powered resume parsing, smart job matching, and browser automation.

![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 🌟 Features

### 📄 Intelligent Resume Parsing
- Extracts structured data from PDF and DOCX resumes
- Powered by Claude AI for accurate skill and experience extraction
- Stores profiles in a structured SQLite database

### 🔍 Smart Job Matching
- Fetches relevant job listings via JSearch API
- Skill-based matching with synonym recognition (e.g., "Python" matches "Python3", "Py")
- Scores jobs 0-100% based on profile compatibility
- Supports remote job filtering

### 🎯 Automated Application Tracking
- Browser automation using Playwright
- Auto-detects and fills common application form fields
- Resume upload capability
- Tracks application status (draft, applied, interviewing, rejected, offer)

### 📊 Match Analytics
- View top job matches for each profile
- Filter by minimum match score
- Track matched vs. missing skills
- Application history and statistics

## 🚀 Quick Start

### Prerequisites
```bash
Python 3.11+
pip
```

### Installation

1. Clone the repository:
```bash
git clone https://github.com/travispvo-cyber/jobappasst.git
cd jobappasst
```

2. Create virtual environment:
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# or
source .venv/bin/activate  # Linux/Mac
```

3. Install dependencies:
```bash
pip install -r requirements.txt
playwright install chromium
```

4. Set up environment variables:
```bash
# Create .env file with:
ANTHROPIC_API_KEY=your_claude_api_key
RAPIDAPI_KEY=your_rapidapi_key
```

5. Initialize database:
```bash
python scripts/init_database.py
```

## 📖 Usage

### Parse a Resume
```bash
python scripts/parse_resume.py data/resumes/YourResume.pdf
```

### Fetch Jobs
```bash
# Fetch jobs based on profile skills
python scripts/fetch_jobs_by_profile.py <profile_id> --location "City, State"

# Example
python scripts/fetch_jobs_by_profile.py 1 --location "Houston, TX"
```

### Score Job Matches
```bash
# Score all jobs for a profile
python scripts/score_matches.py <profile_id> --min-score 70

# View all matches
python scripts/view_all_matches.py
```

### Apply to Jobs (Interactive)
```bash
# Dry run (detect fields only)
python scripts/apply_to_jobs.py <profile_id> <job_id> --dry-run

# Full run with resume
python scripts/apply_to_jobs.py <profile_id> <job_id> --resume data/resumes/YourResume.pdf
```

### View Application History
```bash
python scripts/view_applications.py <profile_id>
```

### Launch Web Interface (Streamlit)
```bash
streamlit run streamlit_app/app.py
```

Features:
- Dashboard with statistics
- Browse profiles, jobs, and matches
- Track applications with status updates
- Schedule interviews and set follow-up reminders
- Export application data to CSV

### Run Dagster Pipeline (Automated Orchestration)
```bash
# Install Dagster (if not already installed)
pip install dagster dagster-webserver

# Launch Dagster UI
python scripts/run_dagster.py
# or
dagster dev -m dagster_pipeline
```

Open http://localhost:3000 for the Dagster UI. The pipeline includes:
- **Daily Schedule**: Runs at 6 AM to fetch new jobs and score matches
- **all_profiles**: Loads all profiles from database
- **fetched_jobs**: Fetches jobs from JSearch API
- **scored_matches**: Scores all jobs against profiles

## 🏗️ Architecture

```
jobappasst/
├── src/
│   ├── db/              # Database layer (SQLite)
│   ├── parsers/         # Resume parsing (Claude AI)
│   ├── jobs/            # Job fetching (JSearch API)
│   ├── matching/        # Job matching engine
│   └── automation/      # Browser automation (Playwright)
├── streamlit_app/       # Web UI (Streamlit)
│   ├── pages/           # Multi-page app
│   ├── components/      # Reusable UI components
│   └── utils/           # Session state & formatters
├── dagster_pipeline/    # Workflow orchestration (Dagster)
│   ├── assets.py        # Data pipeline assets
│   └── resources.py     # Shared resources
├── scripts/             # CLI tools
├── data/
│   ├── resumes/         # Resume PDFs
│   └── *.db            # SQLite database (excluded from git)
├── schemas/             # JSON validation schemas
└── docs/               # Documentation
```

## 🛠️ Technology Stack

- **Language:** Python 3.11
- **Database:** SQLite3
- **AI/ML:** Anthropic Claude API
- **Job Data:** JSearch API (via RapidAPI)
- **Browser Automation:** Playwright
- **Web UI:** Streamlit
- **Orchestration:** Dagster
- **PDF Processing:** pdfplumber
- **Document Processing:** python-docx

## 📊 Database Schema

### Tables
- **profiles** - User profiles with contact information
- **skills** - Skills linked to profiles (name, level, years)
- **experience** - Work history
- **jobs** - Job listings from JSearch API
- **job_matches** - Scored matches (profile + job + score)
- **applications** - Application tracking with status

## 🎨 Features in Detail

### Resume Parser
- Extracts text from PDF/DOCX files
- Uses Claude AI to structure data
- Validates against JSON schema
- Prevents duplicates with upsert logic

### Job Fetcher
- Searches by skills, not just job titles
- Filters for remote positions
- Normalizes data from multiple sources
- Stores with deduplication

### Matching Engine
- Skill taxonomy with 50+ synonym mappings
- Basic scoring algorithm (0-100%)
- Optional Claude-enhanced matching
- Tracks matched vs. missing skills

### Browser Automation
- Smart form field detection
- Auto-fill for common fields
- Resume upload support
- Manual submission control (safety feature)
- Slow-motion mode for visibility

## 🔐 Security & Privacy

- ✅ `.env` file for API keys (excluded from git)
- ✅ Database excluded from version control
- ✅ Resume files excluded from git
- ✅ Manual submission control in automation
- ✅ No automatic submission without confirmation

## 📝 Example Workflow

1. **Parse Resume** → Extract skills and experience
2. **Fetch Jobs** → Find relevant positions based on skills
3. **Score Matches** → Calculate compatibility scores
4. **Review Matches** → See top matches with explanations
5. **Apply** → Use automation to fill applications
6. **Track** → Monitor application status

## 🤝 Contributing

This is a personal learning project. Feel free to fork and adapt for your own use!

## 📄 License

MIT License - See LICENSE file for details

## ⚠️ Disclaimer

This tool is for educational purposes and personal use. Always review applications before submission. Respect website terms of service and rate limits.

## 📚 Documentation

- [Quick Start Guide](README_QUICK_START.md)
- [Phase 5: Browser Automation](docs/PHASE5_AUTOMATION.md)
- [Dagster Pipeline](dagster_pipeline/README.md)
- [Project Context](.claude/claude.md)

## 🎯 Project Status

**Current Phase:** Phase 7 Complete (All Phases Done!)

### Completed
- ✅ Phase 1: Database Foundation
- ✅ Phase 2: Resume Parser
- ✅ Phase 3: Job Fetcher
- ✅ Phase 4: Matching Engine
- ✅ Phase 5: Browser Automation
- ✅ Phase 6: Application Tracker UI
- ✅ Phase 7: Dagster Orchestration

## 🌐 Live Demo

_Coming soon: Interactive landing page via Google Stitch_

## 📧 Contact

Built by Travis Vo as a learning project for Python, APIs, databases, and browser automation.

---

**Note:** This project requires valid API keys for Anthropic (Claude) and RapidAPI (JSearch). Some features may require additional setup.
