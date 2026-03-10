from graph.research_graph import build_graph
from IPython.display import Image

graph = build_graph()
# print(graph.get_graph())
with open("Sequence.png", "wb") as f:
    f.write(graph.get_graph().draw_mermaid_png())
result = graph.invoke({
    "query": "Impact of AI on Healthcare"
})

print(result["pdf_path"])