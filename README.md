# Research Writer Assistant 🤖📄

An AI agent that takes a research topic and produces a fully written, professionally structured research paper as a PDF — triggered from a simple chat message.

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://python.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-1.0+-green.svg)](https://langchain-ai.github.io/langgraph/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-teal.svg)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-ready-blue.svg)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## How it works

You type a topic in the n8n chat interface. The full pipeline runs automatically and returns a PDF link.

```
User types topic
      ↓
n8n chat interface
      ↓
POST /research  (FastAPI)
      ↓
LangGraph pipeline
  Search → Scrape → Outline → Write → Images → PDF
      ↓
PDF saved to ./output/
      ↓
Download link returned to chat
```

---

## Stack

| Layer | Technology |
|---|---|
| LLM | Groq — Llama 3.3 70B |
| Web search | Tavily API |
| Pipeline orchestration | LangGraph |
| API layer | FastAPI + Uvicorn |
| Chat frontend | n8n |
| Containerization | Docker + uv |
| Dependency management | uv (frozen lockfile) |

---

## Quickstart

### Prerequisites

- Python 3.12
- [uv](https://docs.astral.sh/uv/)
- Docker + Docker Compose
- Groq API key
- Tavily API key

### Run locally

```bash
git clone https://github.com/memoriesbytalha/Research-Writer-Assistant.git
cd Research-Writer-Assistant

# Pin Python version
uv python pin 3.12

# Install dependencies from lockfile
uv sync

# Create .env file
cp .env.example .env
# Add your API keys to .env

# Run
uv run main.py
```

FastAPI docs available at `http://localhost:8000/docs`.

### Run with Docker + n8n

```bash
# Create output folder
mkdir output

# Build and start all services
docker compose up --build
```

Services:
- FastAPI → `http://localhost:8000`
- n8n → `http://localhost:5678`

### API usage

```bash
curl -X POST http://localhost:8000/research \
  -H "Content-Type: application/json" \
  -d '{"query": "KServe and vLLM on OpenShift AI"}'
```

Response:
```json
{
  "job_id": "abc123",
  "query": "KServe and vLLM on OpenShift AI",
  "pdf_path": "/app/output/abc123.pdf",
  "message": "Research paper generated successfully"
}
```

Download the PDF:
```
GET http://localhost:8000/research/{job_id}/download
```

---

## n8n workflow

The n8n workflow is 3 nodes:

```
Chat Trigger → HTTP Request → Edit Fields
```

Import `n8n_workflow.json` into your n8n instance to get started immediately.

In the HTTP Request node:
- Method: `POST`
- URL: `http://app:8000/research`
- Body: `{ "query": "{{ $json.chatInput }}" }`

---

## Project structure

```
research-writer-assistant/
├── agents/
│   ├── outline_agent.py      # Research outline generation
│   └── writer_agent.py       # Section-by-section writing
├── tools/
│   ├── web_search.py         # Tavily-powered search
│   ├── scraper.py            # Content extraction
│   └── image_fetcher.py      # Image collection
├── graph/
│   └── research_graph.py     # LangGraph workflow
├── pdf/
│   └── pdf_generator.py      # PDF creation with ReportLab
├── config/
│   └── llm.py                # LLM configuration
├── main.py                   # FastAPI application
├── Dockerfile
├── docker-compose.yml
└── n8n_workflow.json         # Importable n8n workflow
```

---

## Environment variables

```env
GROQ_API_KEY=your_groq_key_here
TAVILY_API_KEY=your_tavily_key_here
SERPAPI_API_KEY=your_serpapi_key_here
```

---

## Roadmap

- [x] LangGraph pipeline (search → scrape → outline → write → PDF)
- [x] FastAPI REST wrapper
- [x] Docker + uv containerization
- [x] n8n chat interface
- [ ] OpenShift AI deployment
- [ ] Job status polling endpoint

---

## License

MIT
