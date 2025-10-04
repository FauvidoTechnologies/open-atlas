from datetime import datetime
from typing import Dict, List, Union

import requests

from oatlas.config import Config, Request
from oatlas.logger import get_logger
from oatlas.tools.github_apis.trufflehog.trufflehog import run
from oatlas.utils.common import download_image_from_url

log = get_logger()


class GitHubEngine:
    """
    The GitHubEngine holds all the API endpoints that can be made using GitHub. It includes the one which require authorization
    and the user needn't worry about that. The basic authorisation key is set at "repo" access but in order to get more information
    users are encouraged to read the blog on adding their own API keys and  change it.

    The Engine holds functions to fetch an about information on the user on GitHub. This is also to verify if a certain username
    is present on GitHub or not! It has functions
    """

    @staticmethod
    def fetch_about(username: str) -> Dict:
        """
        Uses the about API to get a json response which is returned as a dicitionary

        I need this to have an authentication field as well!
        """
        output = {}

        log.warn("Fetching GitHub about page for: {}".format(username))
        url = Config.API.github.about_url.format(username=username)

        headers = {
            "User-Agent": Request.user_agents.common_linux,
            "Connection": "keep-alive",
        }

        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()

        try:
            profile_picture = data["avatar_url"]
            result = download_image_from_url(
                profile_picture, f"github_profile_picture_{username}.jpg"
            )

            if result:
                log.info(f"Found and downloaded the GitHub profile picture for {username}")
                output[
                    "downloaded_image"
                ] = f"github_profile_picture_{username}.jpg"  # Atlas knows where to look for this file
            else:
                log.info(f"Profile picture found but could not be downloaded: {profile_picture}")
                output[
                    "image_url"
                ] = profile_picture  # This should tell that downloading the image was not possible -> Make sure to include these caveats in the prompt

            # Some more potentially useful information we can take into account
            output_ = {
                "user_view_type": data["user_view_type"],  # public or private profile
                "name": data["name"],
                "company": data["company"],
                "blog": data["blog"],
                "location": data["location"],
                "bio": data["bio"],
                "twitter_username": data["twitter_username"],
                "followers": data["followers"],
                "created_at": str(
                    datetime.fromisoformat(data["created_at"].replace("Z", "+00:00"))
                ),  # Need to make this a string because datetime is not json serialisable
                "last_updated": str(
                    datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00"))
                ),
            }  # This will tell if they're active or not
            # The created at and last updated dates are in UTC -> We can convert this to local time? Or keep it UTC only?datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
            return output | output_

        except Exception:
            log.error("Couldn't get the GitHub about page")
            return {
                "result": False,
                "reason": "Hit API limit",
                "conclusion": "Try authenticating your requests or skip",
            }

    @staticmethod
    def fetch_repos(username: str) -> Dict:
        """
        Fetches all repositories of the username from GitHub and returns data on that as a dictionary

        Returns:
                - Repo description
                - Language
                - fork (yes or no basically)
                - created_at
                - Updated_at
        - as a dictionary
        """
        output = {}

        log.warn(f"Fetching GitHub repos for {username}")
        url = Config.API.github.repos_url.format(username=username)

        headers = {
            "User-Agent": Request.user_agents.common_linux,
            "Connection": "keep-alive",
        }

        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()

        try:
            # This will probably be a list -> Not sure if .json() will work here.
            for repo in data:
                output[repo.get("name")] = {
                    "is_private": repo.get("private"),
                    "is_fork": repo.get("fork"),
                    "stargazers_count": repo.get("stargazers_count"),
                    "created_at": str(repo.get("created_at")),
                    "updated_at": str(repo.get("updated_at")),
                    "language": repo.get("language"),
                }

            return output
        except Exception:
            log.error("Couldn't get the GitHub about page")
            return {
                "result": False,
                "reason": "Hit API limit",
                "conclusion": "Try authenticating your requests or skip",
            }

    @staticmethod
    def get_repo_secrets(
        repository_names: List[str],
        rules_file: str = Config.path.trufflehog_rules,
        processes: int = 4,
        verbose: int = 0,
    ) -> Union[str, Dict[str, str]]:
        """
        Function to use the trufflehog secret finder on any public GitHub repo

        Args:
            `repository_names`: List of repository URLs that are to be scanned
            `rules_file`: The rules file for trufflehog (we'll keep this at default for now)
            `processes`: The number of CPU cores to be used
            `verbose`: Verbose mode set to 0 (it just won't matter TBH)
        Returns:
            Template formatted output string through jninja or a dictionary explaining
            why the process failed
        """
        try:
            if not isinstance(repository_names, list):
                if isinstance(repository_names, str):
                    repository_names = repository_names.split(
                        ","
                    )  # No URL will have a comma, hence even comma seperated string would work
                else:
                    return {
                        "result": False,
                        "reason": "I need a list of GitHub URLs or commma seperated values",
                        "conclusion": "Please provide with a list of GitHub URLs or comma seperated URLs in a string",
                    }
            output = run(
                targets=repository_names,
                rules=rules_file,
                processes=processes,
                verbose=verbose,
            )

            return output
        except Exception as e:
            log.error(f"For some reason, running trufflehog failed: {e}")
            return {
                "result": False,
                "reason": e,
                "conclusion": "Unless explicitly fixed, don't try again",
            }

    # These are classmethods because all staticmethods will be read in the `registry.py` file~
    @classmethod
    def get_abbr():
        return "ghE"
