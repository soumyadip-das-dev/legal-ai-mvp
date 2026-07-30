# Project Changelog & Learning Log

This file tracks major changes, optimizations, and technical insights for the **Legal Research Assistant (MVP)** project.

---

## [2026-07-30] Phase 3: UI/UX Redesign & Explicit Button Callbacks

### Overview
Overhauled the Streamlit user interface with a custom dark theme design system, sidebar layout reorganization, and explicit `on_click` callback handlers for instant button interactions.

### Problems Identified & Solved

#### 1. Unresponsive Button Click Handlers
- **Problem**: Default Streamlit button evaluation (`if st.button(...)`) suffered from execution lifecycle issues during page reruns, causing document generation buttons ("Generate Research Note" and "Generate Bail Draft") to occasionally fail or lose session state.
- **Fix**: Bound all buttons to explicit Python callback handlers (`do_search`, `do_generate_note`, `do_generate_draft`) via `on_click`. Callbacks execute before script rerender, guaranteeing immediate state update in `st.session_state`.
- **Result**: Button clicks respond instantly, and generated research notes and bail application drafts render reliably.

#### 2. Search Trigger on Enter Key
- **Problem**: Pressing Enter in the query input field did not trigger a search automatically.
- **Fix**: Bound `on_change=do_search` to `st.text_input("query_input")`. Now pressing `Enter` or clicking the `🔍 Search` button triggers the search engine seamlessly.

#### 3. Modern Dark Theme Dashboard
- **Styling**: Injected custom CSS rules with Google Fonts (`Inter`), gradient accent header, custom CSS variables (`--bg-primary`, `--bg-card`), and badge colors (`badge-ratio`, `badge-cited`, `badge-para`).
- **Sidebar**: Moved optional case metadata inputs (Applicant Name, FIR Number, Sections, Police Station, Court Name, Custody Date, Case Facts) to the left sidebar to declutter the main search interface.

---

## [2026-07-30] Phase 2: Enhanced Metadata Extraction & Search Ranking

### Overview
Refactored the cross-citation detection mechanism to improve precision and redesigned the similarity search ranking algorithm to support a 4-pass prioritized result retrieval. Also, deduplicated the search logic by integrating both the CLI and Streamlit interfaces into a unified utility function.

### Problems Identified & Solved

#### 1. Self-Citation False Positives
- **Problem**: When a paragraph referenced the current case itself (e.g. "as observed in D.K. Basu v. West Bengal"), it was incorrectly classified as a cross-citation.
- **Fix**: Upgraded `detect_cross_citation` in [ingest.py](file:///c:/legal_ai/ingest.py) to use a regex pattern matching case titles (`X v. Y` or `A vs. B`) and filtering out any matches containing keywords from the current case title (`current_case`).
- **Result**: Self-references are correctly flagged as `is_cross_citation = False`, preserving critical holding paragraphs.

#### 2. Broad Search Exclusion of Cross-Citations
- **Problem**: Precedent-based holdings containing cross-citations were completely omitted from search results because the search logic discarded any paragraph with `is_cross_citation = True`.
- **Fix**: Redesigned the search algorithm in [search_engine.py](file:///c:/legal_ai/search_engine.py) to implement a **4-pass prioritized ranking system**:
  - *Pass 1*: Direct ratio/holdings (`para_type = RATIO` and `is_cross_citation = False`).
  - *Pass 2*: Precedent-based holdings (`para_type = RATIO` and `is_cross_citation = True`).
  - *Pass 3*: Direct guidelines/observations (`para_type = OTHER` and `is_cross_citation = False`).
  - *Pass 4*: Precedent-based guidelines/observations (`para_type = OTHER` and `is_cross_citation = True`).
  - *Pass 5 & 6*: Facts and general fallbacks.
- **Result**: Relevant citations are now returned in results rather than deleted, but are ranked lower than direct holdings.

#### 3. Search Engine Code Duplication
- **Problem**: The search ranking logic was duplicated in [search_engine.py](file:///c:/legal_ai/search_engine.py) and [streamlit_app.py](file:///c:/legal_ai/streamlit_app.py), creating code drift and double-loading embedding models in memory.
- **Fix**:
  - Extended `search_legal_query` in [search_engine.py](file:///c:/legal_ai/search_engine.py) to support a dynamic `max_results` parameter.
  - Rewrote [streamlit_app.py](file:///c:/legal_ai/streamlit_app.py) to import `search_legal_query` from [search_engine.py](file:///c:/legal_ai/search_engine.py) and remove duplicate database loading functions.

---

## [2026-07-30] Phase 1: Robust Ingestion, Paragraph Stitching & Defragmentation

### Overview
Conducted a deep audit of the text processing pipeline and implemented a robust extraction engine in [ingest.py](file:///c:/legal_ai/ingest.py) to resolve severe data-loss bugs, layout corruption, and search engine metadata bias.

### Problems Identified & Solved

#### 1. Case-Sensitive PDF Ingestion
- **Problem**: Ingestion only matched `.pdf` extensions. The file `Arnesh_Kumar_vs_State_of_Bihar_2014.pdf.PDF` (ending in `.PDF`) was completely ignored, resulting in 0 paragraphs indexed.
- **Fix**: Modified file matching to convert filenames to lowercase before extension checking (`file.lower().endswith(".pdf")`).
- **Result**: `Arnesh Kumar v. State of Bihar (2014)` is now fully ingested (20 paragraphs).

#### 2. Arbitrary Line Length Truncation
- **Problem**: Any line shorter than 30 characters was silently skipped. This discarded short sentence endings, list items, and citations, causing sentences to break in half.
- **Fix**: Removed the line-length filter completely, allowing all text lines to be processed.

#### 3. Running Header & Footer Pollution
- **Problem**: Standard running headers (e.g., `Shri D.K. Basu...`) and footers (e.g., `Indian Kanoon - http://...`) on each PDF page were captured as regular text, getting concatenated into the middle of actual legal paragraphs.
- **Fix**: Added a robust line-level filter (`is_junk_line`) utilizing keywords and dynamic case-title matching to identify and strip headers/footers before paragraph assembly.

#### 4. Cross-Citation False Positives
- **Problem**: Because headers containing names like `DK Basu vs State of W.B.` were merged into paragraphs, the citation detector marked almost all paragraphs as cross-citations (`is_cross_citation = True`). The search engine subsequently excluded these paragraphs from results, hiding the most critical holdings of the judgments.
- **Fix**: Stripping running headers at the line level removed these false citation triggers, restoring the correct `is_cross_citation` flag.

#### 5. Paragraph Stitching Across Pages
- **Problem**: Text was flushed on every page boundary, splitting continuous paragraphs in half. Paragraph divisions based solely on trailing periods (`line.endswith(".")`) failed for sentences ending with quotes (`."`), brackets (`.]`), or parentheses.
- **Fix**: 
  - Extracted all page lines into a single list first to allow continuous stitching.
  - Implemented lookahead checks in `is_paragraph_end`: if the next line starts with a lowercase letter, it is treated as a continuation of the current sentence even if the previous line ended with a dot.
  - Checked for secondary terminal indicators such as `."` or `.)`.

### Ingestion Metrics Summary

| Case Law PDF | Old Paragraph Count | New Paragraph Count | Status |
| :--- | :--- | :--- | :--- |
| `Arnesh Kumar v. State of Bihar` | 0 | 20 | **Ingested Successfully** |
| `DK Basu v. State of West Bengal` | 23 | 83 | **Defragmented & Complete** |
| `Joginder Kumar v. State of UP` | 12 | 37 | **Defragmented & Complete** |
| `Lalita Kumari v. Government of UP` | 62 | 170 | **Defragmented & Complete** |
| `Manubhai Ratilal Patel v. State of Gujarat` | 15 | 34 | **Defragmented & Complete** |
| `State of Haryana v. Bhajan Lal` | 12 | 28 | **Defragmented & Complete** |
| **Total Database Size** | **124 paragraphs** | **372 paragraphs** | **~3x Data Density Increase** |

---

## Future Prospects & Learnings

1. **PDF Text Stream Pitfalls**: Standard PDF extractors split text streams by layout lines rather than semantic flow. Always process files by grouping lines globally and stripping running headers/footers before running sentence-boundary detection.
2. **Metadata Filtering Risk**: Complete exclusion of matching parameters (e.g., discarding all paragraphs with `is_cross_citation: True`) is highly risky if the metadata can be corrupted by header artifacts. Prefer soft-penalizing or scoring rather than absolute exclusion.
