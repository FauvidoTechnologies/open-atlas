import asyncio
import re
from pathlib import Path
from typing import Dict

import requests
from bs4 import BeautifulSoup

from oatlas.config import API, UserAgents, Config
from oatlas.logger import get_logger
from oatlas.tools.reverse_instagram_lookup.utils import download_public_posts

log = get_logger()


def download_profile_picture(profile_pic_url: str) -> bool:
    """
    Helper function to download the profile picture

    Args:
            profile_pic_url: The URL to download from
    """
    profile_pic_download_dir = Config.path.image_file_dir / "scraped"
    response = requests.get(profile_pic_url, stream=True)

    if response.status_code == 200:
        with Path(profile_pic_download_dir / "instagram_profile_picture.jpg").open("wb") as fp:
            for chunk in response.iter_content(1024):
                fp.write(chunk)

        log.info(f"Extracted the instagram profile picture at: {profile_pic_download_dir}")
        return True
    else:
        log.error("Unable to download the profile picture")
        return False


class InstagramEngine:
    """
    Class to hold tools for Instagram account scraping (legally). This uses the fact that
    instagram renders the HTML page which includes basic information about an account which is
    used by crawlers to help in better ranking their results.

    For extracting more information like public posts and comments, its a slightly grey area so
    will be considered later
    """

    def __init__(self) -> None:
        self.profile_pic_download_dir = Config.path.image_file_dir / "scraped"

        try:
            self.profile_pic_download_dir.mkdir(exists_ok=True, parents=True)
        except PermissionError:
            log.error(
                "Couldn't create directory to store scraped images, some features might not be available"
            )

    @staticmethod
    def fetch_account_information(username: str) -> Dict:
        """
        Fetches	basic account information for a username and logs it into the database

        Args:
                username: The username to be scanned
        Returns:
                {
                        "num_followers": int,
                        "num_following": int,
                        "num_posts": int,
                        "profile_picture_path": Path,
                        "all_content": str
                        "profile_picture_basic_analysis": {
                                "race": "",
                                "emotion": "",
                                "age": "",
                                "gender": ""
                        }
                }

        The image analysis is performed after cleaning and resizing the image as the deepface models require them
        """

        url = API.instagram.base_url.format(username=username)
        headers = {
            "User-Agent": UserAgents.instagram_
        }  # Do not try to replicate a real browser here

        html = requests.get(url, headers=headers)
        soup = BeautifulSoup(html.text, "html.parser")

        # Fetching and downloading the profile picture
        profile_pic_tag = soup.find("meta", attrs={"property": "og:image"})
        profile_pic_url = profile_pic_tag["content"] if profile_pic_tag else None
        download_profile_picture(profile_pic_url)

        meta_tag = soup.find("meta", attrs={"name": "description"})
        if not meta_tag:
            meta_tag = soup.find("meta", attrs={"property": "og:description"})

        followers = following = posts = None
        if meta_tag and "content" in meta_tag.attrs:
            content = meta_tag["content"]
            # Matching for
            match = re.search(
                r"([\d.,]+[KMB]?) Followers, ([\d.,]+[KMB]?) Following, ([\d.,]+) Posts", content
            )
            if match:
                followers = match.group(1).replace(",", "")
                following = match.group(2).replace(",", "")
                posts = match.group(3).replace(",", "")

        # Need to perform image analysis and add that to the output
        return {
            "profile_picture_url": profile_pic_url,
            "num_followers": followers,
            "num_following": following,
            "num_posts": posts,
            "all_content": content,
        }

    @staticmethod
    def fetch_public_account_posts(username: str):
        """
        This is a more advanced browser automation tool. This is needed because
        the public posts are only made available after the javascript renders
        and hence we'll actually need to use a browser for this to work

        - Opens the URL with playwright
        - Goes over each post (there should be at max 12 if there are more than 12 posts)
        - Extracts the images, comments, likes and image analysis for each of them
        """

        instagram_url = API.instagram.base_url.format(username)
        output = asyncio.run(download_public_posts(instagram_url))

        return output

    @classmethod
    def get_abbr():
        return "insE"
