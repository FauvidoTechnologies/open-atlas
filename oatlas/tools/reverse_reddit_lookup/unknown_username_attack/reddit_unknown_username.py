# Copyright (c) 2025 Achintya Jai
# This file is part of the Atlas project.
# All rights reserved. Unauthorized use prohibited.

from typing import Dict

import requests

from oatlas import logger
from oatlas.config import API, Request

log = logger.get_logger()


class RedditUnknownEngine:
    """
    Class for running unknown username functions
    """

    @staticmethod
    def search_reddit_posts(
        query: str,
        subreddit: str = None,
        t: str = "all",
        limit: int = 25,
        sort: str = "relevance",
        restrict_sr: str = "true",
        type: str = "link",
    ):
        """
            Search Reddit posts matching a query.

        Args:
            query: Keywords to search for.
            subreddit: Optional subreddit to restrict search to.
            t: Time filter ('day', 'week', etc.).
            limit: Max number of results.
            sort: Sorting method ('relevance', 'new', etc.).
            restrict_sr: Whether to restrict search to the subreddit.
            type: Type of result (usually 'link').
        """
        log.warn("Reverse reddit searching with unknown username")

        config = {
            "q": query,
            "subreddit": subreddit,
            "t": t,
            "limit": limit,
            "sort": sort,
            "restrict_sr": restrict_sr,
            "type": type,
        }

        url_template = (
            API.reddit.search_post_across_subreddit
            if subreddit
            else API.reddit.search_post_across_reddit
        )

        url = url_template.format(**config)

        headers = {
            "User-Agent": Request.user_agents.common_linux,
            "Connection": "keep-alive",
            "Accept": "application/json",
        }

        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        try:
            return [c["data"] for c in data["data"]["children"]]
        except (KeyError, TypeError):
            return None

    @staticmethod
    def fetch_post_details(subreddit, post_id) -> Dict:
        log.warn(
            "Reverse reddit lookups: fetching the post details for {0} from {1}".format(
                post_id, subreddit
            )
        )
        headers = {
            "User-Agent": Request.user_agents.common_linux,
            "Connection": "keep-alive",
        }
        url = API.reddit.post_details.format(subreddit, post_id)

        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()

        return data

    @classmethod
    def get_abbr():
        return "ruE"
