from config.llm import llm

def generate_outline(state):

    material = "\n".join(state["sources_content"])

    prompt = f"""
    Create a structured research paper outline.

    Topic:
    {state["query"]}

    Research material:
    {material}
    """

    response = llm.invoke(prompt)

    state["outline"] = response.content

    return state