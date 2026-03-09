from config.llm import llm
from decorator.decorators import step_logger
@step_logger
def write_sections(state):
    sections = []

    outline_content = state["outline"]

    # Convert list-of-dicts to a single string
    if isinstance(outline_content, list):
        outline_text = ""
        for item in outline_content:
            if isinstance(item, dict) and "text" in item:
                outline_text += item["text"] + "\n"
            else:
                outline_text += str(item) + "\n"
    else:
        outline_text = str(outline_content)

    # Now split by lines
    outline_parts = outline_text.split("\n")

    for section in outline_parts:
        if not section.strip():
            continue  # skip empty lines
        prompt = f"""
        Write a detailed academic section.

        Topic: {state['query']}
        Section: {section}
        """
        result = llm.invoke(prompt)
        # store result
        sections.append(result.content if isinstance(result.content, str) else str(result.content))

    state["sections"] = sections
    return state