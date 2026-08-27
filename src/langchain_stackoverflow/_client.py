"""Stack Exchange API client wrapper.

Provides a clean interface for interacting with the Stack Exchange API v2.3,
handling pagination, filtering, and response parsing.
"""

from __future__ import annotations

from typing import Any
import requests
import re

class StackOverflowClient:
    """Wrapper around Stack Exchange API v2.3."""
    
    BASE_URL = "https://api.stackexchange.com/2.3"
    
    # Regex to extract question ID from a Stack Overflow URL
    SO_URL_PATTERN = re.compile(r"questions/(\d+)")
    SO_SHORT_URL_PATTERN = re.compile(r"q/(\d+)")
    
    def __init__(self, api_key: str | None = None) -> None:
        self._api_key = api_key
        self.session = requests.Session()
        
    def _make_request(self, endpoint: str, params: dict[str, Any]) -> dict[str, Any]:
        """Make a GET request to the API."""
        if self._api_key:
            params["key"] = self._api_key
            
        url = f"{self.BASE_URL}{endpoint}"
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Note: Stack Exchange API can return a 'backoff' field.
            # For a production client, we might want to respect this,
            # but for a simple retriever, we'll just return the data.
            if "error_id" in data:
                raise RuntimeError(f"Stack Exchange API Error {data['error_id']}: {data.get('error_message')}")
                
            return data
            
        except requests.RequestException as e:
            raise RuntimeError(f"Stack Exchange API request failed: {e}") from e

    def search_questions(
        self,
        query: str,
        max_results: int = 10,
        sort: str = "relevance",
        site: str = "stackoverflow",
        tagged: str | None = None,
        accepted_only: bool = False
    ) -> list[dict[str, Any]]:
        """Search Stack Exchange via /search/advanced endpoint.
        
        Args:
            query: Search query string.
            max_results: Maximum number of results to fetch.
            sort: 'relevance', 'votes', 'creation', 'activity'.
            site: Stack Exchange site (e.g., 'stackoverflow', 'serverfault').
            tagged: Semicolon-separated list of tags.
            accepted_only: If True, only return questions with accepted answers.
            
        Returns:
            List of matching questions.
        """
        endpoint = "/search/advanced"
        
        results: list[dict[str, Any]] = []
        page = 1
        pagesize = min(100, max_results)
        
        while len(results) < max_results:
            params = {
                "q": query,
                "site": site,
                "sort": sort,
                "pagesize": pagesize,
                "page": page,
                "filter": "withbody" # Required to get the question body
            }
            if tagged:
                params["tagged"] = tagged
            if accepted_only:
                params["accepted"] = "True"
                
            data = self._make_request(endpoint, params)
            
            items = data.get("items", [])
            if not items:
                break
                
            for item in items:
                if len(results) >= max_results:
                    break
                results.append(item)
                
            if not data.get("has_more", False):
                break
                
            page += 1
            
        return results

    def get_answers(
        self,
        question_id: int | str,
        sort: str = "votes",
        site: str = "stackoverflow"
    ) -> list[dict[str, Any]]:
        """Fetch all answers for a specific question via /questions/<id>/answers.
        
        Args:
            question_id: The Stack Exchange question ID.
            sort: 'votes', 'creation', 'activity'.
            site: Stack Exchange site.
            
        Returns:
            List of answer dictionaries.
        """
        endpoint = f"/questions/{question_id}/answers"
        
        results: list[dict[str, Any]] = []
        page = 1
        pagesize = 100
        
        while True:
            params = {
                "site": site,
                "sort": sort,
                "pagesize": pagesize,
                "page": page,
                "filter": "withbody" # Required to get the answer body
            }
            
            data = self._make_request(endpoint, params)
            
            items = data.get("items", [])
            results.extend(items)
                
            if not data.get("has_more", False):
                break
                
            page += 1
            
        return results

    @classmethod
    def extract_question_id(cls, url_or_id: str) -> str:
        """Extract question ID from a stackoverflow.com URL or raw ID."""
        url_or_id = str(url_or_id).strip()
        
        match = cls.SO_URL_PATTERN.search(url_or_id)
        if match:
            return match.group(1)
            
        match = cls.SO_SHORT_URL_PATTERN.search(url_or_id)
        if match:
            return match.group(1)
            
        if url_or_id.isdigit():
            return url_or_id
            
        raise ValueError(f"Could not extract a Stack Overflow question ID from: '{url_or_id}'")
