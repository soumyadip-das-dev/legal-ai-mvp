from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

INDEX_PATH = "data/faiss_index"

# Load embeddings (same model as indexing)
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Load FAISS index
db = FAISS.load_local(
    INDEX_PATH,
    embeddings,
    allow_dangerous_deserialization=True
)

def search_legal_query(query, k=15, max_results=5):
    results = db.similarity_search(query, k=k)

    seen_cases = set()
    ranked_results = []

    def add_matches(filter_fn):
        for doc in results:
            if len(ranked_results) >= max_results:
                break
            meta = doc.metadata
            case_key = meta.get("case_title")
            if case_key not in seen_cases and filter_fn(meta):
                ranked_results.append(doc)
                seen_cases.add(case_key)

    # Pass 1: RATIO and not cross-citation (direct holdings)
    add_matches(lambda m: m.get("para_type") == "RATIO" and not m.get("is_cross_citation", False))

    # Pass 2: RATIO and cross-citation (holdings with precedents)
    add_matches(lambda m: m.get("para_type") == "RATIO" and m.get("is_cross_citation", False))

    # Pass 3: OTHER and not cross-citation (direct observations / guidelines)
    add_matches(lambda m: m.get("para_type") == "OTHER" and not m.get("is_cross_citation", False))

    # Pass 4: OTHER and cross-citation (observations with precedents)
    add_matches(lambda m: m.get("para_type") == "OTHER" and m.get("is_cross_citation", False))

    # Pass 5: FACTS fallback
    add_matches(lambda m: m.get("para_type") == "FACTS")

    # Pass 6: Ultimate fallback
    add_matches(lambda m: True)

    formatted_results = []

    for doc in ranked_results:
        meta = doc.metadata
        formatted_results.append({
            "case_title": meta.get("case_title"),
            "court": meta.get("court"),
            "year": meta.get("year"),
            "paragraph": meta.get("paragraph"),
            "para_type": meta.get("para_type"),
            "is_cross_citation": meta.get("is_cross_citation", False),
            "text": doc.page_content
        })

    return formatted_results



if __name__ == "__main__":
    query = input("Enter legal query: ")
    results = search_legal_query(query)

    print("\n=== SEARCH RESULTS ===\n")

    for i, r in enumerate(results, 1):
        print(f"{i}. {r['case_title']} ({r['year']})")
        print(f"   Court: {r['court']}")
        print(f"   Type: {r['para_type']}")
        print(f"   Cross-citation: {r.get('is_cross_citation', False)}")
        print(f"   Paragraph {r['paragraph']}")
        print(f"   {r['text']}\n")



