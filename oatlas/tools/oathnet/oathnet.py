import os
from json.decoder import JSONDecodeError
from typing import Dict

import requests
from dotenv import load_dotenv

from oatlas.config import Config, Request
from oatlas.logger import get_logger

load_dotenv()

log = get_logger()


class OathNetEngine:
    """
    This engine is to call OathNet APIs because I don't want to get my own
    database of leaks.
    """

    headers = {
        "X-API-Key": os.getenv("oathnet_api_key"),
        "User-Agent": Request.user_agents.common_linux,
        "Content-Type": "application/json",
    }
    session_id = None
    timeout = 1.0

    @classmethod
    def initialize_with_query(cls, query: str) -> str:
        """
        The OathNetEngine needs to be initialised according to how the docs
        have mentioned: https://oathnet.org/api. Here we send a post request
        to the server saying that we'll be talking to it for the next 30 minutes.

        Then we'll hit the following endpoints as well and output the final report
        1. Search Stealer Logs: /search-stealer/
        2. Search Breaches: /search-breach/

        Args:
                query: A string containing a username, email-address or phonenumber

        Returns:
                session_id
        """

        url = Config.API.oathnet.init_url
        payload = {"query": query}

        r = requests.post(
            url, json=payload, headers=OathNetEngine.headers, timeout=OathNetEngine.timeout
        )

        try:
            data = r.json()
        except JSONDecodeError:
            log.error(f"There was an error initializing OathNet: {r.text}")
            return None

        if not data.get("success"):
            log.error("Failed to initialize search session: " + data.get("message"))
            return None

        session = data.get("data", {}).get("session")
        if not session:
            log.error("Something went wrong with initializing OathNet")
            return None

        session_id = session.get("id")

        return session_id

    @staticmethod
    def get_breached_data(query: str) -> Dict:
        """
        Hits the /search-breach/ endpoint with the query
        """
        if OathNetEngine.session_id is None:
            OathNetEngine.session_id = OathNetEngine.initialize_with_query(query)

        url = Config.API.oathnet.search_breach_url

        params = {"q": query, "search_id": OathNetEngine.session_id}

        response = requests.get(
            url, headers=OathNetEngine.headers, params=params, timeout=OathNetEngine.timeout
        )

        # Returning the response directly, later we can do more processing here
        try:
            return response.json()
        except JSONDecodeError:
            return response

    @staticmethod
    def get_stealer_logs(query: str) -> Dict:
        """
        Hits the /search-stealer/ endpoint with the query
        """
        if OathNetEngine.session_id is None:
            OathNetEngine.session_id = OathNetEngine.initialize_with_query(query)
        url = Config.API.oathnet.search_stealer_url

        params = {"q": query, "search_id": OathNetEngine.session_id}

        response = requests.get(
            url, headers=OathNetEngine.headers, params=params, timeout=OathNetEngine.timeout
        )

        # Returning the response directly, later we can do more processing here
        try:
            return response.json()
        except JSONDecodeError:
            return response

    @staticmethod
    def combined_oathnet_search(query: str) -> Dict:
        """
        Runs both the stealer data and breached data checker
        """

        if OathNetEngine.session_id is None:
            OathNetEngine.session_id = OathNetEngine.initialize_with_query(query)

        breached_data = OathNetEngine.get_breached_data(query)
        stealer_logs = OathNetEngine.get_stealer_logs(query)

        return {"breached_data": breached_data, "stealer_logs": stealer_logs}
