from config.llm import llm
from my_decorators.decorators import step_logger

@step_logger
def generate_outline(state):

    material = "\n".join(item for item in state["sources_content"] if item)

    # Truncate to ~8000 chars to stay within Groq's token limit
    if len(material) > 8000:
        material = material[:8000] + "\n...[truncated]"

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