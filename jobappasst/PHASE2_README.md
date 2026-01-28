# Phase 2: Resume Parser - Setup Complete

Phase 2 of your Job Application Assistant is now ready! You can now parse PDF/DOCX resumes into structured data using Claude API.

## What Was Built

### Directory Structure
```
jobappasst/
├── data/
│   └── resumes/              # Place your resume files here
├── schemas/
│   └── profile_schema.json   # JSON schema for validation
├── src/
│   ├── parsers/
│   │   ├── resume_parser.py       # PDF/DOCX text extraction
│   │   └── profile_extractor.py   # Claude API parsing
│   └── db/
│       └── queries.py             # Database operations for profiles
└── scripts/
    └── parse_resume.py            # Main CLI script
```

### Installed Packages
- `pdfplumber` - Extract text from PDF files
- `python-docx` - Extract text from DOCX files
- `anthropic` - Claude API client (already installed)
- `jsonschema` - Validate extracted data

## Setup Required

### 1. Add Your Anthropic API Key

Edit `.env` and replace `your-key-here` with your actual API key:

```bash
ANTHROPIC_API_KEY=sk-ant-...your-actual-key...
```

Get your API key from: https://console.anthropic.com/

### 2. Load Environment Variables

The scripts will automatically load from `.env` using `python-dotenv`.

## How to Use

### Parse a Resume

1. Place your resume in `data/resumes/` (or anywhere)
2. Run the parser:

```bash
python scripts/parse_resume.py data/resumes/your_resume.pdf
```

### What Happens

1. **Text Extraction**: Extracts text from PDF/DOCX
2. **Claude Parsing**: Sends text to Claude API for structured extraction
3. **Validation**: Validates against JSON schema
4. **Storage**: Stores profile, skills, and experience in database
5. **Summary**: Displays parsed information

### Example Output

```
======================================================================
Job Application Assistant - Resume Parser
======================================================================

Resume file: data/resumes/john_doe_resume.pdf

Step 1: Extracting text from resume...
[+] Extracted 2,450 characters
[+] Found 87 lines

Step 2: Parsing resume with Claude API...
    (This may take 10-30 seconds)
[+] Successfully parsed profile
[+] Name: John Doe
[+] Skills: 12 skills extracted
[+] Experience: 3 positions

Step 3: Storing profile in database...
[+] Profile stored successfully!
[+] Profile ID: 1

======================================================================
PROFILE SUMMARY
======================================================================

Name:     John Doe
Email:    john.doe@example.com
Phone:    555-1234
Location: San Francisco, CA

Summary:
  Senior Software Engineer with 5+ years of experience...

Skills:
  - Python (advanced, 5.0 years)
  - JavaScript (intermediate, 3.0 years)
  - React (intermediate, 2.5 years)
  ...

Experience:
  - Senior Software Engineer at Tech Corp (2020-01 to present)
  - Software Engineer at Startup Inc (2018-06 to 2019-12)
  ...

======================================================================
[+] Resume parsing complete!
```

## Testing Individual Components

### Test Text Extraction Only

```bash
python src/parsers/resume_parser.py data/resumes/your_resume.pdf
```

### Test Claude Parsing (with extracted text file)

```bash
# First, extract text to a file
python src/parsers/resume_parser.py your_resume.pdf > resume_text.txt

# Then test Claude parsing
python src/parsers/profile_extractor.py resume_text.txt
```

## What Gets Stored in Database

### Profile Data
- Basic info (name, email, phone, location, summary)
- Full JSON in `raw_json` field
- Source filename
- Created/updated timestamps

### Skills (separate rows)
- Skill name
- Category (technical/soft/tool/concept)
- Level (beginner/intermediate/advanced)
- Years of experience
- Context (where/how used)

### Experience (separate rows)
- Job title, company, industry
- Start/end dates
- Responsibilities (JSON array)
- Accomplishments (JSON array)
- Skills used (JSON array)

## Troubleshooting

### "ANTHROPIC_API_KEY environment variable required"

Make sure you've:
1. Set the API key in `.env`
2. Saved the file
3. Restarted any running scripts

### "No text could be extracted from PDF"

Try:
- Make sure PDF is not image-based (scanned)
- Convert to DOCX if needed
- Check file is not corrupted

### "Extracted profile data doesn't match schema"

This means Claude returned data in unexpected format. The script tries to handle this, but you may need to:
- Check the resume has minimum required fields (name, at least one skill, one job)
- Try a different resume format
- Check Claude API status

## Cost Estimate

Claude API pricing (as of Jan 2025):
- Claude Sonnet 4: ~$3 per million input tokens, ~$15 per million output tokens
- Average resume: ~2,000 input tokens + ~1,500 output tokens
- **Cost per resume: ~$0.03 - $0.05**

Very affordable for learning and personal use!

## Next Steps

Once you've successfully parsed a resume:

1. **Explore the database**: Use SQLite Viewer to see stored data
2. **Parse multiple resumes**: Test with different formats
3. **Move to Phase 3**: Job Fetcher (fetch job listings from JSearch API)

## Files You Can Customize

- `schemas/profile_schema.json` - Modify validation rules
- `src/parsers/profile_extractor.py` - Adjust Claude prompt for better extraction
- `scripts/parse_resume.py` - Add custom processing or output

## Learning Outcomes ✓

You've now learned:
- ✓ File I/O with Python (PDF, DOCX, JSON)
- ✓ REST API usage (Anthropic Claude API)
- ✓ JSON schema validation
- ✓ Database operations (INSERT with foreign keys)
- ✓ CLI script creation
- ✓ Error handling and user feedback

**Phase 2 Complete!** 🎉
