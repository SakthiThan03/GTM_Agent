# Week 3 Project Documentation — GTM Agent: Ideation to Copy

**Project:** GTM Agent — Ideation to Copy (3D)  
**Build track:** Python, LangGraph, Streamlit  
**Status:** Implementation prepared; live model execution and output validation must be completed by the submitter.

## Project overview
The GTM Agent turns a product or event brief into four marketing assets: a LinkedIn post, promotional email, short blog draft, and three ad copy variations. It retrieves relevant source text, optionally searches the web, drafts the content, runs an independent critique, revises it, and pauses for human approval before download. It does not publish anything.

## Dataset / source materials
A fictional `sample_data/product_launch.txt` brief for TripSpark is bundled. The app also accepts a user-uploaded TXT or text-based PDF. Local TF-IDF retrieval selects relevant passages. Optional Tavily results provide supplemental research, which is treated as unverified unless corroborated.

## Architecture and state
LangGraph runs `retrieve → research → draft → review → revise`. The graph state stores product, audience, tone, source, retrieved context, research status, drafts, critique, final outputs, and execution history. Streamlit holds the completed output and human approval within the browser session.

## Prompt design
- Draft prompt: generate each format using source excerpts, target audience, and brand tone; do not invent facts or links.
- Critique prompt: independently check factual grounding, cross-format consistency, unsupported promises, and tone.
- Revision prompt: rewrite each format using critique notes while retaining source grounding.

## Vibe-coding / AI assistance
Initial code and documentation were generated with ChatGPT assistance. **Before submitting, add the exact prompts you personally used, any edits you made, and screenshots or logs of actual runs.** Do not claim experiments or testing that have not happened.

## Iterations and observations (complete after running)
1. First run: [date, input, result, issues]
2. Error-path test: [remove Tavily key or simulate timeout, note fallback]
3. Revision/quality check: [identify and correct a factual or style issue]

## Evaluation
Test three different product briefs. For each, record: completed all four formats (yes/no), review critique present (yes/no), factual claims supported by brief (count), approval required (yes/no), and runtime. Target 3/3 complete runs with no unsupported product claims in the final approved copy.

## Error handling and human-in-the-loop
Tavily failures degrade to document-only mode. The UI catches parsing/model errors and gives retry guidance. Content remains a draft until a human checks the approval box. The app never sends email or publishes posts.

## Limitations / future improvements
The model can still hallucinate; the review agent is not a guarantee. TF-IDF is lightweight and lacks semantic embedding depth. Session state is not durable between browser sessions. Add claim-level citations, persistent history, automated evals, and provider-specific publication approval flows later.

## Submission artifacts
- GitHub repository: [ADD URL AFTER PUSH]
- Demo video (≤5 minutes): [ADD LINK AFTER RECORDING]
- Google Doc: paste this document into a Google Doc and complete the run evidence.
