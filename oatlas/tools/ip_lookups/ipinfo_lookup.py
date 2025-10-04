import json
import os

import requests
from dotenv import load_dotenv

from oatlas.config import API, Request

load_dotenv()


class IPinfoEngine:
    """
    For exposing the API endpoints for the IPinfo classes
    """

    @staticmethod
    def basic_ip_lookup(ipaddress) -> str:
        """
        The free API version lookups

        Args:
                ipaddress: The ipaddress to scan
        Returns:
                String for the recieved information

        The api token will be pulled from the free tier ones
        """
        api_token = os.getenv(API.ipinfo.api_token)
        url = API.ipinfo.base_url.format(ipaddress=ipaddress, api_token=api_token)

        headers = {"User-Agent": Request.user_agents.common_linux, "Accept": "application/json"}

        response = requests.get(url, headers=headers).json()

        return json.dumps(response, indent=2)  # Returning that as a string object

    @staticmethod
    def core_api_lookups(ipaddress) -> str:
        """
        This uses the paid version of the IPinfo API to perform ip lookups using the ipaddress
        """
        load_dotenv(".env.private")
        api_token = os.getenv(API.ipinfo.core_api_token)
        url = API.ipinfo.core_base_url_ipaddress.format(ipaddress=ipaddress, api_token=api_token)
        headers = {"User-Agent": Request.user_agents.common_linux, "Accept": "application/json"}

        response = requests.get(url, headers=headers).json()

        return json.dumps(response, indent=2)

    @staticmethod
    def core_api_lookups_asn(asn_number) -> str:
        """
        This uses the paid version of the IPinfo API to perform ip lookups using the ASN number
        """

        load_dotenv(".env.private")
        api_token = os.getenv(API.ipinfo.core_api_token)

        url = API.ipinfo.core_base_url_asn.format(ASN_number=asn_number, api_token=api_token)
        headers = {"User-Agent": Request.user_agents.common_linux, "Accept": "application/json"}

        response = requests.get(url, headers=headers).json()

        return json.dumps(response, indent=2)

    @classmethod
    def get_abbr():
        return "ipE"
