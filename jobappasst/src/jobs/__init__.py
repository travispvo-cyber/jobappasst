"""Job fetching module for Job Application Assistant"""

from .jsearch_client import JSearchClient, search_jobs
from .normalizer import normalize_job_data

__all__ = ['JSearchClient', 'search_jobs', 'normalize_job_data']
