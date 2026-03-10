# tools/image_fetcher.py
import os
import requests
from dotenv import load_dotenv
from my_decorators.decorators import step_logger
load_dotenv()

SERPAPI_KEY = os.environ.get("serpi_account")

@step_logger
def fetch_images(state, limit=3):
    """
    Fetch images related to the research query and update the state.
    
    Args:
        state (dict): The LangGraph state dictionary.
        limit (int): Number of images to fetch.
        
    Returns:
        state (dict): Updated state with image URLs in state['images'].
    """

    query = state["query"]
    image_urls = []

    try:
        response = requests.get(
            "https://serpapi.com/search",
            params={
                "engine": "google_images",
                "q": query,
                "api_key": SERPAPI_KEY,
            },
            timeout=10
        )
        data = response.json()

        if "images_results" in data:
            for item in data["images_results"][:limit]:
                image_urls.append(item.get("original"))

    except Exception as e:
        print(f"[Image Fetcher] Error fetching images: {e}")

    # Save in the LangGraph state
    state["images"] = image_urls
    return state