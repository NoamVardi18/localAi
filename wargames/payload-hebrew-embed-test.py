#!/usr/bin/env python3
"""Hebrew+English retrieval smoke test for a local Ollama embedding model.

Usage:
  python3 payload-hebrew-embed-test.py <model>            # live test against localhost:11434
  python3 payload-hebrew-embed-test.py --selftest         # offline math check, no server needed

Scores a model by whether each query's TOP-1 retrieved document is the correct one.
PASS bar (per wargame 00-localai-stack.md M7): >= 5/6 queries correct.
Pure stdlib — no pip installs.
"""
import json
import sys
import urllib.request

OLLAMA = "http://127.0.0.1:11434/api/embed"

# 6 documents: 3 Hebrew, 2 English, 1 mixed — mimics Noam's vault reality.
DOCS = {
    "heb-army": "הצבא מסתיים באמצע דצמבר 2026. אחרי השחרור אני מתכנן לנסוע לחו\"ל ואז להתחיל לעבוד כמפתח פול סטאק.",
    "heb-cook": "מתכון לשקשוקה: מטגנים בצל ושום, מוסיפים עגבניות מרוסקות ופפריקה, מבשלים רבע שעה ושוברים ביצים פנימה.",
    "heb-money": "תקציב חודשי: שכר דירה 4500 שקל, אוכל 2000, תחבורה 400. המטרה לחסוך אלפיים שקל כל חודש.",
    "eng-rag": "Retrieval-augmented generation grounds a language model's answers in documents fetched from a vector index at query time.",
    "eng-gpu": "Apple Silicon uses unified memory, so the GPU can address the same RAM as the CPU without copying tensors.",
    "mix-vault": "ה-vault שלי ב-Obsidian מסונכרן עם git. כל note מקבל frontmatter עם categories ו-topics.",
}

# Each query names its one correct document.
QUERIES = {
    "מתי אני משתחרר מהצבא ומה התוכנית אחרי?": "heb-army",
    "איך מכינים שקשוקה?": "heb-cook",
    "כמה אני רוצה לחסוך בחודש?": "heb-money",
    "How does RAG ground model answers?": "eng-rag",
    "Why doesn't Apple Silicon need to copy tensors to the GPU?": "eng-gpu",
    "איך הפתקים שלי מסונכרנים ומה יש בכל note?": "mix-vault",
}


def embed(model, texts):
    req = urllib.request.Request(
        OLLAMA,
        data=json.dumps({"model": model, "input": texts}).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.load(r)["embeddings"]


def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(x * x for x in b) ** 0.5
    return dot / (na * nb) if na and nb else 0.0


def run(doc_vecs, query_vecs):
    """doc_vecs: {doc_id: vec}, query_vecs: {query: vec}. Returns (hits, total, rows)."""
    hits, rows = 0, []
    for q, want in QUERIES.items():
        ranked = sorted(doc_vecs, key=lambda d: cosine(query_vecs[q], doc_vecs[d]), reverse=True)
        got = ranked[0]
        ok = got == want
        hits += ok
        rows.append(f"  {'PASS' if ok else 'FAIL'}  want={want:<9} got={got:<9} q={q[:40]}")
    return hits, len(QUERIES), rows


def selftest():
    # Synthetic orthogonal-ish vectors: each doc gets a distinct axis; each query
    # points mostly at its correct doc's axis with noise on the others.
    ids = list(DOCS)
    doc_vecs = {d: [1.0 if i == n else 0.05 for i in range(len(ids))] for n, d in enumerate(ids)}
    query_vecs = {}
    for q, want in QUERIES.items():
        n = ids.index(want)
        query_vecs[q] = [0.9 if i == n else 0.1 for i in range(len(ids))]
    hits, total, rows = run(doc_vecs, query_vecs)
    print("\n".join(rows))
    assert hits == total, f"selftest broken: {hits}/{total}"
    print(f"SELFTEST OK {hits}/{total} — ranking math verified")


def main():
    if sys.argv[1:] == ["--selftest"]:
        return selftest()
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    model = sys.argv[1]
    ids = list(DOCS)
    dv = embed(model, [DOCS[d] for d in ids])
    qv = embed(model, list(QUERIES))
    doc_vecs = dict(zip(ids, dv))
    query_vecs = dict(zip(QUERIES, qv))
    hits, total, rows = run(doc_vecs, query_vecs)
    print("\n".join(rows))
    print(f"RESULT {model}: {hits}/{total} top-1 correct ({'PASS' if hits >= 5 else 'FAIL'}, bar is 5/6)")


if __name__ == "__main__":
    main()
