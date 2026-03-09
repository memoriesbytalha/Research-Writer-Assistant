import requests
from trafilatura import extract

def scrape_content(state):

    contents = []

    for url in state["search_results"]:
        html = requests.get(url).text
        text = extract(html)

        contents.append(text)

    state["sources_content"] = contents

    return state