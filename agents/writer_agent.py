from config.llm import llm

def write_sections(state):

    sections = []

    outline_parts = state["outline"].split("\n")

    for section in outline_parts:

        prompt = f"""
        Write a detailed academic section.

        Topic: {state["query"]}

        Section:
        {section}
        """

        result = llm.invoke(prompt)

        sections.append(result.content)

    state["sections"] = sections

    return state