import time
from functools import wraps
from typing import Any, Dict

def step_logger(func):
    """
    Decorator to log the start, end, and key information of a node function in the research pipeline.
    """
    @wraps(func)
    def wrapper(state: Dict[str, Any], *args, **kwargs):
        step_name = func.__name__.upper()
        print(f"\n[{step_name}] Starting...")

        start_time = time.time()
        result = func(state, *args, **kwargs)
        end_time = time.time()

        # Log key info depending on what the state contains
        if "search_results" in result:
            print(f"[{step_name}] Search results: {len(result['search_results'])} items")
        if "sources_content" in result:
            print(f"[{step_name}] Scraped content: {len(result['sources_content'])} sources")
        if "outline" in result:
            print(f"[{step_name}] Outline generated: {len(result['outline'].splitlines())} lines")
        if "sections" in result:
            print(f"[{step_name}] Sections written: {len(result['sections'])}")
        if "images" in result:
            print(f"[{step_name}] Images fetched: {len(result['images'])}")
        if "pdf_path" in result:
            print(f"[{step_name}] PDF generated at: {result['pdf_path']}")

        print(f"[{step_name}] Completed in {end_time - start_time:.2f}s\n")
        return result

    return wrapper