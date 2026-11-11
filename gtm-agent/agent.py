"""GTM agent: retrieval, research, content drafting, critique, revision and approval.

The LangGraph workflow uses explicit state and tool calls; human approval happens
in the Streamlit UI before content is marked approved. No content is auto-posted.
"""
import os
import re
import time
from typing import TypedDict

import requests
from langgraph.graph import StateGraph, END
from openai import OpenAI
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

FORMATS = ["LinkedIn post", "Promotional email", "Short blog draft", "Ad copy variations"]


class GTMState(TypedDict, total=False):
    product: str
    audience: str
    tone: str
    source_text: str
    retrieved_context: str
    research: str
    research_status: str
    drafts: dict
    critique: str
    final_content: dict
    errors: list
    step_history: list


def chunk_text(text: str, size: int = 850, overlap: int = 120) -> list[str]:
    if not text.strip():
        return []
    chunks = []
    pos = 0
    while pos < len(text):
        chunks.append(text[pos:pos + size])
        if pos + size >= len(text):
            break
        pos += size - overlap
    return chunks


def retrieve(text: str, query: str, k: int = 4) -> str:
    """Local document retrieval; no cloud embedding account required."""
    chunks = chunk_text(text)
    if not chunks:
        raise ValueError("The product document is empty.")
    if len(chunks) == 1:
        return chunks[0]
    vec = TfidfVectorizer(stop_words="english")
    matrix = vec.fit_transform(chunks + [query])
    scores = cosine_similarity(matrix[-1], matrix[:-1]).ravel()
    selected = sorted(scores.argsort()[-k:].tolist(), key=lambda i: -scores[i])
    return "\n\n".join(f"[Source excerpt {i+1}] {chunks[i]}" for i in selected)


def llm(prompt: str) -> str:
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is missing. Add it to .env or your environment.")
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"], base_url=os.getenv("OPENAI_BASE_URL") or None, timeout=40.0, max_retries=1)
    response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        messages=[{"role": "system", "content": "You are a careful marketing assistant. Never fabricate facts, links, prices, reviews, endorsements, or launch dates. If unverified, label as unverified or omit. Follow source documents. Do not publish anything."}, {"role": "user", "content": prompt}],
        temperature=0.5,
    )
    return response.choices[0].message.content or ""


def research_tool(product: str) -> tuple[str, str]:
    """Optional Tavily search; absence/failure degrades gracefully to document-only mode."""
    key = os.getenv("TAVILY_API_KEY")
    if not key:
        return "No external research performed. Use the uploaded document only.", "document-only"
    try:
        res = requests.post("https://api.tavily.com/search", json={"api_key": key, "query": f"{product} product features target audience", "search_depth": "basic", "max_results": 3}, timeout=12)
        res.raise_for_status()
        results = res.json().get("results", [])
        if not results:
            return "No web results found. Use the uploaded document only.", "no-results"
        lines = [f"{r.get('title','Untitled')}: {r.get('content','')} (source: {r.get('url','unknown')})" for r in results]
        return "\n".join(lines)[:4500], "web-research"
    except (requests.RequestException, ValueError) as exc:
        return f"Web research failed ({type(exc).__name__}). Use the uploaded document only.", "research-failed"


def retrieval_node(s: GTMState) -> dict:
    query = f"{s['product']} features audience launch dates benefits messaging limitations"
    return {"retrieved_context": retrieve(s["source_text"], query), "step_history": ["Retrieved relevant document excerpts"]}


def research_node(s: GTMState) -> dict:
    research, status = research_tool(s["product"])
    return {"research": research, "research_status": status, "step_history": s["step_history"] + [f"Research tool: {status}"]}


def draft_node(s: GTMState) -> dict:
    drafts = {}
    for fmt in FORMATS:
        specific = {
            "LinkedIn post": "Write 100–160 words, a strong opening, and a CTA with 2–3 relevant hashtags.",
            "Promotional email": "Include subject line, preview text, greeting, 100–170 word body, and CTA.",
            "Short blog draft": "Write a title and 250–350 words with 2–3 section headings.",
            "Ad copy variations": "Provide 3 distinct ads, each with headline, 1–2 sentence body, and CTA.",
        }[fmt]
        drafts[fmt] = llm(f"Create {fmt} for {s['product']}. {specific}\nAudience: {s['audience']}\nTone: {s['tone']}\nVerified document excerpts:\n{s['retrieved_context']}\nSupplemental web research (unverified; cross-check against source):\n{s['research']}\nNever invent a working URL. Use [INSERT REAL URL] if needed. Keep all facts grounded in the document.")
    return {"drafts": drafts, "step_history": s["step_history"] + ["Generated four content formats"]}


def review_node(s: GTMState) -> dict:
    content = "\n\n".join(f"{k}:\n{v}" for k, v in s["drafts"].items())
    critique = llm(f"Act as a separate critical marketing review agent. Check factual accuracy against the SOURCE, tone, audience fit, consistency, unsupported promises, invented URLs and missing disclaimers. Return a concise list of specific fixes.\nSOURCE:\n{s['retrieved_context']}\nCONTENT:\n{content}")
    return {"critique": critique, "step_history": s["step_history"] + ["Reviewed accuracy and consistency"]}


def revision_node(s: GTMState) -> dict:
    revised = {}
    for fmt, draft in s["drafts"].items():
        revised[fmt] = llm(f"Revise this {fmt} using the review notes. Return ONLY the final {fmt}. Preserve all required elements. Do not add unsupported facts.\nSOURCE:\n{s['retrieved_context']}\nREVIEW NOTES:\n{s['critique']}\nDRAFT:\n{draft}")
    return {"final_content": revised, "step_history": s["step_history"] + ["Revised all formats", "Awaiting human approval; nothing published"]}


def build_graph():
    graph = StateGraph(GTMState)
    for name, fn in [("retrieve", retrieval_node), ("research", research_node), ("draft", draft_node), ("review", review_node), ("revise", revision_node)]:
        graph.add_node(name, fn)
    graph.set_entry_point("retrieve")
    graph.add_edge("retrieve", "research")
    graph.add_edge("research", "draft")
    graph.add_edge("draft", "review")
    graph.add_edge("review", "revise")
    graph.add_edge("revise", END)
    return graph.compile()


def run_agent(product: str, audience: str, tone: str, source_text: str) -> GTMState:
    if not product.strip() or not source_text.strip():
        raise ValueError("Provide a product name and non-empty source document.")
    return build_graph().invoke({"product": product.strip(), "audience": audience.strip(), "tone": tone.strip(), "source_text": source_text, "errors": [], "step_history": []})
