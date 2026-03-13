"""
my_decorators/decorators.py
───────────────────────────
A clean step logger that only reports keys that were NEW or CHANGED
after a node runs — so later nodes don't re-print everything upstream.
"""

import time
from functools import wraps
from typing import Any, Dict


# Maps state-key → human-readable label and how to summarise its value
_KEY_SUMMARY = {
    "search_results":  ("Search results",   lambda v: f"{len(v)} URLs"),
    "sources_content": ("Scraped sources",  lambda v: f"{len(v)} pages"),
    "outline":         ("Outline",          lambda v: f"{len(str(v).splitlines())} lines"),
    "sections":        ("Sections written", lambda v: f"{len(v)} section(s)"),
    "images":          ("Images fetched",   lambda v: f"{len(v)} image(s)"),
    "pdf_path":        ("PDF saved",        lambda v: str(v)),
}


def step_logger(func):
    """
    Decorator that logs the start, timing, and *new* state changes
    produced by each LangGraph node function.
    """
    @wraps(func)
    def wrapper(state: Dict[str, Any], *args, **kwargs):
        step_name = func.__name__.upper()
        separator = "─" * 50

        print(f"\n{separator}")
        print(f"  ▶  {step_name}")
        print(separator)

        # Snapshot keys & values before the call
        before = {k: v for k, v in state.items()}

        start = time.time()
        result = func(state, *args, **kwargs)
        elapsed = time.time() - start

        # Report only keys that are new or whose value changed
        for key, (label, summarise) in _KEY_SUMMARY.items():
            if key not in result:
                continue
            new_val = result[key]
            old_val = before.get(key)

            # Consider changed if key is new, or length/value differs
            is_new     = key not in before
            try:
                is_changed = old_val != new_val
            except Exception:
                is_changed = True

            if is_new or is_changed:
                try:
                    summary = summarise(new_val)
                except Exception:
                    summary = str(new_val)
                print(f"    ✔  {label}: {summary}")

        print(f"    ⏱  Completed in {elapsed:.2f}s")
        print(separator)

        return result

    return wrapper