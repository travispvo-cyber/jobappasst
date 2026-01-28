"""Browser automation using Playwright"""

import os
import time
from typing import Optional, Dict, Any
from contextlib import contextmanager


class BrowserManager:
    """Manages Playwright browser instance for job applications"""

    def __init__(self, headless: bool = False, slow_mo: int = 500):
        """
        Initialize browser manager.

        Args:
            headless: Run browser in headless mode
            slow_mo: Slow down operations by N milliseconds
        """
        self.headless = headless
        self.slow_mo = slow_mo
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    def start(self):
        """Start the browser"""
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            raise ImportError(
                "Playwright is not installed. Install with: pip install playwright && playwright install"
            )

        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            slow_mo=self.slow_mo
        )
        self.context = self.browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        self.page = self.context.new_page()

        return self.page

    def stop(self):
        """Stop the browser"""
        if self.page:
            self.page.close()
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def __enter__(self):
        """Context manager entry"""
        return self.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop()


def navigate_to_job(page, job_url: str, timeout: int = 30000) -> bool:
    """
    Navigate to a job application URL.

    Args:
        page: Playwright page object
        job_url: URL to navigate to
        timeout: Navigation timeout in milliseconds

    Returns:
        bool: True if navigation successful
    """
    try:
        page.goto(job_url, timeout=timeout, wait_until='domcontentloaded')
        time.sleep(1)  # Wait for page to stabilize
        return True
    except Exception as e:
        print(f"Navigation error: {e}")
        return False


def take_screenshot(page, filepath: str) -> bool:
    """
    Take a screenshot of the current page.

    Args:
        page: Playwright page object
        filepath: Path to save screenshot

    Returns:
        bool: True if screenshot saved successfully
    """
    try:
        page.screenshot(path=filepath, full_page=True)
        return True
    except Exception as e:
        print(f"Screenshot error: {e}")
        return False


def wait_for_element(page, selector: str, timeout: int = 5000) -> bool:
    """
    Wait for an element to appear on the page.

    Args:
        page: Playwright page object
        selector: CSS selector
        timeout: Wait timeout in milliseconds

    Returns:
        bool: True if element found
    """
    try:
        page.wait_for_selector(selector, timeout=timeout, state='visible')
        return True
    except Exception:
        return False


def click_element(page, selector: str, timeout: int = 5000) -> bool:
    """
    Click an element on the page.

    Args:
        page: Playwright page object
        selector: CSS selector
        timeout: Wait timeout in milliseconds

    Returns:
        bool: True if click successful
    """
    try:
        page.wait_for_selector(selector, timeout=timeout, state='visible')
        page.click(selector)
        time.sleep(0.5)  # Wait for click to register
        return True
    except Exception as e:
        print(f"Click error: {e}")
        return False


def fill_input(page, selector: str, value: str, timeout: int = 5000) -> bool:
    """
    Fill an input field.

    Args:
        page: Playwright page object
        selector: CSS selector
        value: Value to fill
        timeout: Wait timeout in milliseconds

    Returns:
        bool: True if fill successful
    """
    try:
        page.wait_for_selector(selector, timeout=timeout, state='visible')
        page.fill(selector, value)
        time.sleep(0.3)  # Wait for input to register
        return True
    except Exception as e:
        print(f"Fill error: {e}")
        return False


def upload_file(page, selector: str, filepath: str, timeout: int = 5000) -> bool:
    """
    Upload a file to an input element.

    Args:
        page: Playwright page object
        selector: CSS selector for file input
        filepath: Path to file to upload
        timeout: Wait timeout in milliseconds

    Returns:
        bool: True if upload successful
    """
    try:
        if not os.path.exists(filepath):
            print(f"File not found: {filepath}")
            return False

        page.wait_for_selector(selector, timeout=timeout)
        page.set_input_files(selector, filepath)
        time.sleep(0.5)  # Wait for upload to register
        return True
    except Exception as e:
        print(f"Upload error: {e}")
        return False
