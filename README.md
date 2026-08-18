# SafetyWatch Agent

An autonomous drug safety monitoring agent that fetches data from the openFDA API, analyzes it using an LLM, and generates a structured weekly report — with no human intervention required.

Built as a demonstration of an **Agentic Analytics Engineer** workflow in pharmaceutical sciences, integrating LangGraph orchestration, RAG-based molecule retrieval, SQL storage, and MCP-style tool calling.

---

## What It Does

Every run, the agent automatically:

1. **Fetches** the latest drug adverse events, recalls, and label changes from [openFDA](https://open.fda.gov/apis/)
2. **Enriches** each query with relevant internal molecule context via RAG (ChromaDB)
3. **Analyzes** the data using Azure OpenAI (GPT-4o), producing signal strength ratings (HIGH / MEDIUM / LOW)
4. **Routes** HIGH-signal findings through a flagging step (HITL escalation gate)
5. **Stores** results in a local SQLite database for trend tracking
6. **Generates** a structured Markdown weekly report
7. **Notifies** the team via MCP tool (logged to `notifications.log`)

---

## Architecture

```
openFDA API
    ↓
[LangGraph State Machine]
    │
    ├── crawl_node       → fetch adverse events / recalls / labels
    ├── rag_node         → retrieve related internal molecules (ChromaDB)
    ├── analyze_node     → LLM analysis with RAG-enriched context
    ├── signal_check_node → rate overall signal: HIGH / MEDIUM / LOW
    │       ↓
    │   HIGH? → escalate_node (HITL flag)
    │
    ├── store_node       → save to SQLite
    ├── report_node      → write Markdown report
    └── notify_node      → MCP tool: send_safety_alert
```

| Component | Technology |
|-----------|-----------|
| Orchestration | LangGraph |
| LLM | Azure OpenAI (GPT-4o) |
| RAG / Vector Store | ChromaDB |
| Database | SQLite |
| MCP Tools | LangChain Core `@tool` |
| Data Source | openFDA REST API (no key required) |

---

## Prerequisites

- Python 3.10+
- An **Azure OpenAI** resource with a GPT-4o deployment
- Internet access (to reach `api.fda.gov`)

---

## Installation

```bash
# 1. Clone the repo
git clone <your-repo-url>
cd Web_crawler

# 2. (Recommended) Create a virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

---

## Configuration

Create a `.env` file in the project root:

```env
AZURE_OAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OAI_KEY=your-azure-api-key
AZURE_OAI_DEPLOYMENT=your-deployment-name
```

| Variable | Where to find it |
|----------|-----------------|
| `AZURE_OAI_ENDPOINT` | Azure Portal → your OpenAI resource → **Keys and Endpoint** |
| `AZURE_OAI_KEY` | Same page, under **KEY 1** |
| `AZURE_OAI_DEPLOYMENT` | Azure OpenAI Studio → **Deployments** → your model name |

> The openFDA API requires **no API key**. It is free and publicly accessible.

---

## Usage

### Run once

```bash
python main.py
```

### Enable weekly schedule (every Monday 08:00)

In `main.py`, uncomment the schedule block at the bottom:

```python
schedule.every().monday.at("08:00").do(run)
while True:
    schedule.run_pending()
    time.sleep(60)
```

Then run:

```bash
python main.py
```

---

## Output

| Output | Location | Description |
|--------|----------|-------------|
| Weekly report | `reports/safetywatch_YYYYMMDD_HHMMSS.md` | Full analysis with signal ratings |
| Notifications | `notifications.log` | MCP tool alert log |
| Signal history | `safety_watch.db` | SQLite database of all runs |

### Sample report structure

```markdown
# SafetyWatch 周报 | 2026 W34

## 执行摘要
...overall risk assessment and action items...

## 药品不良事件  🔴 HIGH
> Data source: https://api.fda.gov/drug/event.json?...
...LLM analysis with RAG-enriched molecule context...

## 药品召回  🟡 MEDIUM
...

## 药品标签  🟢 LOW
...
```

---

## Project Structure

```
Web_crawler/
├── main.py          # Entry point
├── graph.py         # LangGraph state machine (8 nodes)
├── crawler.py       # openFDA API fetch (adverse events / recalls / labels)
├── summarizer.py    # Azure OpenAI LLM analysis
├── rag.py           # ChromaDB vector store + molecule retrieval
├── storage.py       # SQLite read/write
├── tools.py         # MCP-style tools (send_safety_alert, get_signal_history)
├── reporter.py      # Markdown report generator
├── config.py        # API config + LLM prompts
├── requirements.txt
└── .env             # Your credentials (not committed to git)
```

---

## Customization

**Change monitored data types** — edit `FDA_ENDPOINTS` in `config.py`:
```python
FDA_ENDPOINTS = {
    "药品不良事件": "/drug/event.json",
    "药品召回":    "/drug/enforcement.json",
    "药品标签":    "/drug/label.json",
}
```

**Change lookback window** — edit `FDA_LOOKBACK_DAYS` in `config.py` (default: 7 days).

**Update internal molecule knowledge base** — edit `INTERNAL_MOLECULES` in `rag.py` to reflect real pipeline molecules.

**Enable real notifications** — replace the file-logging logic in `tools.py > send_safety_alert` with SMTP email or a Slack webhook.

---

## Security Note

Never commit your `.env` file. Add it to `.gitignore`:

```bash
echo ".env" >> .gitignore
```
