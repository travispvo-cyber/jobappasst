"""Job matching module for Job Application Assistant"""

from .scorer import calculate_basic_match_score, match_profile_to_job
from .taxonomy import normalize_skill, find_skill_synonyms

__all__ = ['calculate_basic_match_score', 'match_profile_to_job', 'normalize_skill', 'find_skill_synonyms']
