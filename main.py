from graph.research_graph import build_graph

graph = build_graph()

result = graph.invoke({
    "query": "Impact of AI on Healthcare"
})

print(result["pdf_path"])