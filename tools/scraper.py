import requests
from trafilatura import extract
from my_decorators.decorators import step_logger

@step_logger
def scrape_content(state):

    contents = []

    for url in state["search_results"]:
        try:
            html = requests.get(url, timeout=10).text
            text = extract(html)
            if text:
                contents.append(text)
            else:
                print(f"[SCRAPER] No content extracted from: {url}")
        except Exception as e:
            print(f"[SCRAPER] Skipping {url} — {e}")

    state["sources_content"] = contents
    return state