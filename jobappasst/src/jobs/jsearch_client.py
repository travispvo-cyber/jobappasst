"""JSearch API client for fetching job listings"""

import os
import requests
from typing import Dict, Any, List, Optional


class JSearchClient:
    """Client for the JSearch API on RapidAPI"""

    BASE_URL = "https://jsearch.p.rapidapi.com"

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize JSearch client.

        Args:
            api_key: RapidAPI key. If None, reads from RAPIDAPI_KEY environment variable
        """
        self.api_key = api_key or os.getenv("RAPIDAPI_KEY")

        if not self.api_key:
            raise ValueError(
                "RapidAPI key required. "
                "Provide via api_key parameter or RAPIDAPI_KEY environment variable"
            )

        self.headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
        }

    def search(
        self,
        query: str,
        location: Optional[str] = None,
        remote_jobs_only: bool = False,
        employment_types: Optional[str] = None,
        date_posted: str = "all",
        num_pages: int = 1,
        page: int = 1
    ) -> Dict[str, Any]:
        """
        Search for jobs using JSearch API.

        Args:
            query: Search query (e.g., "Python developer", "Data Engineer")
            location: Location filter (e.g., "Houston, TX", "Remote")
            remote_jobs_only: Only return remote jobs
            employment_types: Comma-separated employment types (FULLTIME, CONTRACTOR, PARTTIME, INTERN)
            date_posted: Date posted filter (all, today, 3days, week, month)
            num_pages: Number of pages to fetch (max 20 per request)
            page: Page number to start from

        Returns:
            dict: API response with job listings

        Raises:
            requests.RequestException: If API request fails
        """
        url = f"{self.BASE_URL}/search"

        params = {
            "query": query,
            "num_pages": str(num_pages),
            "page": str(page),
            "date_posted": date_posted
        }

        if location:
            params["location"] = location

        if remote_jobs_only:
            params["remote_jobs_only"] = "true"

        if employment_types:
            params["employment_types"] = employment_types

        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()

        except requests.RequestException as e:
            raise Exception(f"JSearch API request failed: {str(e)}")

    def get_job_details(self, job_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific job.

        Args:
            job_id: JSearch job ID

        Returns:
            dict: Detailed job information
        """
        url = f"{self.BASE_URL}/job-details"

        params = {"job_id": job_id}

        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()

        except requests.RequestException as e:
            raise Exception(f"JSearch API request failed: {str(e)}")


def search_jobs(
    query: str,
    location: Optional[str] = None,
    remote_jobs_only: bool = False,
    employment_types: Optional[str] = None,
    date_posted: str = "all",
    num_pages: int = 1,
    api_key: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Convenience function to search for jobs and return just the job list.

    Args:
        query: Search query
        location: Location filter
        remote_jobs_only: Only return remote jobs
        employment_types: Employment type filter
        date_posted: Date filter
        num_pages: Number of pages to fetch
        api_key: RapidAPI key (optional)

    Returns:
        list: List of job dictionaries

    Example:
        jobs = search_jobs("Python developer", location="Houston, TX", remote_jobs_only=False)
    """
    client = JSearchClient(api_key=api_key)
    response = client.search(
        query=query,
        location=location,
        remote_jobs_only=remote_jobs_only,
        employment_types=employment_types,
        date_posted=date_posted,
        num_pages=num_pages
    )

    return response.get("data", [])


# Example usage
if __name__ == "__main__":
    import json

    # Test the client
    try:
        client = JSearchClient()
        results = client.search(
            query="Python developer",
            location="Houston, TX",
            date_posted="week",
            num_pages=1
        )

        print(f"Found {len(results.get('data', []))} jobs")

        if results.get("data"):
            first_job = results["data"][0]
            print("\nFirst job:")
            print(json.dumps(first_job, indent=2))

    except Exception as e:
        print(f"Error: {e}")
