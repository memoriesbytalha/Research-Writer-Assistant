from langgraph.graph import StateGraph
from typing import TypedDict, List

from tools.web_search import search_web
from tools.scraper import scrape_content
from agents.outline_agent import generate_outline
from agents.writer_agent import write_sections
from tools.image_fetcher import fetch_images
from pdf.pdf_generator import generate_pdf


class ResearchState(TypedDict):

    query: str
    search_results: List[str]
    sources_content: List[str]
    outline: str
    sections: List[str]
    images: List[str]
    pdf_path: str


def build_graph():

    builder = StateGraph(ResearchState)

    builder.add_node("search", search_web)
    builder.add_node("scrape", scrape_content)
    builder.add_node("outline", generate_outline)
    builder.add_node("write", write_sections)
    builder.add_node("images", fetch_images)
    builder.add_node("pdf", generate_pdf)

    builder.set_entry_point("search")

    builder.add_edge("search", "scrape")
    builder.add_edge("scrape", "outline")
    builder.add_edge("outline", "write")
    builder.add_edge("write", "images")
    builder.add_edge("images", "pdf")

    return builder.compile()