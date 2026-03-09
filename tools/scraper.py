import requests
from trafilatura import extract
from decorator.decorators import step_logger
@step_logger
def scrape_content(state):

    contents = []

    for url in state["search_results"]:
        html = requests.get(url).text
        text = extract(html)

        contents.append(text)
    state["sources_content"] = contents

    return state