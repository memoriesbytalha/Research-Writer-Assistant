from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from decorator.decorators import step_logger
@step_logger
def generate_pdf(state):

    styles = getSampleStyleSheet()

    elements = []

    elements.append(Paragraph(state["query"], styles["Title"]))

    for section in state["sections"]:
        elements.append(Paragraph(section, styles["BodyText"]))

    pdf_path = "research_paper.pdf"

    doc = SimpleDocTemplate(pdf_path)

    doc.build(elements)

    state["pdf_path"] = pdf_path

    return state