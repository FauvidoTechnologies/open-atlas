import os

import requests

from oatlas.config import UserAgents, HIBP
from oatlas.logger import get_logger

log = get_logger()


class HaveIBeenPwnedEngine:
    """
    Engine to make API calls to HaveIBeenPwned to see if the email has been pwned.
    """

    @staticmethod
    def check_email_against_breach_data(email: str) -> str:
        """
        uses the hibp-api-key to make API calls to HIBP datasets.
        """

        headers = {
            "hibp-api-key": os.getenv("hibp-api-key"),
            "User-Agent": UserAgents.common_linux,
        }

        url = HIBP.url.format(email=email)

        try:
            resp = requests.get(url, headers=headers, timeout=60)
            if resp.status_code == 200:
                breaches = resp.json()
                results = ""
                for index, breach in enumerate(breaches, start=1):
                    breach_name = breach.get("Name", "Unknown")
                    domain = breach.get("Domain", "Unknown")
                    breach_date = breach.get("BreachDate", "Unknown")
                    added_date = breach.get("AddedDate", "Unknown")
                    pwn_count = breach.get("PwnCount", "Unknown")
                    data_classes = ", ".join(breach.get("DataClasses", []))

                    results += f"| Breach #{index}: {breach_name}|\n"
                    results += f"|    Domain: {domain}|\n"
                    results += f"|    Breach Date: {breach_date}|\n"
                    results += f"|    Added Date:  {added_date}|\n"
                    results += f"|    PwnCount:    {pwn_count}|\n"
                    results += f"|    Data Types:  {data_classes}|\n"

                return results

            elif resp.status_code == 404:
                return "No beaches found"

            elif resp.status_code == 401:
                return "The API key was wrong -> Please look into the key used!"

        except Exception as e:
            log.error(f"There was an error with HIBP engine!: {e}")
            return "We came out with an error!"
