from config.llm import llm
from my_decorators.decorators import step_logger

@step_logger
def write_sections(state):
    outline_content = state["outline"]

    if isinstance(outline_content, list):
        outline_text = "\n".join(item.get("text", str(item)) if isinstance(item, dict) else str(item) for item in outline_content)
    else:
        outline_text = str(outline_content)

    # Single LLM call instead of one per section
    prompt = f"""
    Write a detailed academic research paper based on this outline.

    Topic: {state['query']}
    Outline:
    {outline_text[:4000]}

    Write each section fully with proper academic depth.
    """
    result = llm.invoke(prompt)
    content = result.content if isinstance(result.content, str) else str(result.content)

    state["sections"] = [content]
    return state