import asyncio
import json
from typing import List, Dict

from playwright.async_api import async_playwright


# Helper function
async def extract_hrefs(url: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, wait_until="load", timeout=30000)

        # Extract all hrefs
        hrefs = await page.eval_on_selector_all("a", "elements => elements.map(el => el.href)")

        await browser.close()
        return hrefs


class HyperlinkExtractEngine:
    """
    This engine uses playwright to extract hyperlinks from a list of webpages or a single webpage. These
    hyperlinks can contain information about

    1. More relevant hyperlinks
    2. contact info (as in, `mailto:email@address.com`)
    3. LinkedIn, Twitter etc. cause people love to link that!
    """

    @staticmethod
    def hyperlinks_for_single_url(url: str) -> List[str]:
        """
        Extracts all the hyperlinks for a single URL and returns them as a list

        Args:
                url: A single URL for which the hyperlinks are to be extracted
        Returns:
                List<str>: List of hyperlinks found
        """
        links = asyncio.run(extract_hrefs(url))
        return json.dumps(links)  # Its just a list, we don't have to indent

    @staticmethod
    def hyperlinks_for_multiple_urls(urls: List) -> Dict[str, List[str]]:
        """
        Extracts all the hyperlinks for a list of URLs and returns them as a dictionary

        Args:
                urls: A list of URLs for which the hyperlinks are to be extracted
        Returns:
                Dict[str,List[str]]: {
                        "url1": ["link1", "link2", ...],
                        "url2": ["link1", "link2", ...],
                        ...
                }
        """
        output = {}

        for url in urls:
            links = asyncio.run(extract_hrefs(url))
            output[url] = json.dumps(links)

        return output
