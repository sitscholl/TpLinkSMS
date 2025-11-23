from playwright.async_api import async_playwright
from typing import List

import time
from pathlib import Path

import logging
logger = logging.getLogger(__name__)

class Router:
    def __init__(self, url: str, password: str, user: str | None = None, debug: bool = False):
        self.url = url
        self.user = user
        self.password = password
        self.debug = debug

    async def _snap(self, page, tag):
        """Save screenshots during debugging"""

        if not self.debug:
            return
        ts = time.strftime("%Y%m%d-%H%M%S")
        shot_dir = Path("debug-shots")
        shot_dir.mkdir(exist_ok=True)
        await page.screenshot(path=shot_dir / f"{ts}-{tag}.png", full_page=True)

    async def send_sms(self, to_numbers: List[str], message: str):
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
                ctx = await browser.new_context()
                page = await ctx.new_page()

                # 1) Login – adjust selectors to your router’s DOM
                await page.goto(self.url, wait_until="domcontentloaded")
                await page.wait_for_selector('input[id="pc-login-password"]', timeout=8000)
                logger.debug('Loaded login page')
                await self._snap(page, "login-loaded")

                # Example selectors – you must inspect your router’s login page and replace:
                await page.fill('input[id="pc-login-password"]', self.password)
                await page.click('button:has-text("Log In")')
                await page.wait_for_load_state("networkidle")

                # Give the conflict popup a chance to appear; ignore timeout if nothing shows
                try:
                    await page.wait_for_selector("button[id=confirm-yes]", timeout = 8000)
                    logger.info("Existing session detected, forcing logout")
                    await page.click('button[id=confirm-yes]')  # confirm takeover
                    await page.wait_for_load_state("networkidle")
                except Exception:
                    pass  # no other device logged in   

                # Optional: assert we’re logged in (look for a known element)
                await page.wait_for_selector('a[id=topLogout]', state='visible', timeout=8000)
                logger.debug('Logged in')
                await self._snap(page, "after-login")

                # 2) Navigate to SMS page – update these steps to match your UI
                await page.click('text=Advanced') #Switch to advanced view
                await self._snap(page, "advanced-form-ready")

                await page.click('a[url="lteSmsInbox.htm"]')
                await self._snap(page, "sms-form-ready1")

                await page.click('a[url="lteSmsNewMsg.htm"]')
                await page.wait_for_selector('textarea[id="inputContent"]', timeout=8000)
                logger.debug('Navigated to SMS sending page')
                await self._snap(page, "sms-form-ready2")

                # 3) Fill recipients & message
                for number in to_numbers:
                    await page.wait_for_selector('textarea[id="inputContent"]', timeout=8000)
                    
                    await page.fill('input[id="toNumber"]', number)
                    await page.fill('textarea[id="inputContent"]', message)
                    await self._snap(page, f"filled-{number}")

                    # 4) Send
                    await page.click('button:has-text("Send")')
                    # Wait for a success toast/alert; change selector text accordingly:
                    # await page.wait_for_selector('text=Message Sent', timeout=10000)
                    time.sleep(10)

                await page.click('a[id=topLogout]')
                await page.click('button:has-text("Yes")')
                await self._snap(page, "logged-out")

        except Exception as e:
            logger.error(f"Error sending sms: {e}")
            raise e

async def _debug_main():
    from .config import load_config
    import logging.config
    config = load_config("config/config.yaml")
    logging.config.dictConfig(config['logging'])

    router = Router(**config["general"])
    await router.send_sms(["+393385221886"], "Hello from script!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(_debug_main())