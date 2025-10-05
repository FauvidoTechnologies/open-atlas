try:
    from playwright.async_api import async_playwright
except ImportError:
    async_playwright = None
    from oatlas.logger import get_logger

    log = get_logger()
    log.error(
        "Playwright is not installed. Please install it using `pip install playwright` "
        "and run `playwright install` for browsers."
    )

from oatlas.config import Config
from oatlas.logger import get_logger

log = get_logger()


async def upload_via_playwright(image_path: str):
    if async_playwright is None:
        log.error("Playwright is not available, cannot perform image upload.")
        return None

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Session requires headless=False
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto(Config.API.isgen.image_detection_url, wait_until="networkidle")
        await page.set_input_files("input[type=file]", image_path)

        button_selector = "button:has-text('Run AI Detection')"
        await page.wait_for_selector(button_selector, state="visible")

        def log_request(request):
            if "detect-image" in request.url:
                log.verbose_info(
                    f"Request Headers for Isgen.ai image detection: {request.headers}"
                )

        page.on("request", log_request)

        async with page.expect_response("**/functions/v1/detect-image") as response_info:
            await page.click(button_selector)

        response = await response_info.value
        try:
            output = await response.json()
        except Exception:
            output = await response.text()

        await browser.close()

    return output
