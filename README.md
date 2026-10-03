# 🔎 Multi-Agent Research Assistant

A multi-agent AI research assistant that **searches, extracts, fact-checks, analyzes, and synthesizes** information from the web into a structured research report.

Instead of one big prompt doing everything, the work is split across specialized agents coordinated by an orchestrator, so each step (finding sources, verifying claims, analyzing, writing) is handled by an agent focused on just that job.

---

## ✨ Features

- 🌐 **Web research** – finds relevant sources with DuckDuckGo search
- 📄 **Source extraction** – pulls readable content from each web page
- ✅ **Fact checking** – a dedicated agent verifies claims against the gathered sources
- 📊 **Analysis** – a dedicated agent identifies key insights, trends, and patterns
- 🧠 **AI synthesis** – combines everything into one structured final report
- 🖥️ **Streamlit web UI** with tabs for the report, fact check, analysis, and sources
- 💻 **CLI mode** for quick terminal-based research

---

## 🏗️ Architecture

```
                   USER
                     │
                     ▼
             ┌──────────────┐
             │ ORCHESTRATOR │
             └──────┬───────┘
                    │
      ┌─────────────┼─────────────┐
      ▼             ▼             ▼
┌──────────┐  ┌──────────┐  ┌──────────┐
│ Research │  │   Fact   │  │  Analyst │
│   Agent  │  │  Checker │  │   Agent  │
└────┬─────┘  └────┬─────┘  └────┬─────┘
     │             │              │
     └─────────────┼──────────────┘
                   ▼
            ┌──────────────┐
            │  Synthesizer │
            │    Agent     │
            └──────┬───────┘
                   ▼
            ┌──────────────┐
            │ Final Report │
            └──────────────┘
```

| Agent | Role |
|-------|------|
| **Orchestrator** | Receives the question, coordinates the other agents, and returns the combined result |
| **Research Agent** | Searches the web and extracts content from the top sources |
| **Fact Checker** | Cross-checks claims against the collected source material |
| **Analyst Agent** | Analyzes the findings and surfaces key insights |
| **Synthesizer Agent** | Merges everything into the final structured report |

---

## 📁 Project Structure

```
multi-agent-research-assistant/
├── agents/            # Orchestrator, researcher, fact checker, analyst, synthesizer
├── config/            # Configuration / settings
├── tools/             # Tools used by the agents (web search, page extraction)
├── app.py             # Streamlit web app
├── main.py            # Command-line interface
├── requirements.txt   # Python dependencies
├── .env.example       # Template for environment variables
└── README.md
```

---

## 🛠️ Tech Stack

- **Python 3.10+**
- **Google Gemini** via [`google-genai`](https://pypi.org/project/google-genai/) – LLM for the agents
- **DuckDuckGo Search** (`ddgs`) – web search
- **Requests + BeautifulSoup4 + lxml** – page fetching and content extraction
- **Streamlit** – web interface
- **python-dotenv** – environment variable management

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/annapoorna147/multi-agent-research-assistant.git
cd multi-agent-research-assistant
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up your API key

Copy the example environment file and add your Gemini API key:

```bash
cp .env.example .env
```

Then edit `.env`:

```env
GEMINI_API_KEY=your_api_key_here
```

> Get a free key from [Google AI Studio](https://aistudio.google.com/app/apikey).
> Never commit your real `.env` file — it is already listed in `.gitignore`.

---

## ▶️ Usage

### Web app (Streamlit)

```bash
streamlit run app.py
```

Open the local URL shown in your terminal, type a research question, and click **🚀 Start Research**. Results appear in four tabs:

| Tab | What you get |
|-----|--------------|
| 📄 **Final Report** | The synthesized, structured research report |
| ✅ **Fact Check** | Verification of the key claims |
| 📊 **Analysis** | Insights and patterns from the sources |
| 🔗 **Sources** | The pages used, and whether content was extracted successfully |

### Command line

```bash
python main.py
```

You'll be prompted for a research question, and the result is printed in the terminal.

---

## 💡 Example Questions

- *How is AI being used in semiconductor manufacturing?*
- *What are the latest trends in edge AI for embedded systems?*
- *How do multi-agent LLM systems compare to single-agent systems?*

---

## 🗺️ Roadmap

- [ ] Run the full multi-agent pipeline from the CLI
- [ ] Configurable number of sources from the UI
- [ ] Export reports as PDF / Markdown
- [ ] Citations linked inline in the final report
- [ ] Support for additional LLM providers
- [ ] Caching to avoid repeated searches

---

## ⚠️ Limitations

- Report quality depends on what web search returns and which pages can be scraped.
- Some websites block automated access, so content extraction can fail for certain sources.
- AI-generated fact checks are a helpful aid, not a guarantee — verify important claims yourself.

---

## 🤝 Contributing

Contributions, issues, and feature ideas are welcome! Feel free to open an issue or submit a pull request.

---

## 👩‍💻 Author

**Annapoorna S U**

- GitHub: [@annapoorna147](https://github.com/annapoorna147)
- LinkedIn: [Annapoorna SU](https://www.linkedin.com/in/annapoorna-s-u-789035341/)

---

⭐ If you found this project useful, consider giving it a star!
