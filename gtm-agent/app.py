"""Streamlit UI for the Week 3 GTM agent."""
import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from pypdf import PdfReader
from agent import FORMATS, run_agent

load_dotenv()
st.set_page_config(page_title="GTM Content Agent", page_icon="🚀", layout="wide")
st.title("🚀 GTM Agent — Ideation to Copy")
st.caption("Document-grounded marketing drafts • Agentic research + critique • Human approval")

sample = Path(__file__).parent / "sample_data" / "product_launch.txt"
with st.sidebar:
    st.header("Configuration")
    st.write("LLM key configured:", "Yes" if os.getenv("OPENAI_API_KEY") else "No — add it to .env")
    st.write("Optional Tavily research:", "Enabled" if os.getenv("TAVILY_API_KEY") else "Off (document-only)")
    st.info("No posts or emails are ever sent automatically.")

product = st.text_input("Product / feature name", value="TripSpark")
audience = st.text_input("Target audience", value="Sports fans and concertgoers planning event trips")
tone = st.selectbox("Brand tone", ["Friendly, energetic, practical", "Professional and clear", "Playful and conversational", "Confident and concise"])
uploaded = st.file_uploader("Upload product brief (TXT or PDF)", type=["txt", "pdf"])
use_sample = st.checkbox("Use included fictional sample brief", value=True)
source_text = ""
if uploaded:
    if uploaded.name.lower().endswith(".pdf"):
        try:
            reader = PdfReader(uploaded)
            source_text = "\n".join(page.extract_text() or "" for page in reader.pages)
        except Exception as exc:
            st.error(f"Could not parse PDF: {exc}")
    else:
        source_text = uploaded.getvalue().decode("utf-8", errors="replace")
elif use_sample:
    source_text = sample.read_text(encoding="utf-8")
with st.expander("Source document preview"):
    st.text_area("Source", value=source_text, height=190, disabled=True)

if st.button("Generate content suite", type="primary"):
    st.session_state.pop("result", None)
    st.session_state["approved"] = False
    if not source_text.strip():
        st.error("Upload a non-empty document or use the sample.")
    elif not os.getenv("OPENAI_API_KEY"):
        st.error("Add OPENAI_API_KEY to your .env file first (see README).")
    else:
        try:
            with st.spinner("Running retrieval → research → drafting → review → revision..."):
                st.session_state["result"] = run_agent(product, audience, tone, source_text)
        except Exception as exc:
            st.error(f"Agent could not finish: {type(exc).__name__}: {exc}")
            st.info("Check API key, model name, network connection, and provider quota; then retry.")

result = st.session_state.get("result")
if result:
    st.success("Drafts ready for human review. Nothing has been published.")
    with st.expander("Agent execution log", expanded=False):
        for step in result.get("step_history", []):
            st.write("•", step)
        st.write("Research status:", result.get("research_status", "unknown"))
    with st.expander("Review agent feedback"):
        st.write(result.get("critique", ""))
    for fmt in FORMATS:
        st.subheader(fmt)
        st.text_area(fmt, value=result["final_content"].get(fmt, ""), height=240, key=f"final_{fmt}")
    st.checkbox("I have checked the content for accuracy and approve it for manual use", key="approved")
    if st.session_state.get("approved"):
        output = "\n\n".join(f"# {fmt}\n\n{st.session_state[f'final_{fmt}']}" for fmt in FORMATS)
        st.download_button("Download approved content (.md)", data=output, file_name="gtm_content_suite.md", mime="text/markdown")
    else:
        st.info("Review and approve to enable download. Publishing/sending remains manual.")
