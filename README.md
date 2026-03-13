# Research Writer Assistant 🤖📝

An intelligent AI-powered research assistant that automates the entire research paper writing process. From topic exploration to final PDF generation, this tool streamlines academic and professional research workflows.

![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)
![LangGraph](https://img.shields.io/badge/LangGraph-1.0+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Features

- **🔍 Intelligent Web Search**: Leverages Tavily API for comprehensive, up-to-date research
- **📄 Content Extraction**: Advanced web scraping with Trafilatura for clean, structured data
- **🗂️ Smart Outlining**: AI-generated research paper outlines tailored to your topic
- **✍️ Automated Writing**: Section-by-section content generation using multiple LLM providers
- **🖼️ Visual Enhancement**: Automatic image fetching and integration
- **📋 PDF Generation**: Professional PDF output with ReportLab
- **🔄 Workflow Orchestration**: Powered by LangGraph for reliable, traceable execution
- **🎯 Multi-LLM Support**: Compatible with OpenAI, Google Gemini, and Groq models

## 🏗️ Architecture

The system follows a structured workflow orchestrated by LangGraph:

```
Search → Scrape → Outline → Write → Images → PDF
```

### Core Components

- **`agents/`**: AI agents for outline generation and content writing
- **`tools/`**: Web search, content scraping, and image fetching utilities
- **`graph/`**: LangGraph workflow definition and state management
- **`pdf/`**: PDF generation and formatting
- **`config/`**: LLM configuration and API management

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- **Groq API key** (currently used LLM provider)
- Tavily API key for web search
- Alternative: OpenAI or Google AI API keys (optional)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/research-writer-assistant.git
   cd research-writer-assistant
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   # On Windows
   .venv\Scripts\activate
   # On macOS/Linux
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   Create a `.env` file in the root directory:
   ```env
   # Primary LLM provider (currently ChatGroq)
   GROQ_API_KEY=your_groq_key_here

   # Alternative LLM providers

   # Required for web search
   TAVILY_API_KEY=your_tavily_key_here
   SERPAPI_API_KEY=your_serpapi_key_here
   ```

### Usage

1. **Run the research assistant**
   ```python
   python main.py
   ```

2. **Customize your research topic**

   Edit the query in `main.py`:
   ```python
   result = graph.invoke({
       "query": "Your Research Topic Here"
   })
   ```

3. **View results**

   The system will generate:
   - Research outline
   - Written sections
   - Integrated images
   - Final PDF document

## 📋 Configuration

### LLM Configuration

The system supports multiple LLM providers. Currently configured to use **ChatGroq** with Llama 3.3 70B. Configure your preferred model in `config/llm.py`:

```python
# Current configuration (ChatGroq)
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY")
)

# Alternative configurations
# llm = ChatOpenAI(model="gpt-4", temperature=0.7)
# llm = ChatGoogleGenerativeAI(model="gemini-pro")
```

### Workflow Customization

Modify the research graph in `graph/research_graph.py` to customize the workflow steps and their connections.

## 🛠️ Development

### Project Structure

```
research-writer-assistant/
├── agents/                 # AI agents
│   ├── outline_agent.py   # Research outline generation
│   └── writer_agent.py    # Content writing
├── tools/                 # Utility tools
│   ├── web_search.py      # Tavily-powered search
│   ├── scraper.py         # Content extraction
│   └── image_fetcher.py   # Image collection
├── graph/                 # Workflow orchestration
│   └── research_graph.py  # LangGraph definition
├── pdf/                   # Document generation
│   └── pdf_generator.py   # PDF creation
├── config/                # Configuration
│   └── llm.py            # LLM setup
└── my_decorators/         # Logging utilities
    └── decorators.py      # Step logging
```

### Adding New Features

1. **Create a new tool** in the `tools/` directory
2. **Add an agent** in the `agents/` directory if needed
3. **Update the graph** in `research_graph.py` to include new steps
4. **Test the workflow** by running `main.py`

## 🔧 Dependencies

### Core Dependencies

- **LangChain**: LLM orchestration and chaining
- **LangGraph**: Workflow state management
- **Tavily**: Web search API
- **Trafilatura**: Web content extraction
- **ReportLab**: PDF generation
- **Requests**: HTTP client

### LLM Providers

- **OpenAI**: GPT models
- **Google AI**: Gemini models
- **Groq**: Fast inference models

## 📊 Example Output

The assistant generates a complete research paper including:

- **Executive Summary**
- **Introduction**
- **Literature Review**
- **Methodology**
- **Results & Analysis**
- **Conclusion**
- **References**

All content is properly formatted and ready for academic submission.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **LangChain** for the powerful LLM orchestration framework
- **LangGraph** for state-of-the-art workflow management
- **Tavily** for reliable web search capabilities
- **Trafilatura** for robust content extraction

## 📞 Support

For questions, issues, or contributions:

- Open an issue on GitHub
- Check the documentation in this README
- Review the code comments for implementation details

---

**Made with ❤️ for researchers and writers everywhere**