
def split_text(text, page_number, chunk_size=150, overlap=30):
    words = text.split()
    chunks = []

    start = 0

    while start < len(words):
        end = start + chunk_size

        chunk_text = " ".join(words[start:end])

        if chunk_text.strip():
            chunks.append({
                "text": chunk_text,
                "page": page_number
            })

        if end >= len(words):
            break

        start = end - overlap

    return chunks
