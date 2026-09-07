# ⚖️ Legal AI — Supreme Court Semantic Search & Draft Assistant

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white" alt="Python 3.10+" />
  <img src="https://img.shields.io/badge/Streamlit-1.x-FF4B4B?logo=streamlit&logoColor=white" alt="Streamlit" />
  <img src="https://img.shields.io/badge/FAISS-CPU_Flat_L2-00599C?logo=meta&logoColor=white" alt="FAISS" />
  <img src="https://img.shields.io/badge/Sentence_Transformers-all--MiniLM--L6--v2-FFA000" alt="Sentence Transformers" />
  <img src="https://img.shields.io/badge/License-MIT-2ECC71" alt="License" />
</p>

> A domain-specific semantic search engine and automated document generation tool built over landmark **Supreme Court of India criminal judgments** — combining dense vector embeddings, a custom multi-pass legal holding ranker, and an interactive Streamlit application.

---

## 📌 Motivation & Problem Statement

Legal research in Indian case law is traditionally bottlenecked by unstructured, multi-page PDFs that contain recurring watermark artifacts, irregular line breaks, and dense judicial language. Standard keyword search frequently falls short because:

1. **Vocabulary Mismatch:** Keyword queries miss synonymous legal concepts (e.g., searching *"illegal detention"* can fail to match rulings discussing *"custodial restraint without statutory procedure"*).
2. **Lack of Precedent Hierarchy:** Off-the-shelf vector search models treat factual narrations, passing observations (*obiter dicta*), and binding legal principles (*ratio decidendi*) with equal semantic priority, often surfacing case facts instead of the core rule of law.

### Why I Built This (Student Engineering Perspective)
Rather than wrapping a generic third-party LLM API around raw text, I wanted to build the foundational data engineering and retrieval layers from scratch:
- Designing a robust heuristic PDF ingestion pipeline to clean and stitch legal text without losing context.
- Indexing dense semantic representations locally using FAISS and Sentence Transformers.
- Implementing a domain-aware, multi-pass ranking system that prioritizes binding holdings over secondary quotations.

---

## 🏛️ System Architecture

```
                                [ Raw Supreme Court PDFs ]
                                             │
                                             ▼
                                  [ ingest.py Pipeline ]
                     ┌───────────────────────┴───────────────────────┐
                     ▼                                               ▼
        [ Junk Filter & Normalizer ]                    [ Lookahead Sentence Stitcher ]
        • Strips Kanoon watermarks                     • Merges cross-page linebreaks
        • Filters running page headers                 • Detects true paragraph boundaries
                     └───────────────────────┬───────────────────────┘
                                             │
                                             ▼
                                 [ Paragraph Classifier ]
                                 • Type: RATIO / FACTS / OTHER
                                 • Cross-citation regex & self-ref suppression
                                             │
                                             ▼
                                  [ build_index.py ]
                            sentence-transformers/all-MiniLM-L6-v2
                                             │
                                             ▼
                                    [ FAISS Flat Index ]
                                             │
                                             ▼
                                 [ search_engine.py ]
                             6-Tier / 4-Pass Priority Ranker
                                             │
                                             ▼
                                [ streamlit_app.py UI ]
                   ┌─────────────────────────┴─────────────────────────┐
                   ▼                                                   ▼
        [ Semantic Search Cards ]                           [ Document Synthesis Engine ]
        • Ratio / Citation badges                           • Legal Research Notes
        • Dynamic metadata filters                          • Pre-populated Bail Drafts
```

---

## ⚙️ Core Technical Implementation

### 1. PDF Text Defragmentation & Cleaning Pipeline (`ingest.py`)
- **Heuristic Noise Filtering:** Implemented `is_junk_line()` to dynamically detect and remove recurring page headers (matching case titles), page counters, and Indian Kanoon watermarks before text assembly.
- **Lookahead Sentence Stitching:** Standard line-by-line extraction splits sentences across page breaks. Built an abbreviation-aware lookahead buffer (`is_paragraph_end`) that checks subsequent character casing (`next_line[0].islower()`) and terminal punctuation (`."`, `.)`) to merge fragmented lines.
- **Data Recovery Impact:** Fixed arbitrary line truncation and extension-matching issues, expanding indexed text from an initial **124 fragmented paragraphs to 372 rich, cohesive paragraphs (~3x data density increase)** across 6 landmark cases.

### 2. Legal Metadata Extraction & Citation Isolation
- Used regex matching (`X v. Y` / `A vs. B`) with self-reference filtering: if a cited title matches the judgment's own title, it is flagged as `is_cross_citation = False` so core holdings are not misclassified as external quotations.
- Tagged paragraphs into categorical types: `RATIO` (core holdings), `FACTS` (case background), and `OTHER` (procedural orders and guidelines).

### 3. Multi-Pass Priority Search Algorithm (`search_engine.py`)
Dense retrieval alone often ranks lengthy factual summaries highly if they mention query terms frequently. To surface authoritative law first, the search engine retrieves top-$K$ candidate vectors ($L_2$ distance) and re-ranks them through a **6-tier priority filter**:

| Pass | Target Content | Cross-Citation | Priority Level |
| :---: | :--- | :---: | :--- |
| **Pass 1** | Direct *ratio decidendi* / binding holding | No | ⭐⭐⭐ **Highest** |
| **Pass 2** | *Ratio decidendi* quoting precedent | Yes | ⭐⭐ **High** |
| **Pass 3** | Direct judicial observation / guideline (`OTHER`) | No | ⭐⭐ **High** |
| **Pass 4** | Precedent-backed observation (`OTHER`) | Yes | ⭐ **Medium** |
| **Pass 5** | Case facts (`FACTS`) | No | Low |
| **Pass 6** | General fallback matches | Any | Lowest |

### 4. Interactive Frontend & Draft Generation (`streamlit_app.py`)
- **Reliable State Management:** Replaced inline button checks with explicit `on_click` and `on_change` callbacks (`do_search`, `do_generate_note`, `do_generate_draft`), eliminating session-state drops during Streamlit rerenders.
- **Keyboard Search Trigger:** Bound query input to `on_change=do_search` to enable instant search execution on the `Enter` key.
- **Automated Draft Synthesis:** Converts retrieved holding paragraphs and sidebar case parameters (FIR details, applicant name, custody date) into structured **Legal Research Notes** and court-ready **Bail Application Drafts**, downloadable as `.txt` files.

---

## 📚 Indexed Landmark Case Law

The benchmark dataset consists of seminal Supreme Court of India rulings governing criminal procedure, personal liberty, and arrest safeguards:

| Case Law | Bench & Year | Primary Legal Principle | Paragraphs |
| :--- | :--- | :--- | :---: |
| *Arnesh Kumar v. State of Bihar* | Supreme Court (2014) | Mandatory notice & arrest checklist under Sec 41 CrPC | 20 |
| *D.K. Basu v. State of West Bengal* | Supreme Court (1997) | Constitutional safeguards against custodial violence | 83 |
| *Joginder Kumar v. State of U.P.* | Supreme Court (1994) | Distinction between power to arrest and justification | 37 |
| *Lalita Kumari v. Govt. of U.P.* | Supreme Court (2014) | Mandatory registration of FIR in cognizable offenses | 170 |
| *Manubhai Ratilal Patel v. State of Gujarat* | Supreme Court (2013) | Judicial application of mind required during remand | 34 |
| *State of Haryana v. Bhajan Lal* | Supreme Court (1992) | Standard guidelines for quashing malicious FIRs | 28 |
| **Total Indexed Corpus** | — | — | **372 paragraphs** |

---

## 🚀 Quickstart Guide

### Prerequisites
- Python 3.10+
- Git

### 1. Clone Repository & Setup Virtual Environment
```bash
git clone https://github.com/soumyadip-das-dev/Legal-AI-Research-Assistant.git
cd Legal-AI-Research-Assistant

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux / macOS:
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install streamlit faiss-cpu sentence-transformers pdfplumber tqdm langchain-community
```

### 3. Build the Database & Vector Index
```bash
# Extract, clean, and categorize paragraphs into data/processed/judgments.json
python ingest.py

# Generate dense embeddings and initialize FAISS index at data/faiss_index/
python build_index.py
```

### 4. Run the Streamlit Application
```bash
streamlit run streamlit_app.py
```
Open **http://localhost:8501** in your web browser.

---

## 💡 Example Queries to Test

| Query | Expected Retrieval |
| :--- | :--- |
| `"mandatory FIR registration cognizable offence"` | Surfaces binding holding from *Lalita Kumari (2014)* |
| `"guidelines to prevent unnecessary arrest"` | Retrieves Section 41 CrPC checklist from *Arnesh Kumar (2014)* |
| `"custodial torture arrestee rights inspection memo"` | Returns procedural guidelines from *D.K. Basu (1997)* |
| `"grounds for quashing criminal proceedings"` | Ranks illustrative quashing criteria from *Bhajan Lal (1992)* |

---

## 🛠️ Key Technical Learnings

1. **PDF Text Stream Realities:** Standard PDF extractors emit text by bounding-box coordinates rather than grammatical flow. Robust extraction requires line-level noise filtering and lookahead casing heuristics before feeding data to an embedding model.
2. **Metadata-Guided Re-ranking:** Dense embeddings alone struggle with domain hierarchy. Incorporating structural classification (e.g., distinguishing *ratio decidendi* from *facts*) into a multi-pass ranking algorithm substantially improves legal relevance over naive nearest-neighbor search.
3. **Reactive UI State:** In Streamlit, coupling long-running actions or multi-step draft generation to explicit callback functions avoids unpredictable state resets across UI reruns.

---

## 🗺️ Roadmap

Planned features and technical improvements:
- [ ] Hybrid search combining dense embeddings with BM25 lexical search (Reciprocal Rank Fusion).
- [ ] Contextual Q&A using open-source instruction-tuned LLMs (e.g., Mistral-7B / Llama-3).
- [ ] Automated evaluation suite measuring Mean Reciprocal Rank (MRR) across a golden test set of legal queries.
- [ ] Cloud deployment on Streamlit Community Cloud / Hugging Face Spaces.

---

## 📜 License & Disclaimer

- **License:** Licensed under the [MIT License](LICENSE).
- **Disclaimer:** This software is developed for educational and academic research purposes. Generated research notes and bail drafts are initial drafts and do not constitute formal legal advice.
