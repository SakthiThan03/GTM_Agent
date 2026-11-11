# 4-minute demo script

**0:00–0:35 — Introduction**  
“My project is a GTM content agent. It transforms a product brief into a LinkedIn post, promotional email, blog draft, and ad copy, while checking the outputs for factual accuracy.”

**0:35–1:15 — Architecture**  
“LangGraph manages five stages: retrieval, optional web research, drafting, critique, and revision. State moves between the stages. Streamlit provides the interface and approval gate.”

**1:15–2:35 — Live demo**  
“Here is a fictional TripSpark product brief. I’ll generate a content suite, then inspect the four outputs and the critique. The Tavily search is optional; without it, the workflow uses only the brief.” [RUN THE APP AND SHOW REAL OUTPUTS.]

**2:35–3:20 — Error handling and approval**  
“If research fails, the agent falls back to document-only generation. Model failures show a clear error instead of fabricated success. The app cannot download approved content until I check the human approval box, and it never auto-publishes.”

**3:20–4:00 — Lessons and next steps**  
“The key challenge is not one prompt but multi-step control flow and keeping claims grounded. I’d next add claim-level citations, persistent memory, and automated quality tests.”

> Record the actual application and only claim results you verified. Keep under five minutes.
