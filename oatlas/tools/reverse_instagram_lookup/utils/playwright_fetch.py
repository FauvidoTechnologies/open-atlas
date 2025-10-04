from pathlib import Path

import requests
from playwright.async_api import async_playwright

from oatlas.config import Config
from oatlas.logger import get_logger

log = get_logger()


async def download_public_posts(url) -> None:
    """
    Function to download the public posts and save it in the specified directory
    The directory must be made known to atlas so that it can reference this later anytime it wants

    Returns:
        Thumbs list -> Also downloads and logs. The directory will be saved to state whenever this function is called
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        await page.goto(url, timeout=60000)
        await page.wait_for_selector("article img")

        # Grab the first 12 thumbnails
        imgs = await page.query_selector_all("article img")
        imgs = imgs[:12]

        thumbnail_download_dir = Config.path.instagram_scraped_dir
        thumbs = []
        for i, img in enumerate(imgs):
            src = await img.get_attribute("src")
            thumbs.append(src)
            log.excited("Extracting and downloading all public thumbnails")
            response = requests.get(src, stream=True)
            if response.status_code == 200:
                with Path(thumbnail_download_dir / "Thumbnail_{}.jpg".format(i + 1)).open(
                    "wb"
                ) as fp:
                    for chunk in response.iter_content(1024):
                        fp.write(chunk)
                log.info(f"Extracted the thumbnail_{i+1} at: {thumbnail_download_dir}")
            else:
                log.error("unable to download thumbnail_{}".format(i + 1))

        # Grab the followers and more information here
        await browser.close()
        return thumbs
