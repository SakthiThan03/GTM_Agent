# GTM Agent — Ideation to Copy

Week 3 Project 3D. A **LangGraph multi-step AI agent** that retrieves product facts from a brief, optionally researches the web, generates four marketing formats, runs an independent AI critique, revises the copy, and waits for human approval. It never auto-posts or emails.

## Setup (Mac / Windows / Linux)

```bash
cd gtm-agent
python3 -m venv .venv
source .venv/bin/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env      # Windows: copy .env.example .env
```

Edit `.env` and enter your **own** OpenAI-compatible API key and correct model. `OPENAI_BASE_URL` is optional for compatible providers. Optionally set `TAVILY_API_KEY` for live search; without it, the agent works in document-only mode. API usage may incur provider charges.

```bash
streamlit run app.py
```

Open the localhost URL shown in your terminal. Keep the sample fictional product brief selected and click **Generate content suite**. Review the four outputs and critique, approve, and download the Markdown file. You can also upload a real TXT or text-based PDF brief. Scanned PDFs without selectable text are not supported.

## Architecture

`Product TXT/PDF → TF-IDF retrieval → optional Tavily research → LLM drafts (4 formats) → independent LLM critique → LLM revision → Streamlit human approval → local download`

- **Agent goal:** Transform a product brief into a consistent, document-grounded marketing suite.
- **Tools/actions:** Local TF-IDF retrieval (read), Tavily search (read, optional), LLM generation (draft), LLM critique (review), LLM revision (edit in memory), download (human-approved write).
- **State:** LangGraph `GTMState` carries the brief, retrieved passages, research, drafts, critique, revised content, and execution history between nodes. Streamlit session state retains the result and approval while the page session is open.
- **Human-in-the-loop:** A human must inspect and explicitly approve content before download. Nothing is posted, sent, or uploaded.
- **Failure recovery:** Tavily timeout/errors fall back to the brief. Missing API keys, invalid inputs, PDF errors, and LLM failures are shown to the user with a retry path. A failed LLM call does not falsely show a successful result.
- **Safety:** Never invent URLs, prices, partnerships, savings or launch claims; require review. Outputs are suggestions and may still contain mistakes.
- **Success measure:** In three test runs with different briefs, the agent completes all four formats, provides critique, and requests approval; manually check each factual claim against the source.

## How to demo (under 5 minutes)

1. Show the sample fictional product brief and the app interface.
2. Explain the LangGraph nodes and state (see diagram above).
3. Generate content (requires a working model API key and network).
4. Open the agent log and review feedback; show LinkedIn, email, blog, and ad copy.
5. Explain the optional Tavily failure fallback, approval checkbox, and download.
6. Mention what you would improve: evaluation harness, persistent history, better citations, and publishing integrations with permissions.

## Test checklist

- [ ] Valid model key: sample brief generates four formats
- [ ] Each format includes only facts supported by sample brief
- [ ] Review critique is populated and revisions are visible
- [ ] Download is unavailable until approval
- [ ] Missing model key shows a clear error
- [ ] Empty document is rejected
- [ ] No Tavily key runs in document-only mode
- [ ] Invalid Tavily key falls back rather than crashing
- [ ] Real uploaded TXT/PDF can be parsed and used

## Notes

The bundled sample is **fictional**, and the launch date is illustrative. Do not present it as a real commercial launch. No live API calls or successful outputs are bundled; run the application and record your own evidence for submission. Do not commit `.env` or secrets. The handout requires a Google Doc, demo video (≤5 min), and GitHub link.
