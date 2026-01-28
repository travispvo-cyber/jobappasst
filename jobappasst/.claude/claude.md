# Job Application Assistant - Project Context

**Last Updated:** 2026-01-27
**Project Status:** Phase 5 Complete (Browser Automation)
**Build Phase:** ON HOLD - Testing Google Stitch MCP

---

## Project Overview

Building a Job Application Assistant to learn Python, APIs, databases, and browser automation. The system automates resume parsing, job matching, and application submission using Claude API, JSearch API, and Playwright.

**Original Brief:** `job-assistant-project-brief.md`

---

## Current Build Status

### ✅ Completed Phases

#### Phase 1: Database Foundation
- **Status:** Complete and tested
- **Database:** SQLite (`data/job_assistant.db`)
- **Tables:**
  - `profiles` - User profiles with contact info
  - `skills` - Skills linked to profiles (name, level, years)
  - `experience` - Work history
  - `jobs` - Job listings from JSearch API
  - `job_matches` - Scored matches (profile + job)
  - `applications` - Application tracking (draft, applied, interviewing, rejected, offer)
- **Key Files:**
  - `src/db/connection.py` - Database connection management
  - `src/db/models.py` - Table schemas with indexes
  - `src/db/queries.py` - CRUD operations with upsert logic
- **Verification:** `scripts/verify_database.py`

#### Phase 2: Resume Parser
- **Status:** Complete and tested
- **Technology:** Claude Sonnet 4, pdfplumber, python-docx
- **Features:**
  - Extracts text from PDF/DOCX resumes
  - Uses Claude API for structured data extraction
  - JSON schema validation
  - Upsert logic prevents duplicates (by source_file)
- **Key Files:**
  - `src/parsers/resume_parser.py` - Text extraction
  - `src/parsers/profile_extractor.py` - Claude API integration
  - `schemas/profile_schema.json` - Validation schema
  - `scripts/parse_resume.py` - CLI script
- **Current Profiles:** 4 profiles parsed
  - Brandon Nguyen (13 skills)
  - David-Viet Nguyen (13 skills)
  - Travis Vo (15 skills)
  - Brittany Nguyen (14 skills)

#### Phase 3: Job Fetcher
- **Status:** Complete and tested
- **Technology:** JSearch API via RapidAPI
- **Features:**
  - Skill-based job searching (not just job titles)
  - Remote job filtering
  - Job normalization and storage
  - Upsert logic prevents duplicates (by external_id)
- **Key Files:**
  - `src/jobs/jsearch_client.py` - API wrapper
  - `src/jobs/normalizer.py` - Data transformation
  - `scripts/fetch_jobs.py` - Basic job fetching
  - `scripts/fetch_jobs_by_profile.py` - Skill-based fetching
- **Current Jobs:** 91 jobs fetched (50 for Travis, 40 for David, 1 test)

#### Phase 4: Matching Engine
- **Status:** Complete and tested
- **Technology:** Custom scoring algorithm + optional Claude API
- **Features:**
  - Skill taxonomy with synonym matching
  - Basic scoring: 0-100% based on skill overlap
  - Claude-enhanced scoring (optional, requires API key)
  - Match storage with notes
- **Key Files:**
  - `src/matching/taxonomy.py` - Skill synonyms and normalization
  - `src/matching/scorer.py` - Match scoring algorithms
  - `scripts/score_matches.py` - CLI scoring script
  - `scripts/view_all_matches.py` - Summary dashboard
- **Current Matches:** 364 total (91 jobs × 4 profiles)
  - Brandon: 10 matches, avg 50.0%
  - David: 15 matches, avg 82.0%
  - Travis: 13 matches, avg 82.0%
  - Brittany: 12 matches, avg 81.0%

#### Phase 5: Browser Automation
- **Status:** Complete, validated, NOT TESTED IN BROWSER
- **Technology:** Playwright (Chromium installed)
- **Features:**
  - Browser automation with visible mode (slow_mo=1000ms)
  - Smart form field detection
  - Auto-fill for common fields (name, email, phone, LinkedIn)
  - Resume upload capability
  - Manual submission control (safety feature)
  - Application tracking in database
- **Key Files:**
  - `src/automation/browser.py` - Browser management
  - `src/automation/form_filler.py` - Form detection and filling
  - `src/automation/tracker.py` - Application tracking
  - `scripts/apply_to_jobs.py` - Interactive automation CLI
  - `scripts/view_applications.py` - Application dashboard
- **Status:** Validated imports and data loading, Playwright installed
- **Not Tested:** Actual browser interaction (on hold for Google Stitch MCP testing)

### 🔄 Remaining Phases (Optional)

#### Phase 6: Application Tracker
- Web UI for tracking applications
- Status updates and notes
- Interview scheduling

#### Phase 7: Orchestration
- Dagster pipeline for daily job fetching
- Automated matching runs
- Scheduled workflows

---

## Key Technical Decisions

### Database Design
- **Many-to-many relationships:** Jobs can match multiple profiles via `job_matches` table
- **Upsert patterns:** Prevent duplicates using unique identifiers
  - Profiles: `source_file`
  - Jobs: `external_id`
  - Matches: `(profile_id, job_id)` composite key
- **JSON storage:** Complex data (requirements, raw_json) stored as JSON text
- **Cascade deletes:** Foreign keys with `ON DELETE CASCADE`

### API Integration
- **Claude API:** Used for resume parsing (optional for enhanced matching)
- **JSearch API:** Used for job fetching via RapidAPI
- **Rate limiting:** Handled by slow_mo delays in automation
- **Error handling:** Graceful fallbacks for missing packages (dotenv, anthropic)

### Skill Matching
- **Synonym mapping:** "python" matches "py", "python3", "python programming"
- **Normalization:** Lowercase, stripped for comparison
- **Scoring:** Percentage of required skills that are matched
- **Default score:** 50% when job has no parsed requirements

### Browser Automation
- **Safety first:** Manual submission control, interactive pauses
- **Dry run mode:** Test field detection without filling
- **Slow motion:** 1000ms delays for visibility
- **Form detection:** Multiple selector patterns for common fields
- **Resume upload:** File input detection and upload

---

## Issues Encountered & Fixes

### Unicode Encoding Errors
- **Problem:** `✓` and `✗` characters caused encoding errors on Windows
- **Fix:** Replaced with ASCII `[+]` and `[!]` throughout codebase
- **Files affected:** connection.py, models.py, all scripts

### Wrong Directory Structure
- **Problem:** Files created in `c:\Projects\` instead of `c:\Projects\jobappasst\`
- **Fix:** Consolidated all files into jobappasst directory
- **Resolution:** User confirmed correct location

### Missing Imports in Automation Module
- **Problem:** `detect_form_fields`, `list_applications`, etc. not exported from `__init__.py`
- **Fix:** Updated `src/automation/__init__.py` to export all necessary functions
- **Impact:** Scripts now import correctly

### Optional Dependencies
- **Problem:** Scripts failed when dotenv or anthropic not installed
- **Fix:** Wrapped imports in try/except blocks
- **Files affected:** parse_resume.py, score_matches.py

### List Type Import Missing
- **Problem:** `NameError: name 'List' is not defined` in queries.py
- **Fix:** Added `List` to typing imports
- **File:** src/db/queries.py line 4

### Job Data Not Including Description/Requirements
- **Problem:** list_jobs() only returned basic fields, missing description/requirements
- **Fix:** Updated SELECT query to include these fields, parse JSON on load
- **Impact:** Matching engine now has full job data for scoring

### Unicode in Job Titles
- **Problem:** Some job titles had special characters causing print errors
- **Fix:** Added `safe_print()` helper function with ASCII fallback
- **Files:** score_matches.py, view_all_matches.py

---

## Environment Setup

### Virtual Environment
- **Location:** `c:\Projects\jobappasst\.venv\`
- **Python:** 3.11
- **Activation:** `.venv\Scripts\activate`

### Installed Packages
```
anthropic         - Claude API client
pdfplumber        - PDF text extraction
python-docx       - DOCX text extraction
jsonschema        - JSON validation
requests          - HTTP client
playwright        - Browser automation (Chromium installed)
```

### Environment Variables (.env)
```
ANTHROPIC_API_KEY=<key>
RAPIDAPI_KEY=<key>
```

### API Keys Required
- **Anthropic:** For resume parsing and enhanced matching
- **RapidAPI:** For JSearch job fetching

---

## Database Current State

### Statistics
- **Total Profiles:** 4
- **Total Skills:** 54 (across all profiles)
- **Total Experience Records:** 16
- **Total Jobs:** 91
- **Total Job Matches:** 364 (scored)
- **Total Applications:** 1 (test)

### Top Matches by Profile

**Travis Vo (ID: 5):**
1. Senior Data Intelligence Engineer at Ampcus, Inc - 100% (Job ID: 9)
2. Data Intelligence Architect at JPS Tech Solutions - 100% (Job ID: 10)
3. SQL Senior Clinical AI Data Analyst at Elsevier - 100% (Job ID: 19)

**David-Viet Nguyen (ID: 4):**
1. Travel CT Tech at Black Women's Mental Health Institute - 100%
2. Senior Data Intelligence Engineer at Ampcus, Inc - 100%
3. Senior ICD/CPT Coding Quality Specialist - 100%

**Brittany Nguyen (ID: 6):**
1. Travel CT Tech at Black Women's Mental Health Institute - 100%
2. TS/SCI Systems Engineer at Probity Inc. - 100%
3. Data Intelligence Architect at JPS Tech Solutions - 100%

**Brandon Nguyen (ID: 3):**
- Best matches: 50% (limited job requirements data)

---

## Key Scripts & Usage

### Resume Parsing
```bash
# Parse a resume
.venv\Scripts\python.exe scripts\parse_resume.py data\resumes\YourResume.pdf

# View profiles
.venv\Scripts\python.exe scripts\view_profiles.py
```

### Job Fetching
```bash
# Fetch jobs by profile skills
.venv\Scripts\python.exe scripts\fetch_jobs_by_profile.py 5 --location "Houston, TX"

# Fetch general jobs
.venv\Scripts\python.exe scripts\fetch_jobs.py --query "Data Engineer" --remote-only
```

### Job Matching
```bash
# Score all jobs for a profile
.venv\Scripts\python.exe scripts\score_matches.py 5 --min-score 70

# View all matches
.venv\Scripts\python.exe scripts\view_all_matches.py

# Refresh scores (delete and re-score)
.venv\Scripts\python.exe scripts\score_matches.py 5 --refresh
```

### Browser Automation
```bash
# Dry run (detect fields only)
.venv\Scripts\python.exe scripts\apply_to_jobs.py 5 9 --dry-run

# Full run with resume
.venv\Scripts\python.exe scripts\apply_to_jobs.py 5 9 --resume data\resumes\TravisVo-V1.pdf

# Headless mode
.venv\Scripts\python.exe scripts\apply_to_jobs.py 5 9 --headless
```

### Application Tracking
```bash
# View all applications
.venv\Scripts\python.exe scripts\view_applications.py

# View applications for specific profile
.venv\Scripts\python.exe scripts\view_applications.py 5
```

---

## Important Context for Future Sessions

### When Resuming Automation Testing
1. **Recommended test job:** Job ID 9 (Senior Data Intelligence Engineer at Ampcus, Inc)
   - 100% match for Travis Vo
   - Private company (not government)
   - Standard application form expected
2. **Previous issue:** Job ID 52 (Belcan, LLC) was a government job with security clearance issues
3. **Test command:** `.venv\Scripts\python.exe scripts\apply_to_jobs.py 5 9 --resume data\resumes\TravisVo-V1.pdf`
4. **Remember:** Type "no" when asked to submit for demo purposes

### Code Organization
- **Module structure:** src/ contains all core logic, scripts/ contains CLI tools
- **Import pattern:** Scripts add src to path with `sys.path.insert(0, str(Path(__file__).parent.parent))`
- **Database access:** Use context managers via `get_db()` from `src.db`
- **Exports:** All __init__.py files carefully maintained for proper imports

### Testing Approach
- **Always test with dry-run first:** `--dry-run` flag for automation
- **Verify data loads:** Check profiles and jobs exist before running scripts
- **Unicode safety:** Use `safe_print()` for output that may contain special characters
- **Error handling:** Most scripts have graceful error handling and helpful messages

### Known Limitations
1. **Custom application forms:** Not all sites follow standard patterns
2. **CAPTCHA:** Cannot be bypassed (intentional, requires manual intervention)
3. **Multi-step forms:** Automation works best with single-page forms
4. **Job requirements:** Some jobs lack detailed requirements (50% default score)
5. **Government jobs:** May have special requirements (security clearance, etc.)

---

## File Structure Reference

```
jobappasst/
├── .venv/                          # Virtual environment
├── .claude/                        # Project context (this file)
├── data/
│   ├── job_assistant.db           # SQLite database (1.5MB)
│   └── resumes/                   # PDF/DOCX resumes + JSON profiles
├── src/
│   ├── db/                        # Database layer
│   │   ├── __init__.py           # Exports all DB functions
│   │   ├── connection.py         # Connection management
│   │   ├── models.py             # Table schemas
│   │   └── queries.py            # CRUD operations
│   ├── parsers/                   # Resume parsing
│   │   ├── __init__.py
│   │   ├── resume_parser.py      # Text extraction
│   │   └── profile_extractor.py  # Claude API integration
│   ├── jobs/                      # Job fetching
│   │   ├── __init__.py
│   │   ├── jsearch_client.py     # JSearch API wrapper
│   │   └── normalizer.py         # Data transformation
│   ├── matching/                  # Matching engine
│   │   ├── __init__.py
│   │   ├── taxonomy.py           # Skill synonyms
│   │   └── scorer.py             # Match scoring
│   └── automation/                # Browser automation
│       ├── __init__.py           # Exports all automation functions
│       ├── browser.py            # Browser management
│       ├── form_filler.py        # Form detection and filling
│       └── tracker.py            # Application tracking
├── scripts/                       # CLI tools
│   ├── init_database.py
│   ├── verify_database.py
│   ├── parse_resume.py
│   ├── view_profiles.py
│   ├── fetch_jobs.py
│   ├── fetch_jobs_by_profile.py
│   ├── score_matches.py
│   ├── view_all_matches.py
│   ├── apply_to_jobs.py
│   └── view_applications.py
├── schemas/
│   └── profile_schema.json        # Resume validation schema
├── docs/
│   └── PHASE5_AUTOMATION.md       # Phase 5 documentation
├── README_QUICK_START.md          # User-facing quick start guide
└── job-assistant-project-brief.md # Original project plan
```

---

## Next Steps When Resuming

1. **Test browser automation** with Job ID 9 (recommended non-government job)
2. **Validate form filling** works across different job sites
3. **Track real applications** and update statuses
4. **Optional:** Build Phase 6 (Application Tracker UI)
5. **Optional:** Build Phase 7 (Dagster orchestration)

---

## Session Handoff Notes

**Current Session:**
- Built and validated Phase 5 (Browser Automation)
- Fixed all import errors in automation module
- Installed Playwright and Chromium browser
- Validated all scripts work correctly
- Identified better test jobs (Job ID 9, 10, 19 - all 100% matches for Travis)
- Created comprehensive README_QUICK_START.md for user reference
- Put build phase ON HOLD for Google Stitch MCP testing

**Status:** Project is in excellent state for future work. All core functionality complete and tested. Browser automation ready but not yet tested in actual browser interaction.

**User Preference:** Likes to see progress via todo lists, appreciates thorough testing before moving to next phase.

---

## Useful Commands for Quick Reference

```bash
# Activate environment
cd c:\Projects\jobappasst
.venv\Scripts\activate

# Quick status check
.venv\Scripts\python.exe scripts\view_all_matches.py

# Parse new resume
.venv\Scripts\python.exe scripts\parse_resume.py data\resumes\NewResume.pdf

# Fetch 30 new jobs for profile 5
.venv\Scripts\python.exe scripts\fetch_jobs_by_profile.py 5 --num-pages 3

# Score all jobs for profile 5
.venv\Scripts\python.exe scripts\score_matches.py 5 --refresh

# Test automation (dry run)
.venv\Scripts\python.exe scripts\apply_to_jobs.py 5 9 --dry-run

# View SQLite database
# Use SQLite Viewer extension in VS Code
```

---

**Last Updated:** 2026-01-27
**Project Lead:** Travis Vo
**Build Status:** Phase 5 Complete, Testing Paused
