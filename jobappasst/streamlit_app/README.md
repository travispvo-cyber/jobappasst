# Streamlit Web Frontend - Job Application Assistant

A multi-user web interface for the Job Application Assistant, built with Streamlit.

## Installation

### 1. Install Streamlit Dependencies

From the project root directory, install the required packages:

```bash
pip install streamlit>=1.42.0
pip install plotly>=5.24.0
pip install altair>=5.5.0
```

Or create a `requirements-web.txt` file with:
```
streamlit>=1.42.0
plotly>=5.24.0
altair>=5.5.0
```

Then install:
```bash
pip install -r requirements-web.txt
```

## Running the App

### Local Development

From the project root directory (`jobappasst/`):

```bash
streamlit run streamlit_app/app.py
```

The app will open in your browser at `http://localhost:8501`

### Configuration

The app configuration is in `.streamlit/config.toml`:
- Theme colors
- Server port (default: 8501)
- Max upload size (10MB for resumes)
- CORS settings

## Features

### Phase 1 (Current) - Basic UI (Read-Only)
- ✅ Landing page with database statistics
- ✅ Profile selector in sidebar
- ✅ **Profiles Page**: View all profiles with skills and experience
- ✅ **Jobs Page**: Browse job listings with filters (remote, location, company)
- ✅ **Matches Page**: View job matches sorted by score

### Phase 2 (Coming Soon) - Interactive Features
- ⏳ Upload resume (PDF/DOCX)
- ⏳ Parse resume with Claude AI
- ⏳ Run job searches via JSearch API
- ⏳ Update application status
- ⏳ Add notes to applications

### Phase 3 (Future) - Polish & Analytics
- ⏳ Dashboard with charts and metrics
- ⏳ Match score visualizations (gauges, radar charts)
- ⏳ Export to CSV
- ⏳ Advanced filtering

## Usage

1. **Select a Profile**: Use the sidebar dropdown to select a user profile
2. **Browse Jobs**: Navigate to the Jobs page to see available positions
3. **View Matches**: Check the Matches page for personalized job recommendations
4. **Filter Results**: Use sidebar filters to narrow down jobs and matches

## Multi-User Support

The app supports multiple users through a simple profile selector:
- Each user selects their profile from the sidebar
- Data is isolated per profile
- No authentication required (trust-based system)

## Deployment Options

### Streamlit Community Cloud (Free)
1. Push code to GitHub
2. Connect repo at [share.streamlit.io](https://share.streamlit.io)
3. Set environment secrets (ANTHROPIC_API_KEY, RAPIDAPI_KEY)
4. Deploy

### Docker
```bash
docker build -t jobappasst .
docker run -p 8501:8501 jobappasst
```

### Heroku/Railway/Render
Add a `Procfile`:
```
web: streamlit run streamlit_app/app.py --server.port=$PORT
```

## Project Structure

```
streamlit_app/
├── app.py                      # Main landing page
├── config.py                   # Imports and constants
├── pages/                      # Multi-page app
│   ├── 2_👤_Profiles.py
│   ├── 3_💼_Jobs.py
│   └── 4_🎯_Matches.py
├── components/                 # Reusable UI components
│   ├── profile_card.py
│   └── job_card.py
└── utils/                      # Utilities
    └── session_state.py
```

## Technology Stack

- **Streamlit**: Web framework
- **Python**: Backend (reuses existing `src/` modules)
- **SQLite**: Database (shared with CLI)
- **Plotly/Altair**: Visualizations (Phase 3)

## Notes

- All business logic is in the existing `src/` directory (no code duplication)
- The web interface shares the same SQLite database as the CLI tools
- Both CLI and web interface can be used simultaneously

## Troubleshooting

**Import errors**: Make sure you're running from the project root directory.

**Database not found**: The app looks for `data/job_assistant.db` relative to the project root.

**API keys**: Make sure `.env` file exists with `ANTHROPIC_API_KEY` and `RAPIDAPI_KEY`.

**Port already in use**: Change the port in `.streamlit/config.toml` or use `--server.port=8502`.
