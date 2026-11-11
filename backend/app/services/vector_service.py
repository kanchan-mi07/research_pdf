
import faiss
import json
import os
import re
import numpy as np

from app.services.embedding_service import generate_embeddings

VECTOR_STORE = "vector_store"


def get_document_path(document_id):
    # Prevent unsafe document IDs from becoming filesystem paths.
    if not re.fullmatch(r"[a-zA-Z0-9_-]+", document_id):
        raise ValueError("Invalid document ID")

    return os.path.join(VECTOR_STORE, document_id)


def save_document_vectors(document_id, chunks):
    if not chunks:
        raise ValueError("No text chunks found in the PDF")

    os.makedirs(get_document_path(document_id), exist_ok=True)

    texts = [chunk["text"] for chunk in chunks]

    embeddings = generate_embeddings(texts)

    embeddings = np.asarray(embeddings, dtype="float32")

    # Inner product on normalized embeddings gives cosine similarity.
    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)

    path = get_document_path(document_id)

    faiss.write_index(
        index,
        os.path.join(path, "index.faiss")
    )

    with open(
        os.path.join(path, "chunks.json"),
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(chunks, file, ensure_ascii=False, indent=4)


def search_document(document_id, question, top_k=4):
    path = get_document_path(document_id)

    index_path = os.path.join(path, "index.faiss")
    chunks_path = os.path.join(path, "chunks.json")

    if not os.path.exists(index_path) or not os.path.exists(chunks_path):
        raise FileNotFoundError("Document index not found. Upload the PDF again.")

    index = faiss.read_index(index_path)

    with open(chunks_path, "r", encoding="utf-8") as file:
        chunks = json.load(file)

    from app.services.embedding_service import generate_query_embedding

    query_embedding = generate_query_embedding(question)
    query_embedding = np.asarray(query_embedding, dtype="float32")

    k = min(top_k, index.ntotal)

    scores, indices = index.search(query_embedding, k)

    results = []

    for score, idx in zip(scores[0], indices[0]):
        if idx == -1:
            continue

        result = chunks[int(idx)].copy()
        result["score"] = float(score)

        results.append(result)

    return results
