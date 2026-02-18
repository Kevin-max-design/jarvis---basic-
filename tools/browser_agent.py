"""
Browser Agent — Real-time browser automation for JARVIS.
Opens visible browser windows and performs actions like a human would.
Uses macOS `open` for quick URL opens + Playwright (non-headless) for complex tasks.
"""
import subprocess
import webbrowser
import asyncio
import urllib.parse
import time

try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


# ─── Common website shortcuts ───────────────────────────────────
WEBSITE_SHORTCUTS = {
    "youtube": "https://www.youtube.com",
    "google": "https://www.google.com",
    "gmail": "https://mail.google.com",
    "github": "https://github.com",
    "twitter": "https://twitter.com",
    "x": "https://x.com",
    "reddit": "https://www.reddit.com",
    "instagram": "https://www.instagram.com",
    "facebook": "https://www.facebook.com",
    "linkedin": "https://www.linkedin.com",
    "netflix": "https://www.netflix.com",
    "spotify": "https://open.spotify.com",
    "amazon": "https://www.amazon.com",
    "flipkart": "https://www.flipkart.com",
    "stack overflow": "https://stackoverflow.com",
    "stackoverflow": "https://stackoverflow.com",
    "chatgpt": "https://chat.openai.com",
    "whatsapp": "https://web.whatsapp.com",
    "telegram": "https://web.telegram.org",
    "maps": "https://maps.google.com",
    "google maps": "https://maps.google.com",
    "drive": "https://drive.google.com",
    "google drive": "https://drive.google.com",
    "docs": "https://docs.google.com",
    "sheets": "https://sheets.google.com",
    "wikipedia": "https://www.wikipedia.org",
    "notion": "https://www.notion.so",
    "figma": "https://www.figma.com",
}

# ─── Search URL templates ────────────────────────────────────────
SEARCH_URLS = {
    "youtube": "https://www.youtube.com/results?search_query={query}",
    "google": "https://www.google.com/search?q={query}",
    "amazon": "https://www.amazon.com/s?k={query}",
    "flipkart": "https://www.flipkart.com/search?q={query}",
    "github": "https://github.com/search?q={query}",
    "reddit": "https://www.reddit.com/search/?q={query}",
    "wikipedia": "https://en.wikipedia.org/wiki/Special:Search?search={query}",
    "stack overflow": "https://stackoverflow.com/search?q={query}",
    "maps": "https://www.google.com/maps/search/{query}",
}


class BrowserAgent:
    def __init__(self):
        self.name = "browser_agent"
        self.playwright_browser = None

    def open_website(self, site_name):
        """Open a website in the user's default browser."""
        site_lower = site_name.lower().strip()

        # Check shortcuts first
        url = WEBSITE_SHORTCUTS.get(site_lower)

        if not url:
            # Check if it's already a URL
            if site_lower.startswith("http://") or site_lower.startswith("https://"):
                url = site_name
            elif "." in site_lower:
                # Looks like a domain
                url = f"https://{site_name}"
            else:
                # Try as a .com
                url = f"https://www.{site_lower}.com"

        try:
            subprocess.run(["open", url], check=True)
            return f"Opening {site_name} in your browser, Sir."
        except Exception as e:
            return f"Error opening {site_name}: {e}"

    def search_on_site(self, site, query):
        """Search on a specific website (YouTube, Google, Amazon, etc.)."""
        site_lower = site.lower().strip()
        encoded_query = urllib.parse.quote_plus(query)

        template = SEARCH_URLS.get(site_lower)
        if template:
            url = template.format(query=encoded_query)
        else:
            # Default: Google search with site filter
            url = f"https://www.google.com/search?q={encoded_query}+site:{site_lower}"

        try:
            subprocess.run(["open", url], check=True)
            return f"Searching for '{query}' on {site}, Sir."
        except Exception as e:
            return f"Error searching: {e}"

    def play_on_youtube(self, query):
        """Search and open YouTube with the query."""
        encoded = urllib.parse.quote_plus(query)
        url = f"https://www.youtube.com/results?search_query={encoded}"
        try:
            subprocess.run(["open", url], check=True)
            return f"Searching YouTube for '{query}', Sir."
        except Exception as e:
            return f"Error opening YouTube: {e}"

    def open_google_maps(self, location):
        """Open Google Maps with a specific location."""
        encoded = urllib.parse.quote_plus(location)
        url = f"https://www.google.com/maps/search/{encoded}"
        try:
            subprocess.run(["open", url], check=True)
            return f"Opening Google Maps for '{location}', Sir."
        except Exception as e:
            return f"Error opening maps: {e}"

    def compose_email(self, to="", subject="", body=""):
        """Open Gmail compose window."""
        params = []
        if to:
            params.append(f"to={urllib.parse.quote(to)}")
        if subject:
            params.append(f"su={urllib.parse.quote(subject)}")
        if body:
            params.append(f"body={urllib.parse.quote(body)}")

        query = "&".join(params)
        url = f"https://mail.google.com/mail/?view=cm&{query}"
        try:
            subprocess.run(["open", url], check=True)
            return "Opening Gmail compose window, Sir."
        except Exception as e:
            return f"Error opening email: {e}"

    async def automate_browser(self, instructions):
        """
        Advanced: Perform complex browser automation using Playwright (visible browser).
        This opens a REAL browser window that the user can see.
        """
        if not PLAYWRIGHT_AVAILABLE:
            return "Playwright is not installed. Cannot perform browser automation."

        try:
            async with async_playwright() as p:
                # Launch VISIBLE browser (headless=False)
                browser = await p.chromium.launch(
                    headless=False,
                    args=["--start-maximized"]
                )
                context = await browser.new_context(no_viewport=True)
                page = await context.new_page()

                # Execute instructions (basic command parser)
                result = await self._execute_instructions(page, instructions)

                # Keep browser open for user to interact
                # Don't close — user will close it manually
                return result

        except Exception as e:
            return f"Browser automation error: {e}"

    async def _execute_instructions(self, page, instructions):
        """Parse and execute browser instructions."""
        steps = instructions if isinstance(instructions, list) else [instructions]
        results = []

        for step in steps:
            step_lower = step.lower()

            if step_lower.startswith("go to ") or step_lower.startswith("navigate to "):
                url = step.split(" to ", 1)[1].strip()
                if not url.startswith("http"):
                    url = f"https://{url}"
                await page.goto(url, timeout=15000)
                results.append(f"Navigated to {url}")

            elif step_lower.startswith("type "):
                # "type hello in search box"
                parts = step.split(" in ", 1)
                text = parts[0].replace("type ", "", 1).strip()
                if len(parts) > 1:
                    selector = parts[1].strip()
                    await page.fill(f'[placeholder*="{selector}" i], [name*="{selector}" i], [aria-label*="{selector}" i]', text)
                else:
                    await page.keyboard.type(text)
                results.append(f"Typed: {text}")

            elif step_lower.startswith("click "):
                target = step.replace("click ", "", 1).strip()
                await page.click(f'text="{target}"', timeout=5000)
                results.append(f"Clicked: {target}")

            elif step_lower == "press enter":
                await page.keyboard.press("Enter")
                results.append("Pressed Enter")

            elif step_lower.startswith("wait"):
                await asyncio.sleep(2)
                results.append("Waited 2 seconds")

            elif step_lower.startswith("screenshot"):
                await page.screenshot(path="screenshot.png")
                results.append("Screenshot saved")

        return "Actions performed: " + ", ".join(results)
