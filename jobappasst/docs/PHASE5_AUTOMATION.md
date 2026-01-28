# Phase 5: Browser Automation - Documentation

## Overview

Phase 5 implements browser automation using Playwright to automatically fill out job application forms and track application status.

## Installation

Install Playwright and its browsers:

```bash
pip install playwright
playwright install
```

## Modules Created

### 1. src/automation/browser.py

Browser management and basic automation functions:
- `BrowserManager`: Context manager for Playwright browser instances
- `navigate_to_job()`: Navigate to job application URLs
- `wait_for_element()`: Wait for elements to appear
- `click_element()`: Click elements on the page
- `fill_input()`: Fill input fields
- `upload_file()`: Upload files (e.g., resume)
- `take_screenshot()`: Capture page screenshots

### 2. src/automation/form_filler.py

Form detection and filling logic:
- `ApplicationFormData`: Dataclass for application form data
- `find_field()`: Find form fields using common selectors
- `fill_application_form()`: Automatically fill application forms
- `detect_form_fields()`: Detect available fields on a page
- `click_submit_button()`: Find and click submit buttons

Common field detection for:
- Name (first/last)
- Email
- Phone
- LinkedIn URL
- Resume upload
- Cover letter

### 3. src/automation/tracker.py

Application tracking and database integration:
- `ApplicationStatus`: Enum for application statuses (draft, applied, interviewing, rejected, offer)
- `track_application()`: Record or update application in database
- `get_application()`: Retrieve application details
- `list_applications()`: List applications for a profile
- `update_application_status()`: Update application status
- `get_application_stats()`: Get statistics by status

## Scripts

### apply_to_jobs.py

Interactive automation for applying to jobs:

```bash
# Basic usage
python scripts/apply_to_jobs.py <profile_id> <job_id>

# With resume upload
python scripts/apply_to_jobs.py 5 52 --resume data/resumes/TravisVo-V1.pdf

# Dry run (detect fields only, don't fill)
python scripts/apply_to_jobs.py 5 52 --dry-run

# Headless mode (no browser window)
python scripts/apply_to_jobs.py 5 52 --headless
```

**Workflow:**
1. Loads profile and job from database
2. Opens browser and navigates to job application URL
3. Detects form fields on the page
4. Fills form with profile data
5. Prompts for manual submission review
6. Tracks application status in database

### view_applications.py

View application status and statistics:

```bash
# View summary for all profiles
python scripts/view_applications.py

# View detailed applications for a profile
python scripts/view_applications.py 5
```

## Usage Examples

### Example 1: Dry Run to Detect Fields

Before actually applying, see what fields are detected:

```bash
python scripts/apply_to_jobs.py 5 52 --dry-run
```

This will:
- Open the job application page
- Detect all form fields
- Show what fields can be auto-filled
- Not actually fill or submit anything

### Example 2: Apply with Resume

Apply to a job with resume upload:

```bash
python scripts/apply_to_jobs.py 5 52 --resume data/resumes/TravisVo-V1.pdf
```

The script will:
1. Navigate to the job URL
2. Auto-fill: name, email, phone, LinkedIn
3. Upload resume file
4. Wait for your confirmation before submitting
5. Track the application in the database

### Example 3: View Application History

Check which jobs you've applied to:

```bash
python scripts/view_applications.py 5
```

Shows:
- Total applications
- Breakdown by status (draft, applied, interviewing, etc.)
- List of recent applications with details

## Safety Features

1. **Manual Submission Control**: Script prompts before actually submitting applications
2. **Dry Run Mode**: Test field detection without filling forms
3. **Interactive Pauses**: Allows you to review before each major step
4. **Screenshot Support**: Can capture page state for debugging
5. **Error Handling**: Graceful fallback if fields can't be found

## Database Schema

The `applications` table tracks:
- `id`: Application ID
- `profile_id`: Which profile applied
- `job_id`: Which job
- `status`: Current status (draft, applied, interviewing, rejected, offer)
- `notes`: Application notes (fields filled, errors, etc.)
- `applied_at`: When application was submitted
- `updated_at`: Last status update

## Limitations

1. **Custom Forms**: Each company has unique application forms. The automation uses common patterns but may not work for all sites.

2. **CAPTCHA**: Cannot bypass CAPTCHA or reCAPTCHA (intentionally - these require manual intervention)

3. **Multi-Step Forms**: Some applications span multiple pages. Script handles single-page forms best.

4. **Required Fields**: Some required fields may not be auto-detected. Manual intervention may be needed.

5. **Rate Limiting**: Applying too quickly may trigger rate limits. Use slow_mo parameter for delays.

## Best Practices

1. **Always Dry Run First**: Use `--dry-run` to see what fields are detected before applying

2. **Manual Review**: Review each application before final submission

3. **Keep Notes**: Use the notes field to track special circumstances

4. **Update Status**: Update application status as you hear back from companies

5. **Resume Versions**: Keep different resume versions for different job types

## Troubleshooting

**Browser doesn't start:**
```bash
playwright install
```

**Fields not detected:**
- Try dry-run mode to see what's detected
- Inspect the page to find custom selectors
- Some sites may require manual application

**Upload fails:**
- Verify resume file path is correct
- Check file is not too large
- Ensure file is PDF or DOCX format

**Submission doesn't work:**
- Many sites have custom submit flows
- Manual submission may be required
- Script will track as "draft" if not submitted

## Next Steps

After Phase 5, you can:
1. Track application responses
2. Update statuses as you interview
3. Generate application reports
4. Move to Phase 6: Application Tracker UI
5. Move to Phase 7: Orchestration with Dagster

## Example Session

```bash
# 1. Find best matches for your profile
python scripts/score_matches.py 5 --min-score 80

# 2. Review top matches
python scripts/view_all_matches.py

# 3. Dry run on a top match (job ID 52)
python scripts/apply_to_jobs.py 5 52 --dry-run

# 4. Actually apply with resume
python scripts/apply_to_jobs.py 5 52 --resume data/resumes/TravisVo-V1.pdf

# 5. Check application status
python scripts/view_applications.py 5
```
