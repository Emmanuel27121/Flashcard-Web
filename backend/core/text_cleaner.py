def clean_text(text: str) -> str:
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    return " ".join(lines)

def chunk_text(text:str, chunk_size: int = 3):
    sentences = [s.strip() for s in text.split(". ") if s.strip()]
    chunks = []
    for i in range(0, len(sentences), chunk_size):
        chunk = ". ".join(sentences[i:i+chunk_size]).strip()
        if chunk and not chunk.endswith("."):
            chunk += "."
        chunks.append(chunk)
    return chunks
                 