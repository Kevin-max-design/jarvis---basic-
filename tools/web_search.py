"""
Web Search Tool — The Eyes of JARVIS
Uses requests + BeautifulSoup to search DuckDuckGo HTML (no API keys, no blocking).
Uses Playwright only for browsing/reading full pages.
"""
import asyncio
import re
import urllib.parse
import warnings

import requests
from bs4 import BeautifulSoup

warnings.filterwarnings("ignore", category=RuntimeWarning)

# Try Playwright for page browsing (optional)
try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}


class WebSearchTool:
    def __init__(self):
        self.name = "web_search"

    def search(self, query, max_results=5):
        """Search the web using DuckDuckGo HTML (fast, free, no API)."""
        print(f"  [Web] Searching for: {query}")

        # Method 1: DuckDuckGo HTML lite (most reliable — no JS needed)
        results = self._search_ddg_html(query, max_results)
        if results:
            return self._format_results(results)

        # Method 2: DuckDuckGo via requests with different params
        results = self._search_ddg_alt(query, max_results)
        if results:
            return self._format_results(results)

        return "I was unable to find results for that query, Sir. Please try rephrasing."

    def _search_ddg_html(self, query, max_results=5):
        """Scrape DuckDuckGo HTML-only search (no JS required)."""
        try:
            encoded = urllib.parse.quote_plus(query)
            url = f"https://html.duckduckgo.com/html/?q={encoded}"

            resp = requests.get(url, headers=HEADERS, timeout=10)
            resp.raise_for_status()

            soup = BeautifulSoup(resp.text, "html.parser")
            results = []

            for result in soup.select(".result"):
                title_el = result.select_one(".result__title a, .result__a")
                snippet_el = result.select_one(".result__snippet")

                title = title_el.get_text(strip=True) if title_el else ""
                snippet = snippet_el.get_text(strip=True) if snippet_el else ""

                # Extract URL
                link = ""
                if title_el and title_el.has_attr("href"):
                    raw_href = title_el["href"]
                    # DDG wraps URLs — extract the actual URL
                    if "uddg=" in raw_href:
                        link = urllib.parse.unquote(raw_href.split("uddg=")[1].split("&")[0])
                    else:
                        link = raw_href

                if title:
                    results.append({
                        "title": title,
                        "snippet": snippet,
                        "url": link,
                    })
                    if len(results) >= max_results:
                        break

            return results

        except Exception as e:
            print(f"  [Web] DDG HTML error: {e}")
            return []

    def _search_ddg_alt(self, query, max_results=5):
        """Alternative DuckDuckGo search using the lite version."""
        try:
            encoded = urllib.parse.quote_plus(query)
            url = f"https://lite.duckduckgo.com/lite/?q={encoded}"

            resp = requests.get(url, headers=HEADERS, timeout=10)
            resp.raise_for_status()

            soup = BeautifulSoup(resp.text, "html.parser")
            results = []

            # Lite version uses tables
            for link in soup.select("a.result-link"):
                title = link.get_text(strip=True)
                href = link.get("href", "")

                # Find the next snippet
                snippet_td = link.find_parent("tr")
                snippet = ""
                if snippet_td:
                    next_tr = snippet_td.find_next_sibling("tr")
                    if next_tr:
                        snippet = next_tr.get_text(strip=True)

                if title and href:
                    results.append({
                        "title": title,
                        "snippet": snippet,
                        "url": href,
                    })
                    if len(results) >= max_results:
                        break

            return results

        except Exception as e:
            print(f"  [Web] DDG Lite error: {e}")
            return []

    def browse(self, url):
        """Visit a URL and extract its main text content."""
        print(f"  [Web] Browsing: {url}")

        if PLAYWRIGHT_AVAILABLE:
            try:
                return asyncio.run(self._browse_playwright(url))
            except Exception as e:
                print(f"  [Web] Playwright browse failed: {e}, falling back to requests")

        # Fallback: use requests (won't render JS but works for most pages)
        return self._browse_requests(url)

    async def _browse_playwright(self, url):
        """Browse page with Playwright (handles JS-heavy sites)."""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(user_agent=HEADERS["User-Agent"])
            page = await context.new_page()

            await page.goto(url, timeout=15000)
            await page.wait_for_load_state("domcontentloaded")

            content = await page.content()
            title = await page.title()
            await browser.close()

        return self._extract_text(content, title)

    def _browse_requests(self, url):
        """Browse page with requests (lightweight, no JS)."""
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            resp.raise_for_status()
            title = ""
            soup = BeautifulSoup(resp.text, "html.parser")
            title_tag = soup.find("title")
            if title_tag:
                title = title_tag.get_text(strip=True)
            return self._extract_text(resp.text, title)
        except Exception as e:
            return f"Error browsing page: {e}"

    def _extract_text(self, html, title=""):
        """Clean HTML content into readable text."""
        soup = BeautifulSoup(html, "html.parser")

        for tag in soup(["script", "style", "nav", "footer", "header", "iframe", "noscript", "aside"]):
            tag.decompose()

        text = soup.get_text(separator=" ")
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        clean_text = "\n".join(chunk for chunk in chunks if chunk)

        # Limit to 4000 chars for the brain
        if len(clean_text) > 4000:
            clean_text = clean_text[:4000] + "..."

        return f"Title: {title}\n\nContent:\n{clean_text}"

    def _format_results(self, results):
        """Format search results into a readable summary."""
        if not results:
            return "No results found."

        summary = ""
        for i, r in enumerate(results, 1):
            title = r.get("title", "Untitled")
            snippet = r.get("snippet", "No description available.")
            summary += f"\n{i}. {title}\n   {snippet}\n"

        return summary.strip()
