# ⚖️ Legal AI — Research Assistant

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Streamlit-1.x-FF4B4B?logo=streamlit&logoColor=white" />
  <img src="https://img.shields.io/badge/FAISS-CPU-blueviolet?logo=meta&logoColor=white" />
  <img src="https://img.shields.io/badge/Sentence_Transformers-all--MiniLM--L6--v2-orange" />
  <img src="https://img.shields.io/badge/License-MIT-green" />
</p>

> A semantic search engine and automated legal document generation tool built over **Indian Supreme Court landmark judgments** — powered by FAISS vector embeddings, Sentence Transformers, and a custom 4-pass citation-aware ranking algorithm.

---

## ✨ Feature Highlights

| Feature | Description |
|---|---|
| 🔍 **Semantic Search** | Dense vector retrieval using `all-MiniLM-L6-v2` over 370+ indexed paragraphs |
| 🏛️ **Citation-Aware Ranking** | 4-pass priority system: direct holdings → precedent holdings → observations → fallbacks |
| 📄 **Legal Research Note Generator** | One-click synthesis of key legal principles from retrieved case law |
| 📝 **Bail Application Draft Generator** | Auto-populated first draft with case metadata and cited Supreme Court precedents |
| ⬇️ **Download Documents** | Export generated notes and bail drafts as `.txt` files |
| 🌙 **Dark Theme UI** | Custom CSS design system with Google Fonts (`Inter`), gradient badges, and hover cards |
| ⌨️ **Search on Enter** | Instant search triggered by pressing Enter or clicking the Search button |

---

## 🗂️ Project Architecture

```
legal_ai/
├── data/
│   ├── raw_pdfs/           # Source PDF judgments (place your PDFs here)
│   ├── processed/
│   │   └── judgments.json  # Structured paragraph database (auto-generated)
│   └── faiss_index/        # FAISS vector index files (auto-generated)
├── ingest.py               # PDF extraction, paragraph stitching & metadata tagging engine
├── build_index.py          # Sentence Transformer embedding + FAISS index builder
├── search_engine.py        # 4-pass similarity search & citation-aware ranking module
├── streamlit_app.py        # Streamlit web application (UI + document generators)
├── CHANGELOG.md            # Detailed time-stamped project history & technical learnings
├── ROADMAP.md              # Planned enhancements & future features
├── .gitignore              # Excludes venv, __pycache__, large data files
└── README.md               # This file
```

---

## 🧠 How It Works

### 1. Ingestion Pipeline (`ingest.py`)
- Loads all PDFs from `data/raw_pdfs/` (case-insensitive extension matching)
- Strips running headers, footers, page numbers, and Indian Kanoon watermarks via `is_junk_line()`
- Stitches fragmented lines across page boundaries using lookahead-based `is_paragraph_end()` detection
- Classifies each paragraph into: `RATIO`, `FACTS`, or `OTHER`
- Detects cross-citations while filtering false-positive self-citations

### 2. Index Building (`build_index.py`)
- Encodes all paragraphs using `sentence-transformers/all-MiniLM-L6-v2`
- Stores dense embeddings in a FAISS flat L2 index for nearest-neighbor retrieval

### 3. Search Engine (`search_engine.py`)
Implements a **6-tier priority ranking**:

| Pass | Para Type | Cross-Citation | Priority |
|------|-----------|----------------|----------|
| 1 | `RATIO` | No | ⭐⭐⭐ Highest |
| 2 | `RATIO` | Yes | ⭐⭐ |
| 3 | `OTHER` | No | ⭐⭐ |
| 4 | `OTHER` | Yes | ⭐ |
| 5 | `FACTS` | No | Low |
| 6 | `FACTS` | Yes | Lowest |

### 4. Streamlit App (`streamlit_app.py`)
- Search bar with Enter-key trigger and `🔍 Search` button
- Results displayed as styled cards with `RATIO` / `Observation` / `Quoted Case` / `¶ N` badges
- Sidebar collects optional case metadata for bail draft generation
- Document generators use `on_click` callbacks to guarantee reliable Streamlit state updates

---

## 📚 Indexed Case Law

| Case | Court | Year | Paragraphs |
|------|-------|------|------------|
| Arnesh Kumar v. State of Bihar | Supreme Court of India | 2014 | 20 |
| D.K. Basu v. State of West Bengal | Supreme Court of India | 1997 | 83 |
| Joginder Kumar v. State of Uttar Pradesh | Supreme Court of India | 1994 | 37 |
| Lalita Kumari v. Government of Uttar Pradesh | Supreme Court of India | 2014 | 170 |
| Manubhai Ratilal Patel v. State of Gujarat | Supreme Court of India | 2013 | 34 |
| State of Haryana v. Bhajan Lal | Supreme Court of India | 1992 | 28 |
| **Total** | | | **~372 paragraphs** |

---

## 🚀 Quickstart

### Prerequisites
- Python 3.10+
- Git

### Step 1 — Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/legal_ai.git
cd legal_ai
```

### Step 2 — Create & activate virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python -m venv venv
source venv/bin/activate
```

### Step 3 — Install dependencies

```bash
pip install streamlit faiss-cpu sentence-transformers pdfplumber tqdm langchain-community
```

### Step 4 — Add your PDFs

Place Supreme Court judgment PDFs inside `data/raw_pdfs/`.

**Naming convention:** `Case_Name_vs_Respondent_YEAR.pdf`

```
data/raw_pdfs/
├── Arnesh_Kumar_vs_State_of_Bihar_2014.pdf
├── DK_Basu_vs_State_of_West_Bengal_1997.pdf
└── ...
```

### Step 5 — Build the knowledge base

```bash
python ingest.py       # Parse and process all PDFs
python build_index.py  # Build the FAISS vector index
```

### Step 6 — Launch the app

```bash
streamlit run streamlit_app.py
```

Open **http://localhost:8501** in your browser.

---

## 💡 Usage Tips

- **Search examples**: `arrest guidelines`, `bail conditions`, `FIR registration mandatory`, `custodial torture rights`
- Fill in the **sidebar fields** before generating a Bail Draft to get a pre-populated document
- Click **📄 Generate Research Note** to synthesize key holdings from search results
- Click **📝 Generate Bail Draft** to create a court-ready first draft
- Use the **⬇ Download** buttons to save documents as `.txt` files

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| UI Framework | [Streamlit](https://streamlit.io/) |
| Vector Embeddings | [Sentence Transformers](https://www.sbert.net/) (`all-MiniLM-L6-v2`) |
| Vector Database | [FAISS](https://faiss.ai/) (CPU) |
| PDF Parsing | [pdfplumber](https://github.com/jsvine/pdfplumber) |
| Progress Tracking | [tqdm](https://tqdm.github.io/) |
| Language | Python 3.10+ |

---

## 🗺️ Roadmap

See [ROADMAP.md](./ROADMAP.md) for planned features including multi-document upload, Gemini/GPT-powered Q&A, full-text Boolean search, and cloud deployment.

---

## 📋 Changelog

See [CHANGELOG.md](./CHANGELOG.md) for a detailed log of all changes, bug fixes, and technical learnings across all development phases.

---

## ⚠️ Disclaimer

This tool is for **legal research and educational purposes only**. Generated documents (research notes, bail drafts) are **first drafts** and must be reviewed by a qualified legal professional before use in any proceedings.

---

## 📜 License

This project is licensed under the **MIT License**.

---

<p align="center">Built with ❤️ using Streamlit · FAISS · Sentence Transformers</p>
