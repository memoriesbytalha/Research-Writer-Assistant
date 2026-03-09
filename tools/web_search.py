from tavily import TavilyClient

client = TavilyClient()

def search_web(state):

    query = state["query"]

    results = client.search(query, max_results=5)

    urls = [r["url"] for r in results["results"]]

    state["search_results"] = urls

    return state