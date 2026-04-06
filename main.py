# from graph.research_graph import build_graph
# from IPython.display import Image
# from dotenv import load_dotenv
# load_dotenv()

# graph = build_graph()
# # print(graph.get_graph())
# with open("Sequence.png", "wb") as f:
#     f.write(graph.get_graph().draw_mermaid_png())
# result = graph.invoke({
#     "query": "kserve and Vllm in openshift AI"
# })

# print(result["pdf_path"])

from dotenv import load_dotenv
load_dotenv()
import shutil
import os
import uuid
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from graph.research_graph import build_graph

app = FastAPI(
    title="Research Writer Assistant",
    description="AI-powered research paper generator",
    version="1.0.0"
)

graph = build_graph()
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "./output")
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ── Request / Response schemas ────────────────────────────────────

class ResearchRequest(BaseModel):
    query: str
    job_id: str | None = None     # optional, auto-generated if not provided


class ResearchResponse(BaseModel):
    job_id: str
    query: str
    pdf_path: str
    message: str


# ── Routes ────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/research", response_model=ResearchResponse)
def run_research(request: ResearchRequest):
    """
    Run the full research pipeline synchronously.
    n8n calls this via HTTP Request node and waits for the PDF path back.
    """
    job_id = request.job_id or str(uuid.uuid4())

    try:
        result = graph.invoke({"query": request.query})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline failed: {str(e)}")

    # Locate PDF from graph result
    pdf_source = result.get("pdf_path") or result.get("output_pdf")

    if not pdf_source or not os.path.exists(pdf_source):
        # Fallback: find most recently created PDF in cwd
        pdfs = sorted(
            [f for f in os.listdir(".") if f.endswith(".pdf")],
            key=lambda f: os.path.getmtime(f),
            reverse=True
        )
        if not pdfs:
            raise HTTPException(status_code=500, detail="Pipeline ran but no PDF was generated")
        pdf_source = pdfs[0]

    # Move PDF to output dir with job_id name
    dest = os.path.join(OUTPUT_DIR, f"{job_id}.pdf")
    shutil.move(pdf_source, dest)

    return ResearchResponse(
        job_id=job_id,
        query=request.query,
        pdf_path=dest,
        message="Research paper generated successfully"
    )


@app.get("/research/{job_id}/download")
def download_pdf(job_id: str):
    pdf_path = os.path.join(OUTPUT_DIR, f"{job_id}.pdf")
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="PDF not found")
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=f"research_{job_id}.pdf",
        headers={"Content-Disposition": "inline"}  # ← shows in browser, not download
    )


@app.get("/research/list")
def list_jobs():
    """List all generated PDFs."""
    files = [f.replace(".pdf", "") for f in os.listdir(OUTPUT_DIR) if f.endswith(".pdf")]
    return {"jobs": files}


# ── Entry point ───────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)