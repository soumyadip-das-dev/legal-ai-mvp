# Legal AI Assistant — Future Roadmap & Student Project Enhancements

This document outlines planned future enhancements and architectural upgrades for the **Legal Research Assistant** project.

---

## 📌 Phase 4: Future Enhancements Roadmap

### 1. True RAG with LLM Synthesis
- Integrate a local LLM (Ollama with Llama 3 / Mistral) or cloud API (Gemini / Groq).
- Replace template string generation with LLM-synthesized legal research notes containing exact inline pin-point citations (e.g., `[DK Basu v. State of WB, ¶57]`).
- Add multi-lingual legal query translation (Hindi, Bengali, Tamil, etc.).

### 2. Hybrid Search (FAISS Dense + BM25 Sparse Search)
- Combine dense vector embeddings (`sentence-transformers/all-MiniLM-L6-v2`) with sparse keyword retrieval (**Rank-BM25**).
- Merge result rankings using **Reciprocal Rank Fusion (RRF)** to optimize for both semantic context and exact statutory references (e.g., "Section 438 CrPC").

### 3. Cross-Encoder Re-Ranking Stage
- Implement a 2-stage retrieval pipeline:
  1. Candidate Retrieval: Fetch Top-20 candidates using FAISS + BM25.
  2. Re-Ranking: Score candidates using `cross-encoder/ms-marco-MiniLM-L-6-v2` to boost top-K accuracy.

### 4. System Evaluation & Benchmarking (RAGAS)
- Build an automated evaluation suite using **RAGAS** / **Trulens** to measure:
  - *Context Precision* & *Context Recall*
  - *Faithfulness* (Hallucination detection)
  - *Answer Relevance*

### 5. Production Engineering & MLOps
- Decouple app into a **FastAPI** backend microservice and **Streamlit** UI frontend.
- Containerize using `Dockerfile` and `docker-compose`.
- Upgrade vector storage to persistent database engine (**Qdrant** / **ChromaDB**).
