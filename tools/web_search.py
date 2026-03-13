from tavily import TavilyClient
from dotenv import load_dotenv
load_dotenv()
import os
from my_decorators.decorators import step_logger

client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

@step_logger
def search_web(state):
    query = state["query"]
    try:
        results = client.search(query, max_results=5)
        urls = [r["url"] for r in results["results"]]
    except Exception as e:
        print(f"[SEARCH_WEB] Search failed: {e}")
        urls = []

    state["search_results"] = urls
    return state