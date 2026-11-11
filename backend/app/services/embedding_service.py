
from sentence_transformers import SentenceTransformer

# Load the model once, not for every request.
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


def generate_embeddings(texts: list[str]):
    embeddings = embedding_model.encode(
        texts,
        normalize_embeddings=True,
        convert_to_numpy=True
    )

    return embeddings


def generate_query_embedding(question: str):
    embedding = embedding_model.encode(
        [question],
        normalize_embeddings=True,
        convert_to_numpy=True
    )

    return embedding
