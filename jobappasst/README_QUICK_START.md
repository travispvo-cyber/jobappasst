# Job Application Assistant - Quick Start Guide

## Project Overview

A Python-based job application assistant that automates resume parsing, job matching, and application submission.

**Current Status:** ✅ Phases 1-5 Complete

## What's Built

### Phase 1: Database Foundation ✅
- SQLite database with 6 tables
- Profile, skills, experience, jobs, job_matches, applications tracking

### Phase 2: Resume Parser ✅
- Claude API integration for intelligent resume parsing
- Extracts skills, experience, contact info
- Stores structured data in database

### Phase 3: Job Fetcher ✅
- JSearch API integration
- Skill-based job searching (not just job titles)
- Fetches 91 jobs currently in database

### Phase 4: Matching Engine ✅
- Skill taxonomy with synonym matching
- Basic scoring algorithm (0-100%)
- Optional Claude-enhanced matching
- 364 job matches scored across 4 profiles

### Phase 5: Browser Automation ✅
- Playwright-based automation
- Auto-detects and fills application forms
- Resume upload capability
- Manual submission control (safety feature)

## Database Summary

```
4 Profiles:
  - Brandon Nguyen: 13 skills, 10 matches (avg 50.0%)
  - David-Viet Nguyen: 13 skills, 15 matches (avg 82.0%)
  - Travis Vo: 15 skills, 13 matches (avg 82.0%)
  - Brittany Nguyen: 14 skills, 12 matches (avg 81.0%)

91 Jobs fetched
364 Job matches scored
```

## Quick Start Commands

### 1. View All Matches
```bash
.venv\Scripts\python.exe scripts\view_all_matches.py
```

### 2. View Top Matches for a Profile
```bash
.venv\Scripts\python.exe scripts\score_matches.py 5 --min-score 80
```

### 3. Parse a New Resume
```bash
.venv\Scripts\python.exe scripts\parse_resume.py data\resumes\YourResume.pdf
```

### 4. Fetch More Jobs
```bash
.venv\Scripts\python.exe scripts\fetch_jobs_by_profile.py 5 --location "Houston, TX"
```

### 5. Apply to a Job (INTERACTIVE)
```bash
# Full run with resume
.venv\Scripts\python.exe scripts\apply_to_jobs.py 5 52 --resume data\resumes\TravisVo-V1.pdf

# Dry run (detect fields only)
.venv\Scripts\python.exe scripts\apply_to_jobs.py 5 52 --dry-run
```

### 6. View Application History
```bash
.venv\Scripts\python.exe scripts\view_applications.py 5
```

## Browser Automation Demo

### Step-by-Step Experience

**Command:**
```bash
cd c:\Projects\jobappasst
.venv\Scripts\python.exe scripts\apply_to_jobs.py 5 52 --resume data\resumes\TravisVo-V1.pdf
```

**What Happens:**

#### 1. Initial Information Display
```
Profile: Travis Vo (travisphamvo@hotmail.com)
Job: Computer Systems Analyst ID# 18055148 Jobs
Company: Belcan, LLC
Location: Arlington, Virginia, US
Apply URL: https://www.clearancejobs.com/jobs/...
```

#### 2. Browser Opens Automatically
- Chrome browser window appears (visible, not headless)
- Navigates to job application page
- Slow motion: 1000ms delays between actions

#### 3. Interactive Pause 1
```
Press Enter when ready to detect form fields...
```
**What to do:**
- Look at the job posting
- Review the application form
- Press **Enter** when ready

#### 4. Field Detection Results
```
Detecting form fields...
  Text inputs: 8
    - firstName
    - lastName
    - email
    - phone
    - linkedin
    ... and 3 more
  File inputs: 1
    - resume
  Textareas: 2
    - coverLetter
    - additionalInfo
```

#### 5. Interactive Pause 2
```
Press Enter to fill the form...
```
**What to do:**
- Review what fields were detected
- Press **Enter** to watch auto-fill

#### 6. Form Auto-Fill (Watch It Happen!)
```
Filling form...
[+] Filled fields: first_name, last_name, email, phone, resume
[!] Missing fields: linkedin, cover_letter
```
- Fields populate in slow motion
- Resume file uploads
- You see every action happen

#### 7. Submission Confirmation
```
Submit application? (yes/no):
```
**What to do:**
- Type **"no"** to NOT submit (recommended for demo)
- Type **"yes"** to actually submit
- Application tracked in database either way

#### 8. Final Review
```
[+] Saved as draft (ID: 42)

Press Enter to close browser...
```
**What to do:**
- Review the filled form in the browser
- Check that everything looks correct
- Press **Enter** when done
- Browser closes automatically

## Common Use Cases

### Use Case 1: Find Best Matches
```bash
# Score all jobs for your profile
.venv\Scripts\python.exe scripts\score_matches.py 5 --min-score 70

# View top matches
.venv\Scripts\python.exe scripts\view_all_matches.py
```

### Use Case 2: Apply to Top 3 Jobs
```bash
# Apply to job IDs 52, 53, 54 (from top matches)
.venv\Scripts\python.exe scripts\apply_to_jobs.py 5 52 --resume data\resumes\TravisVo-V1.pdf
.venv\Scripts\python.exe scripts\apply_to_jobs.py 5 53 --resume data\resumes\TravisVo-V1.pdf
.venv\Scripts\python.exe scripts\apply_to_jobs.py 5 54 --resume data\resumes\TravisVo-V1.pdf
```

### Use Case 3: Track Application Progress
```bash
# View all applications
.venv\Scripts\python.exe scripts\view_applications.py 5

# Update status in database (using SQLite Viewer extension)
# Or add update script if needed
```

## Project Structure

```
jobappasst/
├── data/
│   ├── job_assistant.db          # SQLite database
│   └── resumes/                  # Resume PDFs
├── src/
│   ├── db/                       # Database layer
│   ├── parsers/                  # Resume parsing
│   ├── jobs/                     # Job fetching (JSearch API)
│   ├── matching/                 # Matching engine
│   └── automation/               # Browser automation (Playwright)
├── scripts/                      # CLI scripts
├── docs/                         # Documentation
└── .venv/                        # Virtual environment
```

## Important Notes

### Safety Features
1. **Manual Submission**: Script asks for confirmation before submitting
2. **Dry Run Mode**: Test field detection without filling
3. **Interactive Pauses**: Review at each step
4. **Draft Tracking**: Applications saved even if not submitted
5. **Browser Stays Open**: Review filled form before closing

### Limitations
1. **Custom Forms**: Each company has unique forms - automation may not work for all sites
2. **CAPTCHA**: Cannot bypass CAPTCHA (requires manual intervention)
3. **Multi-Step Forms**: Best for single-page applications
4. **Required Fields**: Some fields may need manual input

### Tips
1. Always run with `--dry-run` first to see what fields are detected
2. Keep resume file path handy
3. Review application before confirming submission
4. Update application status as you hear back from companies
5. Save different resume versions for different job types

## Environment Setup

If you need to reinstall packages:

```bash
# Activate virtual environment
.venv\Scripts\activate

# Install core packages
pip install anthropic pdfplumber python-docx jsonschema requests

# Install Playwright
pip install playwright
playwright install chromium

# Verify installation
python -c "from playwright.sync_api import sync_playwright; print('Playwright ready!')"
```

## Troubleshooting

**Browser doesn't open:**
```bash
playwright install chromium
```

**Import errors:**
```bash
# Make sure you're in the project root
cd c:\Projects\jobappasst

# Run scripts using .venv Python
.venv\Scripts\python.exe scripts/apply_to_jobs.py 5 52
```

**Fields not detected:**
- Try dry-run mode first
- Some sites have non-standard forms
- May require manual application

**Resume upload fails:**
- Verify file path is correct
- Check file exists and is readable
- Ensure file is PDF or DOCX

## Next Steps

### Phase 6: Application Tracker (Optional)
- Web UI for tracking applications
- Email notifications
- Interview scheduling

### Phase 7: Orchestration (Optional)
- Dagster pipeline for daily job fetching
- Automated matching runs
- Scheduled application submissions

## Support

For issues or questions, check:
- `docs/PHASE5_AUTOMATION.md` - Detailed automation docs
- Project brief: `job-assistant-project-brief.md`
- Database: Use SQLite Viewer extension in VS Code

## Demo Command (Try This First!)

```bash
cd c:\Projects\jobappasst
.venv\Scripts\python.exe scripts\apply_to_jobs.py 5 52 --resume data\resumes\TravisVo-V1.pdf
```

**Remember:** Type "no" when asked to submit, so it's saved as a draft for demo purposes.
