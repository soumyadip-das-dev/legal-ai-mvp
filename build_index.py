import json
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document

DATA_PATH = "data/processed/judgments.json"
INDEX_PATH = "data/faiss_index"

with open(DATA_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

documents = []

for item in data:
    doc = Document(
        page_content=item["text"],
        metadata={
            "case_title": item["case_title"],
            "court": item["court"],
            "year": item["year"],
            "paragraph": item["paragraph"],
            "para_type": item["para_type"],
            "is_cross_citation": item["is_cross_citation"]
            }
    )
    documents.append(doc)

print(f"Loaded {len(documents)} documents for embedding...")

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

db = FAISS.from_documents(documents, embeddings)
db.save_local(INDEX_PATH)

print("FAISS index built successfully using FREE local embeddings.")
