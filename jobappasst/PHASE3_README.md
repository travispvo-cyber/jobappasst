# Phase 3: Job Fetcher - Setup Complete

Phase 3 of your Job Application Assistant is now ready! You can now fetch job listings from JSearch API and store them in your database.

## What Was Built

### Directory Structure
```
jobappasst/
├── src/
│   └── jobs/
│       ├── __init__.py
│       ├── jsearch_client.py     # JSearch API wrapper
│       └── normalizer.py          # Job data transformation
├── src/db/
│   └── queries.py                 # Added job storage functions
└── scripts/
    └── fetch_jobs.py              # Main CLI script
```

### New Database Functions
- `upsert_job(job_data)` - Insert or update jobs (prevents duplicates)
- `list_jobs(limit, remote_only)` - List recent jobs
- `get_job(job_id)` - Get full job details

## Setup Required

### 1. Get RapidAPI Key

1. Go to [RapidAPI JSearch](https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch)
2. Click "Subscribe to Test"
3. Select the **FREE** plan (500 requests/month)
4. Copy your API key from the code snippets

### 2. Add API Key to `.env`

Edit your `.env` file and add:

```bash
RAPIDAPI_KEY=your-rapidapi-key-here
```

## How to Use

### Fetch Jobs

```bash
python scripts/fetch_jobs.py "Python developer" --location "Houston, TX"
```

### Available Options

```bash
--location <location>      Location filter (e.g., 'Houston, TX')
--remote                   Only fetch remote jobs
--type <types>             Employment types (FULLTIME,CONTRACTOR,PARTTIME,INTERN)
--date <filter>            Date filter (all, today, 3days, week, month)
--pages <num>              Number of pages to fetch (default: 1)
```

### Examples

**Search for Python developers in Houston:**
```bash
python scripts/fetch_jobs.py "Python developer" --location "Houston, TX" --date week
```

**Search for remote Data Engineer jobs:**
```bash
python scripts/fetch_jobs.py "Data Engineer" --remote --type FULLTIME
```

**Search for recent Software Engineer jobs:**
```bash
python scripts/fetch_jobs.py "Software Engineer" --date 3days --pages 2
```

## What Happens

1. **Fetches jobs** from JSearch API based on your search
2. **Normalizes data** to match your database schema
3. **Stores in database** with upsert logic (no duplicates)
4. **Shows summary** of fetched jobs

### Example Output

```
======================================================================
Job Application Assistant - Job Fetcher
======================================================================

Search query: Python developer
Location: Houston, TX
Date filter: week
Pages to fetch: 1

Step 1: Fetching jobs from JSearch API...
[+] Fetched 15 jobs from API

Step 2: Normalizing job data...
[+] Normalized 15 jobs

Step 3: Storing jobs in database...
[+] Stored 15 new jobs
[+] Updated 0 existing jobs

======================================================================
SAMPLE JOBS FETCHED
======================================================================

Job 1:
Title: Senior Python Developer
Company: Tech Corp
Location: Houston, TX, US
Salary: $120,000 - $160,000
Posted: 2025-01-20
Requirements: 5 listed
Apply: https://example.com/apply

... and 10 more jobs

======================================================================

Total jobs in database: 15

======================================================================
[+] Job fetching complete!
```

## What Gets Stored in Database

### jobs table:
- Basic info (title, company, location)
- Salary range (if available)
- Remote flag
- Full description
- Requirements (JSON array)
- Apply URL
- Source (job board name)
- Posted date
- Full raw JSON from API

### Duplicate Prevention

Jobs are matched by `external_id` (JSearch job ID):
- **First fetch**: Creates new job
- **Subsequent fetches**: Updates existing job data
- **No duplicate jobs** in database

## API Costs & Limits

### Free Tier (RapidAPI JSearch)
- **500 requests/month** free
- Each search = 1 request
- Typical search returns 10-15 jobs
- **~30-50 job searches per month** on free tier

### Cost per Search
- **Free** on free tier
- Additional requests: ~$0.005 per request after limit

## Troubleshooting

### "RAPIDAPI_KEY environment variable required"

Make sure you've:
1. Set the API key in `.env`
2. Saved the file
3. Restarted any running scripts

### "No jobs found for this search"

Try:
- Broadening your search query
- Removing location filter
- Changing date filter to "all"
- Different keywords

### API Rate Limiting

If you hit the 500 request/month limit:
- Wait until next month
- Upgrade to paid plan
- Use more specific searches to reduce requests

## Database Schema

Jobs are stored with this structure:

```sql
CREATE TABLE jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    external_id TEXT UNIQUE,        -- JSearch job ID (prevents duplicates)
    title TEXT NOT NULL,
    company TEXT NOT NULL,
    location TEXT,
    remote BOOLEAN DEFAULT 0,
    description TEXT,
    requirements TEXT,              -- JSON array
    salary_min INTEGER,
    salary_max INTEGER,
    apply_url TEXT,
    source TEXT,                    -- Indeed, LinkedIn, etc.
    posted_date TEXT,
    fetched_at TIMESTAMP,           -- When we pulled it
    raw_json TEXT                   -- Full API response
);
```

## Next Steps

Once you've fetched some jobs:

1. **View in SQLite Viewer**: See all fetched jobs
2. **Query specific jobs**: Filter by remote, salary, location
3. **Move to Phase 4**: Matching Engine (score jobs against your profile!)

## Files You Can Customize

- `src/jobs/jsearch_client.py` - Add more API parameters
- `src/jobs/normalizer.py` - Change how data is transformed
- `scripts/fetch_jobs.py` - Customize output or filtering

## Learning Outcomes ✓

You've now learned:
- ✓ REST API integration (RapidAPI/JSearch)
- ✓ API authentication with headers
- ✓ Data normalization and transformation
- ✓ Upsert logic (prevent duplicates)
- ✓ CLI argument parsing
- ✓ Working with external job boards

**Phase 3 Complete!** 🎉

Ready for Phase 4: Matching Engine to score these jobs against your profile!
