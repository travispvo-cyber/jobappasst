"""Form filling automation for job applications"""

import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class ApplicationFormData:
    """Data structure for job application form fields"""
    first_name: str
    last_name: str
    email: str
    phone: str
    location: Optional[str] = None
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    resume_path: Optional[str] = None
    cover_letter: Optional[str] = None
    years_experience: Optional[int] = None
    current_company: Optional[str] = None
    current_title: Optional[str] = None
    salary_expectation: Optional[str] = None


# Common field selectors for job application forms
COMMON_SELECTORS = {
    'first_name': [
        'input[name*="firstName"]',
        'input[name*="first_name"]',
        'input[name*="fname"]',
        'input[id*="firstName"]',
        'input[placeholder*="First"]',
        'input[aria-label*="First name"]'
    ],
    'last_name': [
        'input[name*="lastName"]',
        'input[name*="last_name"]',
        'input[name*="lname"]',
        'input[id*="lastName"]',
        'input[placeholder*="Last"]',
        'input[aria-label*="Last name"]'
    ],
    'email': [
        'input[name*="email"]',
        'input[type="email"]',
        'input[id*="email"]',
        'input[placeholder*="email"]',
        'input[aria-label*="Email"]'
    ],
    'phone': [
        'input[name*="phone"]',
        'input[type="tel"]',
        'input[id*="phone"]',
        'input[placeholder*="phone"]',
        'input[aria-label*="Phone"]'
    ],
    'linkedin': [
        'input[name*="linkedin"]',
        'input[name*="linkedIn"]',
        'input[id*="linkedin"]',
        'input[placeholder*="LinkedIn"]'
    ],
    'resume': [
        'input[type="file"][name*="resume"]',
        'input[type="file"][name*="cv"]',
        'input[type="file"][id*="resume"]',
        'input[type="file"][accept*="pdf"]'
    ],
    'cover_letter': [
        'textarea[name*="cover"]',
        'textarea[id*="cover"]',
        'textarea[placeholder*="cover"]'
    ]
}


def find_field(page, field_name: str) -> Optional[str]:
    """
    Find a form field using common selectors.

    Args:
        page: Playwright page object
        field_name: Field name from COMMON_SELECTORS

    Returns:
        str: Selector if found, None otherwise
    """
    if field_name not in COMMON_SELECTORS:
        return None

    for selector in COMMON_SELECTORS[field_name]:
        try:
            if page.query_selector(selector):
                return selector
        except Exception:
            continue

    return None


def fill_application_form(
    page,
    form_data: ApplicationFormData,
    dry_run: bool = False
) -> Dict[str, Any]:
    """
    Fill out a job application form.

    Args:
        page: Playwright page object
        form_data: Form data to fill
        dry_run: If True, only detect fields without filling

    Returns:
        dict: Results of form filling
    """
    results = {
        'filled_fields': [],
        'missing_fields': [],
        'errors': []
    }

    # Field mapping
    fields_to_fill = {
        'first_name': form_data.first_name,
        'last_name': form_data.last_name,
        'email': form_data.email,
        'phone': form_data.phone,
    }

    # Add optional fields if provided
    if form_data.linkedin_url:
        fields_to_fill['linkedin'] = form_data.linkedin_url

    # Fill text fields
    for field_name, value in fields_to_fill.items():
        selector = find_field(page, field_name)

        if selector:
            if not dry_run:
                try:
                    page.fill(selector, value)
                    time.sleep(0.3)
                    results['filled_fields'].append(field_name)
                except Exception as e:
                    results['errors'].append(f"{field_name}: {str(e)}")
            else:
                results['filled_fields'].append(field_name)
        else:
            results['missing_fields'].append(field_name)

    # Handle resume upload
    if form_data.resume_path:
        resume_selector = find_field(page, 'resume')
        if resume_selector:
            if not dry_run:
                try:
                    page.set_input_files(resume_selector, form_data.resume_path)
                    time.sleep(0.5)
                    results['filled_fields'].append('resume')
                except Exception as e:
                    results['errors'].append(f"resume: {str(e)}")
            else:
                results['filled_fields'].append('resume')
        else:
            results['missing_fields'].append('resume')

    # Handle cover letter
    if form_data.cover_letter:
        cover_selector = find_field(page, 'cover_letter')
        if cover_selector:
            if not dry_run:
                try:
                    page.fill(cover_selector, form_data.cover_letter)
                    time.sleep(0.3)
                    results['filled_fields'].append('cover_letter')
                except Exception as e:
                    results['errors'].append(f"cover_letter: {str(e)}")
            else:
                results['filled_fields'].append('cover_letter')

    return results


def detect_form_fields(page) -> Dict[str, List[str]]:
    """
    Detect available form fields on the page.

    Args:
        page: Playwright page object

    Returns:
        dict: Detected fields grouped by type
    """
    detected = {
        'text_inputs': [],
        'file_inputs': [],
        'textareas': [],
        'selects': [],
        'buttons': []
    }

    # Detect text inputs
    text_inputs = page.query_selector_all('input[type="text"], input[type="email"], input[type="tel"]')
    for inp in text_inputs:
        name = inp.get_attribute('name') or inp.get_attribute('id') or 'unknown'
        detected['text_inputs'].append(name)

    # Detect file inputs
    file_inputs = page.query_selector_all('input[type="file"]')
    for inp in file_inputs:
        name = inp.get_attribute('name') or inp.get_attribute('id') or 'unknown'
        detected['file_inputs'].append(name)

    # Detect textareas
    textareas = page.query_selector_all('textarea')
    for ta in textareas:
        name = ta.get_attribute('name') or ta.get_attribute('id') or 'unknown'
        detected['textareas'].append(name)

    # Detect select dropdowns
    selects = page.query_selector_all('select')
    for sel in selects:
        name = sel.get_attribute('name') or sel.get_attribute('id') or 'unknown'
        detected['selects'].append(name)

    # Detect submit buttons
    buttons = page.query_selector_all('button[type="submit"], input[type="submit"]')
    for btn in buttons:
        text = btn.inner_text() or btn.get_attribute('value') or 'Submit'
        detected['buttons'].append(text)

    return detected


def click_submit_button(page, timeout: int = 5000) -> bool:
    """
    Find and click the submit button.

    Args:
        page: Playwright page object
        timeout: Wait timeout in milliseconds

    Returns:
        bool: True if submit successful
    """
    submit_selectors = [
        'button[type="submit"]',
        'input[type="submit"]',
        'button:has-text("Submit")',
        'button:has-text("Apply")',
        'button:has-text("Send Application")',
        'a:has-text("Submit Application")'
    ]

    for selector in submit_selectors:
        try:
            if page.query_selector(selector):
                page.click(selector, timeout=timeout)
                time.sleep(1)
                return True
        except Exception:
            continue

    return False
