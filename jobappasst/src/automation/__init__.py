"""Browser automation module for Job Application Assistant"""

from .browser import BrowserManager, navigate_to_job
from .form_filler import fill_application_form, ApplicationFormData, detect_form_fields
from .tracker import (
    track_application,
    ApplicationStatus,
    list_applications,
    get_application_stats,
    get_application,
    update_application_status
)

__all__ = [
    'BrowserManager',
    'navigate_to_job',
    'fill_application_form',
    'ApplicationFormData',
    'detect_form_fields',
    'track_application',
    'ApplicationStatus',
    'list_applications',
    'get_application_stats',
    'get_application',
    'update_application_status'
]
