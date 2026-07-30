import streamlit as st
from search_engine import search_legal_query

# ──────────────────────────────────────────────
# Page Config
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="Legal AI — Research Assistant",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ──────────────────────────────────────────────
# Session State Initialization
# ──────────────────────────────────────────────
if "results" not in st.session_state:
    st.session_state["results"] = []

if "query" not in st.session_state:
    st.session_state["query"] = ""

# ──────────────────────────────────────────────
# Helper Functions
# ──────────────────────────────────────────────
def generate_research_note(results):
    """Generate a concise research note from RATIO paragraphs."""
    points = []

    # Pass 1: Use RATIO paragraphs
    for r in results:
        if r["para_type"] == "RATIO":
            point = f"- {r['text'].strip()} ({r['case_title']})"
            points.append(point)

    # Pass 2: Fallback to OTHER if no RATIO found
    if not points:
        for r in results:
            point = f"- {r['text'].strip()} ({r['case_title']})"
            points.append(point)

    if not points:
        return "No relevant legal principles found for this query."

    note = "LEGAL RESEARCH NOTE\n\n"
    note += "Based on relevant Supreme Court judgments, the following legal principles and observations emerge:\n\n"
    note += "\n\n".join(points[:5])

    note += "\n\n---\n"
    note += "This note is generated from Supreme Court judgments using semantic search."

    return note


def generate_bail_draft(results, inputs):
    """Generate a bail application first draft from search results and case inputs."""
    citations = []

    for r in results:
        if r["para_type"] == "RATIO":
            citations.append(r["case_title"])

    if not citations:
        citations = [r["case_title"] for r in results[:3]]

    unique_citations = list(dict.fromkeys(citations))

    draft = f"""
IN THE COURT OF {inputs.get("court_name", "___________") or "___________"}

BAIL APPLICATION UNDER SECTION 437/439 Cr.P.C.

IN THE MATTER OF:

{inputs.get("applicant_name", "___________________________") or "___________________________"}  ...Applicant
Versus
State of ________________   ...Respondent

MOST RESPECTFULLY SHOWETH:

1. That the Applicant has been arrested in FIR No. {inputs.get("fir_number", "_____") or "_____"}
   registered under Sections {inputs.get("sections", "_____") or "_____"}
   at {inputs.get("police_station", "_____") or "_____"} Police Station.

2. That the Applicant was taken into custody on {inputs.get("custody_date", "_____") or "_____"} .

3. That the Applicant has been falsely implicated and is innocent.

4. That the allegations do not disclose any serious offence warranting continued incarceration.

5. That arrest should not be automatic and must be based on necessity, as held by the Hon'ble Supreme Court in {", ".join(unique_citations)}.

6. That the Applicant undertakes to cooperate with the investigation and shall not tamper with evidence.

7. That the Applicant has deep roots in society and is not a flight risk.

8. That the brief facts of the case are as follows:
   {inputs.get("case_facts", "_____________________________________________") or "_____________________________________________"}

PRAYER

It is therefore most respectfully prayed that this Hon'ble Court may be pleased to enlarge the Applicant on bail in the interest of justice.

Place:
Date:

COUNSEL FOR THE APPLICANT
"""

    return draft.strip()


# ──────────────────────────────────────────────
# Callback Handlers (Guarantees Instant Button Response)
# ──────────────────────────────────────────────
def do_search():
    q = st.session_state.get("query_input", "").strip()
    if q:
        st.session_state["query"] = q
        st.session_state["results"] = search_legal_query(q, max_results=6)
        st.session_state.pop("txt_research_note", None)
        st.session_state.pop("txt_bail_draft", None)

def do_generate_note():
    results = st.session_state.get("results", [])
    if results:
        note = generate_research_note(results)
        st.session_state["txt_research_note"] = note

def do_generate_draft():
    results = st.session_state.get("results", [])
    if results:
        inputs = {
            "applicant_name": st.session_state.get("applicant_name", ""),
            "fir_number": st.session_state.get("fir_number", ""),
            "sections": st.session_state.get("sections", ""),
            "police_station": st.session_state.get("police_station", ""),
            "court_name": st.session_state.get("court_name", ""),
            "custody_date": st.session_state.get("custody_date", ""),
            "case_facts": st.session_state.get("case_facts", ""),
        }
        draft = generate_bail_draft(results, inputs)
        st.session_state["txt_bail_draft"] = draft


# ──────────────────────────────────────────────
# Custom CSS — Dark Theme + Typography + Cards
# ──────────────────────────────────────────────
st.markdown("""
<style>
    /* ── Google Font ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* ── Root Theme Variables ── */
    :root {
        --bg-primary: #0f1117;
        --bg-secondary: #1a1d23;
        --bg-card: #1e2128;
        --bg-card-hover: #252830;
        --border-subtle: #2a2d35;
        --border-accent: #3b82f6;
        --text-primary: #e8eaed;
        --text-secondary: #9aa0a6;
        --text-muted: #6b7280;
        --accent-blue: #3b82f6;
        --accent-green: #22c55e;
        --accent-amber: #f59e0b;
        --accent-red: #ef4444;
        --accent-purple: #a855f7;
        --gradient-start: #3b82f6;
        --gradient-end: #8b5cf6;
        --shadow-card: 0 2px 8px rgba(0,0,0,0.3);
        --radius-md: 10px;
        --radius-lg: 14px;
    }

    /* ── Global Reset ── */
    html, body, [data-testid="stAppViewContainer"],
    [data-testid="stApp"], .main, .block-container {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        color: var(--text-primary) !important;
    }

    /* ── Hide default Streamlit chrome ── */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stToolbar"] {display: none;}

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: var(--bg-secondary) !important;
        border-right: 1px solid var(--border-subtle) !important;
    }
    [data-testid="stSidebar"] .block-container {
        padding-top: 2rem !important;
    }
    [data-testid="stSidebar"] label {
        color: var(--text-secondary) !important;
        font-size: 0.8rem !important;
        font-weight: 500 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
    }

    /* ── Sidebar Input Fields ── */
    [data-testid="stSidebar"] input,
    [data-testid="stSidebar"] textarea {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 8px !important;
        color: var(--text-primary) !important;
        font-size: 0.88rem !important;
    }
    [data-testid="stSidebar"] input:focus,
    [data-testid="stSidebar"] textarea:focus {
        border-color: var(--accent-blue) !important;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.15) !important;
    }

    /* ── Main Area Input Fields ── */
    .stTextInput > div > div > input {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--radius-md) !important;
        color: var(--text-primary) !important;
        padding: 0.75rem 1rem !important;
        font-size: 1rem !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }
    .stTextInput > div > div > input:focus {
        border-color: var(--accent-blue) !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2) !important;
    }
    .stTextInput > div > div > input::placeholder {
        color: var(--text-muted) !important;
    }

    /* ── Buttons (Interactive & Responsive) ── */
    div[data-testid="stButton"] > button {
        width: 100% !important;
        background: linear-gradient(135deg, var(--gradient-start), var(--gradient-end)) !important;
        color: white !important;
        border: none !important;
        border-radius: var(--radius-md) !important;
        padding: 0.65rem 1.5rem !important;
        font-weight: 600 !important;
        font-size: 0.92rem !important;
        letter-spacing: 0.02em !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 8px rgba(59, 130, 246, 0.25) !important;
    }
    div[data-testid="stButton"] > button:hover {
        opacity: 0.92 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 16px rgba(59, 130, 246, 0.35) !important;
    }
    div[data-testid="stButton"] > button:active {
        transform: translateY(0) !important;
        opacity: 1 !important;
    }

    /* ── Download Buttons ── */
    div[data-testid="stDownloadButton"] > button {
        width: 100% !important;
        background: transparent !important;
        border: 1px solid var(--border-subtle) !important;
        color: var(--text-secondary) !important;
        border-radius: 8px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 500 !important;
        font-size: 0.85rem !important;
        cursor: pointer !important;
        box-shadow: none !important;
        transition: border-color 0.2s ease, color 0.2s ease !important;
    }
    div[data-testid="stDownloadButton"] > button:hover {
        border-color: var(--accent-blue) !important;
        color: var(--accent-blue) !important;
    }

    /* ── Expanders ── */
    .streamlit-expanderHeader {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 8px !important;
        color: var(--text-secondary) !important;
        font-size: 0.88rem !important;
        font-weight: 500 !important;
    }
    .streamlit-expanderContent {
        background: var(--bg-secondary) !important;
        border: 1px solid var(--border-subtle) !important;
        border-top: none !important;
        border-radius: 0 0 8px 8px !important;
        color: var(--text-primary) !important;
        line-height: 1.7 !important;
        font-size: 0.92rem !important;
    }

    /* ── Text Areas (generated drafts) ── */
    .stTextArea textarea {
        background: var(--bg-card) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--radius-md) !important;
        font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace !important;
        font-size: 0.85rem !important;
        line-height: 1.6 !important;
    }

    /* ── Custom Classes ── */
    .brand-header {
        padding: 0.5rem 0 1.5rem 0;
    }
    .brand-header .accent-bar {
        width: 60px;
        height: 4px;
        background: linear-gradient(90deg, var(--gradient-start), var(--gradient-end));
        border-radius: 2px;
        margin-bottom: 1rem;
    }
    .brand-header h1 {
        font-size: 2rem;
        font-weight: 700;
        color: var(--text-primary);
        margin: 0 0 0.35rem 0;
        letter-spacing: -0.02em;
    }
    .brand-header .tagline {
        font-size: 0.95rem;
        color: var(--text-secondary);
        font-weight: 400;
    }

    .result-card {
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-left: 3px solid var(--accent-blue);
        border-radius: var(--radius-md);
        padding: 1.25rem 1.5rem;
        margin-bottom: 1rem;
        transition: background 0.2s ease, border-color 0.2s ease;
        box-shadow: var(--shadow-card);
    }
    .result-card:hover {
        background: var(--bg-card-hover);
        border-left-color: var(--accent-purple);
    }
    .result-card .card-title {
        font-size: 1.05rem;
        font-weight: 600;
        color: var(--text-primary);
        margin: 0 0 0.4rem 0;
    }
    .result-card .card-meta {
        font-size: 0.8rem;
        color: var(--text-muted);
        margin-bottom: 0.5rem;
    }

    .badge {
        display: inline-block;
        padding: 0.18rem 0.6rem;
        border-radius: 999px;
        font-size: 0.72rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-right: 0.4rem;
        vertical-align: middle;
    }
    .badge-ratio {
        background: rgba(34, 197, 94, 0.12);
        color: var(--accent-green);
        border: 1px solid rgba(34, 197, 94, 0.25);
    }
    .badge-other {
        background: rgba(107, 114, 128, 0.12);
        color: var(--text-secondary);
        border: 1px solid rgba(107, 114, 128, 0.25);
    }
    .badge-cited {
        background: rgba(245, 158, 11, 0.12);
        color: var(--accent-amber);
        border: 1px solid rgba(245, 158, 11, 0.25);
    }
    .badge-para {
        background: rgba(59, 130, 246, 0.10);
        color: var(--accent-blue);
        border: 1px solid rgba(59, 130, 246, 0.20);
    }

    .result-count {
        display: inline-block;
        background: rgba(59, 130, 246, 0.10);
        color: var(--accent-blue);
        padding: 0.25rem 0.8rem;
        border-radius: 999px;
        font-size: 0.82rem;
        font-weight: 500;
        margin-top: 0.5rem;
    }

    .section-label {
        font-size: 0.78rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--text-muted);
        margin: 2rem 0 0.75rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid var(--border-subtle);
    }

    .gen-header {
        font-size: 0.95rem;
        font-weight: 600;
        color: var(--text-primary);
        margin: 0.75rem 0 0.25rem 0;
    }

    .app-footer {
        margin-top: 4rem;
        padding: 1.5rem 0;
        border-top: 1px solid var(--border-subtle);
        text-align: center;
    }
    .app-footer p {
        font-size: 0.78rem;
        color: var(--text-muted);
        margin: 0.15rem 0;
    }
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# Sidebar — Case Detail Inputs
# ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="margin-bottom: 1.5rem;">
        <span style="font-size: 1.3rem;">📋</span>
        <span style="font-size: 1.05rem; font-weight: 600; color: #e8eaed; margin-left: 0.4rem;">Case Details</span>
        <p style="font-size: 0.8rem; color: #6b7280; margin: 0.3rem 0 0 0;">Optional — used for bail draft generation</p>
    </div>
    """, unsafe_allow_html=True)

    st.text_input("Applicant Name", key="applicant_name")
    st.text_input("FIR Number", key="fir_number")
    st.text_input("Sections Invoked", key="sections", placeholder="e.g. 420, 406 IPC")
    st.text_input("Police Station", key="police_station")
    st.text_input("Court Name", key="court_name")
    st.text_input("Custody Date", key="custody_date")
    st.text_area("Brief Case Facts", key="case_facts", height=100)

    st.markdown("""
    <div style="margin-top: 2rem; padding-top: 1rem; border-top: 1px solid #2a2d35;">
        <p style="font-size: 0.75rem; color: #6b7280; margin: 0;">
            ⚡ Powered by FAISS + Sentence Transformers
        </p>
    </div>
    """, unsafe_allow_html=True)


# ──────────────────────────────────────────────
# Branded Header
# ──────────────────────────────────────────────
st.markdown("""
<div class="brand-header">
    <div class="accent-bar"></div>
    <h1>⚖️ Legal Research Assistant</h1>
    <div class="tagline">Semantic case law search with citation-aware ranking</div>
</div>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# Search Bar & Trigger
# ──────────────────────────────────────────────
st.text_input(
    "Search case law",
    placeholder="e.g. arrest guidelines supreme court, bail conditions, FIR registration...",
    key="query_input",
    on_change=do_search,
    label_visibility="collapsed"
)

search_col, _ = st.columns([1, 4])
with search_col:
    st.button("🔍  Search", key="btn_search", on_click=do_search, use_container_width=True)

results = st.session_state.get("results", [])


# ──────────────────────────────────────────────
# Results & Document Generators
# ──────────────────────────────────────────────
if results:
    st.markdown(f"""
    <div class="result-count">
        {len(results)} result{"s" if len(results) != 1 else ""} found for "{st.session_state.get('query', '')}"
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-label">Search Results</div>', unsafe_allow_html=True)

    for i, r in enumerate(results, 1):
        type_badge = (
            '<span class="badge badge-ratio">Ratio</span>'
            if r["para_type"] == "RATIO"
            else '<span class="badge badge-other">Observation</span>'
        )

        citation_badge = (
            '<span class="badge badge-cited">Quoted Case</span>'
            if r.get("is_cross_citation")
            else ""
        )

        para_badge = (
            f'<span class="badge badge-para">¶ {r["paragraph"]}</span>'
            if r.get("paragraph")
            else ""
        )

        year_display = f" ({r['year']})" if r.get("year") else ""

        st.markdown(f"""
        <div class="result-card">
            <div style="display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap;">
                <span class="card-title">{i}. {r['case_title']}{year_display}</span>
                {type_badge}{citation_badge}{para_badge}
            </div>
            <div class="card-meta">{r.get('court', 'Court not specified')}</div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander(f"📖  Read paragraph text — {r['case_title']}"):
            st.write(r["text"])

    # ──────────────────────────────────────────
    # Document Generators
    # ──────────────────────────────────────────
    st.markdown('<div class="section-label">Generate Documents</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.button("📄  Generate Research Note", key="btn_gen_note", on_click=do_generate_note, use_container_width=True)

        if "txt_research_note" in st.session_state:
            st.markdown('<p class="gen-header">📄 Legal Research Note</p>', unsafe_allow_html=True)
            st.text_area(
                "research_note_area",
                key="txt_research_note",
                height=300,
                label_visibility="collapsed"
            )
            st.download_button(
                "⬇  Download Research Note",
                data=st.session_state["txt_research_note"],
                file_name="legal_research_note.txt",
                mime="text/plain",
                key="btn_dl_note",
                use_container_width=True
            )

    with col2:
        st.button("📝  Generate Bail Draft", key="btn_gen_draft", on_click=do_generate_draft, use_container_width=True)

        if "txt_bail_draft" in st.session_state:
            st.markdown('<p class="gen-header">📝 Bail Application Draft</p>', unsafe_allow_html=True)
            st.text_area(
                "bail_draft_area",
                key="txt_bail_draft",
                height=350,
                label_visibility="collapsed"
            )
            st.download_button(
                "⬇  Download Bail Draft",
                data=st.session_state["txt_bail_draft"],
                file_name="bail_application_draft.txt",
                mime="text/plain",
                key="btn_dl_draft",
                use_container_width=True
            )

else:
    # Empty state
    st.markdown("""
    <div style="text-align: center; padding: 4rem 1rem; color: #6b7280;">
        <div style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.5;">🔍</div>
        <p style="font-size: 1.1rem; font-weight: 500; margin: 0;">
            Enter a legal query above to search Supreme Court judgments
        </p>
        <p style="font-size: 0.85rem; margin-top: 0.5rem;">
            Try: "arrest guidelines", "bail conditions", "FIR registration mandatory"
        </p>
    </div>
    """, unsafe_allow_html=True)


# ──────────────────────────────────────────────
# Footer
# ──────────────────────────────────────────────
st.markdown("""
<div class="app-footer">
    <p>⚖️ <strong>Legal Research Assistant</strong> — MVP v2.0</p>
    <p>Semantic search over Indian Supreme Court landmark judgments</p>
    <p style="margin-top: 0.5rem;">Built with Streamlit · FAISS · Sentence Transformers</p>
</div>
""", unsafe_allow_html=True)
