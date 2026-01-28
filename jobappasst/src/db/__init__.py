"""Database module for Job Application Assistant"""

from .connection import get_connection, init_db, get_db
from .models import create_all_tables, get_table_info
from .queries import (
    store_profile,
    get_profile,
    list_profiles,
    delete_profile,
    update_profile,
    find_profile_by_source,
    upsert_profile,
    store_job,
    find_job_by_external_id,
    upsert_job,
    list_jobs,
    get_job,
    store_job_match,
    upsert_job_match,
    get_matches_for_profile,
    get_top_matches,
    delete_matches_for_profile
)

__all__ = [
    'get_connection',
    'get_db',
    'init_db',
    'create_all_tables',
    'get_table_info',
    'store_profile',
    'get_profile',
    'list_profiles',
    'delete_profile',
    'update_profile',
    'find_profile_by_source',
    'upsert_profile',
    'store_job',
    'find_job_by_external_id',
    'upsert_job',
    'list_jobs',
    'get_job',
    'store_job_match',
    'upsert_job_match',
    'get_matches_for_profile',
    'get_top_matches',
    'delete_matches_for_profile'
]
