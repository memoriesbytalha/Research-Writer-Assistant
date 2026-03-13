"""
tools/image_fetcher.py
──────────────────────
Fetch image URLs via SerpAPI (Google Images) and validate each one
is actually downloadable before storing in state.
Images are stored as URLs; the PDF generator handles downloading them.
"""

import os
import requests
from dotenv import load_dotenv
from my_decorators.decorators import step_logger

load_dotenv()

# Support both env-var spellings
SERPAPI_KEY = (
    os.environ.get("SERPAPI_API_KEY")
    or os.environ.get("serpi_account")
    or ""
)

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; ResearchBot/1.0)"}


def _url_is_reachable(url: str, timeout: int = 6) -> bool:
    """Quick HEAD/GET check to confirm the image URL actually loads."""
    try:
        r = requests.head(url, timeout=timeout, headers=HEADERS, allow_redirects=True)
        if r.status_code < 400 and "image" in r.headers.get("Content-Type", ""):
            return True
        # Some servers reject HEAD; fall back to a tiny GET
        r = requests.get(url, timeout=timeout, headers=HEADERS, stream=True)
        content_type = r.headers.get("Content-Type", "")
        return r.status_code < 400 and "image" in content_type
    except Exception:
        return False


@step_logger
def fetch_images(state: dict, limit: int = 3) -> dict:
    """
    Fetch up to `limit` image URLs for the research query.

    Strategy:
      1. Call SerpAPI Google Images.
      2. Validate each candidate URL is reachable & is an image.
      3. Stop once we have `limit` good URLs.
    Falls back to an empty list on any error so the pipeline never crashes.
    """
    query = state.get("query", "")
    image_urls: list[str] = []

    if not SERPAPI_KEY:
        print("[Image Fetcher] ⚠  No SerpAPI key found — skipping image fetch.")
        state["images"] = image_urls
        return state

    try:
        resp = requests.get(
            "https://serpapi.com/search",
            params={
                "engine": "google_images",
                "q": query,
                "api_key": SERPAPI_KEY,
                "num": limit * 4,       # fetch extras in case some fail validation
                "safe": "active",
                "ijn": "0",
            },
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()

        candidates = [
            item.get("original", "")
            for item in data.get("images_results", [])
            if item.get("original")
        ]

        for url in candidates:
            if len(image_urls) >= limit:
                break
            print(f"[Image Fetcher] Checking: {url[:70]}…")
            if _url_is_reachable(url):
                image_urls.append(url)
                print(f"[Image Fetcher] ✓ Valid ({len(image_urls)}/{limit})")
            else:
                print("[Image Fetcher] ✗ Skipped (unreachable or non-image)")

    except Exception as e:
        print(f"[Image Fetcher] Error: {e}")

    if not image_urls:
        print("[Image Fetcher] No valid images found — PDF will be text-only.")

    state["images"] = image_urls
    return state