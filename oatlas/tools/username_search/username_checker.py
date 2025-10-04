import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict

import requests

from oatlas.config import Config, UserAgents
from oatlas.logger import get_logger

log = get_logger()


class UsernameCheckEngine:
    """
    Functions to check if a certain username is available in different social media sites.
    Makes use of the OSS WhatsMyName @ WebBreacher
    """

    @staticmethod
    def check_usernames(username: str) -> Dict[str, str]:
        """
        Performs a username check on multiple different social media websites
        and returns a dictionary of all positive matches.
        Dict is a threadsafe datatype at cpython level so adding to it with multiple
        threads won't be an issue.

        Args:
            username: This is the username that we are scanning for
        Returns:
            A dictionaries with all found sites as keys and their
            URIs as values | an empty dictionary
        """
        log.info(
            "Enable verbose logging to get running information on the status of username scans"
        )
        final_dict = {}

        headers = {
            "Accept": "text/html, application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "accept-language": "en-US;q=0.9,en,q=0,8",
            "accept-encoding": "gzip, deflate",
            "user-Agent": UserAgents.common_linux,
        }

        with open(Config.path.username_search_urls, "r", encoding="utf-8") as f:
            data = json.load(f)

        sites = data["sites"]

        def check_site(site):
            name = site.get("name")
            uri_check = site.get("uri_check").format(account=username)

            try:
                log.verbose_info(f"Testing: {uri_check}")
                res = requests.get(uri_check, headers=headers, timeout=5)
                estring_pos = site["e_string"] in res.text
                estring_neg = site["m_string"] in res.text

                if res.status_code == site["e_code"] and estring_pos and not estring_neg:
                    log.excited(f"Found a match: {name}, {uri_check}")
                    return name, uri_check

            except Exception:
                return None

        # Decrease max_workers if the system is dying
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(check_site, site) for site in sites]
            for future in as_completed(futures):
                result = future.result()
                if result:
                    final_dict[result[0]] = result[1]

        return final_dict

    @classmethod
    def get_abbr():
        return "ucE"
