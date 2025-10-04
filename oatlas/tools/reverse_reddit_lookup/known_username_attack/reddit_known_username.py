from typing import Dict, List, Union

import requests

from oatlas import logger
from oatlas.config import API, Request

log = logger.get_logger()


class RedditKnownEngine:
    """
    Class for reverse reddit lookups on known usernames
    """

    @staticmethod
    def fetch_comments(username, limit=100) -> Union[List[dict], str, None]:
        """
        Fetch redditor's comments.
        Args:
                Limit to the comments
        Returns:
                The entire list as returned by the API call
        """
        log.warn("Reverse reddit lookups: fetching comments for {}".format(username))
        headers = {
            "User-Agent": Request.user_agents.common_linux,
            "Connection": "keep-alive",
        }

        url = API.reddit.comments.format(username, limit)

        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()

        try:
            output = []
            all_comments = [c["data"] for c in data["data"]["children"]]
            for comment in all_comments:
                output.append(
                    {
                        "post_title": comment.get("link_title", None),
                        "subreddit": comment.get("subreddit", None),
                        "comment": comment.get("body", None),
                    }
                )
            return output
        except (KeyError, TypeError):
            # This means either the output is differently formatted or the username is wrong
            if "error" in list(data.keys()) and data.get("error") == 404:
                return "Username doesn't exist"
            else:
                return None

    @staticmethod
    def fetch_about(username) -> Dict:
        """
        Fetch redditor's settings
        Args:
                None
        Returns:
                Redditor's about settings
        """
        log.warn("Reverse reddit lookups: fetching the about page for {}".format(username))
        headers = {
            "User-Agent": Request.user_agents.common_linux,
            "Connection": "keep-alive",
        }
        url = API.reddit.about.format(username)

        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()

        return data

    @staticmethod
    def fetch_user_posts(username) -> List:
        log.warn("Reverse reddit lookups: fetching {}'s posts".format(username))
        headers = {
            "User-Agent": Request.user_agents.common_linux,
            "Connection": "keep-alive",
        }
        url = API.reddit.user_submissions.format(username)

        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()

        try:
            return [c["data"] for c in data["data"]["children"]]
        except (KeyError, TypeError):
            return None

    @classmethod
    def get_abbr():
        return "rkE"
