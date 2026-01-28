"""
Configuration file for Streamlit app
Manages imports and constants
"""

import sys
from pathlib import Path

# Add parent directory to path for importing src modules
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import database functions
from src.db.queries import (
    list_profiles,
    get_profile,
    upsert_profile,
    store_profile,
    delete_profile,
    list_jobs,
    get_job,
    upsert_job,
    get_matches_for_profile,
    get_top_matches,
    upsert_job_match,
)

from src.db.connection import get_db

# Import parsers
from src.parsers.resume_parser import extract_text_from_resume
from src.parsers.profile_extractor import extract_profile_from_text

# Import job search
from src.jobs.jsearch_client import JSearchClient
from src.jobs.normalizer import normalize_job_list, normalize_job

# Import matching
from src.matching.scorer import match_profile_to_job, calculate_basic_match_score
from src.matching.taxonomy import normalize_skill, find_skill_synonyms

# Constants
APP_TITLE = "Job Application Assistant"
APP_ICON = "🤖"
DEFAULT_PAGE_SIZE = 50
MIN_MATCH_SCORE = 0
MAX_UPLOAD_SIZE_MB = 10

# Status options for applications
APPLICATION_STATUSES = ["draft", "applied", "interviewing", "rejected", "offer"]

# Skill categories
SKILL_CATEGORIES = ["technical", "soft", "tool", "concept"]

# Skill levels
SKILL_LEVELS = ["beginner", "intermediate", "advanced"]
