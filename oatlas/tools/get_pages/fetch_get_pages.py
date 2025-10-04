from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Union

import requests

from oatlas.config import Request


class GetPagesEngine:
    """
    A simple engine for performing GET requests against one or more URLs.

    It is primarily designed for endpoints that return JSON-like responses,
    but works for any text-based response.

    Example:
        url = "https://www.hackerrank.com/rest/contests/master/hackers/{username}/profile"
        result = GetPagesEngine.fetch_get_page(url)
        print(result)

        urls = ["https://api.github.com", "https://httpbin.org/status/404"]
        results = GetPagesEngine.fetch_get_pages_bulk(urls)
        print(results)
    """

    COMMON_HEADERS = {"User-Agent": Request.user_agents.common_linux, "Accept": "application/json"}

    @staticmethod
    def fetch_get_page(url: str) -> Dict[str, Union[int, str]]:
        """
        Perform a synchronous GET request on a single URL.

        Args:
            url (str): The target URL.

        Returns:
            Dict[str, Union[int, str]]:
                A dictionary containing the status code and response text.
        """
        try:
            response = requests.get(url, headers=GetPagesEngine.COMMON_HEADERS, timeout=10)
            if response.text.lower().startswith("<!doctype html>"):
                return {"status": -1, "text": "This give useless HTML content"}
            return {"status": response.status_code, "text": response.text}
        except requests.RequestException as e:
            return {"status": -1, "text": str(e)}

    @staticmethod
    def fetch_get_pages_bulk(
        urls: List[str], max_workers: int = 10
    ) -> Dict[str, Dict[str, Union[int, str]]]:
        """
        Perform GET requests on multiple URLs concurrently using threads.

        Args:
            urls (List[str]): A list of target URLs.
            max_workers (int): Maximum number of threads to use.

        Returns:
            Dict[str, Dict[str, Union[int, str]]]:
                A mapping from URL → { "status": code, "text": response }
        """
        results: Dict[str, Dict[str, Union[int, str]]] = {}

        def fetch(url: str) -> Dict[str, Union[int, str]]:
            try:
                response = requests.get(url, headers=GetPagesEngine.COMMON_HEADERS, timeout=10)
                if response.text.lower().startswith("<!doctype html>"):
                    return {"status": -1, "text": "This give useless HTML content"}
                return {"status": response.status_code, "text": response.text}
            except requests.RequestException as e:
                return {"status": -1, "text": str(e)}

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {executor.submit(fetch, url): url for url in urls}
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    results[url] = future.result()
                except Exception as e:
                    results[url] = {"status": -1, "text": str(e)}

        return results
