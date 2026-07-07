#!/usr/bin/env python3
"""WG5 M8 scratch RAG: chunk note by paragraphs -> embed -> top-2 cosine -> generate.
Usage: python3 rag-scratch.py <note_path> <question> [chunk_chars]
cosine() adapted from payload-hebrew-embed-test.py. Pure stdlib.
"""
import json
import sys
import urllib.request

EMBED_MODEL = "qwen3-embedding"
DAILY_TAG = "qwen3.6:27b"
API = "http://127.0.0.1:11434/api"


def post(path, payload, timeout=400):
    req = urllib.request.Request(
        f"{API}/{path}", data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(x * x for x in b) ** 0.5
    return dot / (na * nb) if na and nb else 0.0


def chunk(text, max_chars=0):
    # strip YAML frontmatter — metadata, not retrievable content
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end != -1:
            text = text[end + 5:]
    raw = [p.strip() for p in text.split("\n\n") if p.strip()]
    # attach lone headers + lead-ins ending with ":" to the following paragraph
    # so sections/lists retrieve as units
    paras = []
    for p in raw:
        if paras and "\n" not in paras[-1] and (
                paras[-1].startswith("#") or paras[-1].rstrip().endswith(":")):
            paras[-1] = paras[-1] + "\n" + p
        else:
            paras.append(p)
    if not max_chars:
        return paras
    out = []  # re-chunk finer: split long paras at ~max_chars
    for p in paras:
        while len(p) > max_chars:
            out.append(p[:max_chars])
            p = p[max_chars:]
        out.append(p)
    return [c for c in out if c.strip()]


def main():
    note_path, question = sys.argv[1], sys.argv[2]
    max_chars = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    chunks = chunk(open(note_path).read(), max_chars)
    cvecs = post("embed", {"model": EMBED_MODEL, "input": chunks})["embeddings"]
    qvec = post("embed", {"model": EMBED_MODEL, "input": [question]})["embeddings"][0]
    ranked = sorted(zip(chunks, cvecs), key=lambda cv: cosine(qvec, cv[1]), reverse=True)
    top2 = [c for c, _ in ranked[:2]]
    print("=== RETRIEVED CHUNKS ===")
    for i, c in enumerate(top2):
        print(f"--- chunk {i+1} ---\n{c[:500]}\n")
    prompt = (f"Answer the question using ONLY the context below. "
              f"Answer in the question's language.\n\nContext:\n"
              + "\n---\n".join(top2) + f"\n\nQuestion: {question}\nAnswer:")
    print("=== ANSWER ===")
    print(post("generate", {"model": DAILY_TAG, "prompt": prompt, "stream": False})["response"])


if __name__ == "__main__":
    main()
