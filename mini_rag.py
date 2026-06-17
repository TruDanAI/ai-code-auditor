"""
mini_rag.py - Manual RAG pipeline (no framework) for exploring the
chatbot-fanpage codebase.

GOAL: build each RAG step yourself so you can EXPLAIN how it works,
not just import a function that does it for you.

PIPELINE
1. Load files from a folder (code + markdown docs)           -- done for you
2. Chunk each file into meaningful pieces                     -- TODO (Day 4)
3. Embed each chunk (sentence-transformers, local, free)      -- done for you
4. Store chunks + embeddings in memory ("vector DB" = a list)  -- done for you
5. On a question: embed it, compute cosine similarity by hand -- TODO (Day 3)
   against every chunk, take top-K                             -- TODO
6. Build a prompt from question + top-K chunks                -- TODO (Day 7)
7. Send prompt to Gemini, print the answer                     -- done for you

SETUP
    pip install sentence-transformers google-genai numpy
    export GEMINI_API_KEY=your_key_here

RUN
    python mini_rag.py /path/to/chatbot-fanpage

HOW TO WORK THROUGH THIS FILE
    Implement the TODOs ONE AT A TIME, in this order:
        chunk_text -> cosine_similarity -> retrieve_top_k -> build_prompt
    After each one, add a small test in the `if __name__ == "__main__":`
    block at the bottom (there's a TEST MODE section) to check just
    that piece before moving to the next. Don't write all four blind
    and then debug everything at once.
"""

import os
import sys
import re
import numpy as np


# -------------------------------------------------------------------
# CONFIG
# -------------------------------------------------------------------
SOURCE_EXTENSIONS = [".js", ".md"]            # which files to index
IGNORE_DIRS = {"node_modules", ".git", "shops", "test", "tests"}  # skip noisy dirs
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"     # small, fast, runs on CPU, free
TOP_K = 3
FALLBACK_CHUNK_SIZE = 800                     # chars, used when no boundary found


# -------------------------------------------------------------------
# STEP 1: LOAD FILES  (fully implemented - this is plumbing, not the
# core RAG concept. Read it once so you know the shape of the data
# going into step 2.)
# -------------------------------------------------------------------
def load_files(root_dir):
    """
    Walk root_dir and return a list of dicts:
        {"path": "relative/or/abs/path", "text": "<file contents>"}
    for every file whose extension is in SOURCE_EXTENSIONS, skipping
    directories listed in IGNORE_DIRS.
    """
    files = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
        for fname in filenames:
            if any(fname.endswith(ext) for ext in SOURCE_EXTENSIONS):
                full_path = os.path.join(dirpath, fname)
                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        text = f.read()
                except (UnicodeDecodeError, OSError):
                    continue
                if text.strip():
                    files.append({"path": full_path, "text": text})
    return files


# -------------------------------------------------------------------
# STEP 2: CHUNKING  <-- TODO (Day 4 concept applies here)
# -------------------------------------------------------------------
def chunk_text(file_dict):
    """
    Input:  {"path": "...", "text": "..."}
    Output: list of dicts, each:
        {"path": "...", "chunk_id": int, "content": "..."}

    TODO - implement chunking. Two strategies depending on file type
    (use file_dict["path"] to decide):

    A) For .md files: split on markdown headings.
       - Use re.split with a pattern that matches lines starting with
         one or more '#' characters, e.g. r'(?m)^(#{1,6} .*)$'
       - Keep the heading attached to the section that follows it
         (so the chunk has context about what it's describing).

    B) For .js files: split on top-level declarations.
       - Use re.split or re.finditer with a pattern that matches the
         START of a function/route/handler, e.g. something matching
         lines like 'function foo(', 'const foo = (', 'router.get(',
         'app.post(', 'module.exports'.
       - Each match starts a new chunk; everything up to the next
         match belongs to the current chunk.

    C) FALLBACK (for anything A/B didn't split, or files where no
       boundary matched at all): split the remaining text into pieces
       of FALLBACK_CHUNK_SIZE characters. This guarantees you never
       end up with one giant chunk that breaks the embedding step.

    Assign chunk_id sequentially starting from 0 for each file.

    WHILE DEVELOPING: print(len(chunk["content"])) for every chunk you
    produce on a couple of real files (e.g. core/webhook.js and
    DESIGN.md). Ask yourself: does each chunk look like a sensible,
    self-contained "unit" a human would also use to answer a question?
    If chunks are cutting a function in half, your regex boundary is
    wrong - fix it before moving on.
    """
    raise NotImplementedError("Implement chunking strategy here")


# -------------------------------------------------------------------
# STEP 3: EMBEDDING MODEL (fully implemented - setup only, the
# interesting part is what you DO with the vectors in step 5)
# -------------------------------------------------------------------
def load_embedding_model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(EMBEDDING_MODEL_NAME)


def embed_texts(model, texts):
    """
    Input:  list of strings, length n
    Output: numpy array, shape (n, embedding_dim)
    """
    return model.encode(texts, convert_to_numpy=True, show_progress_bar=False)


# -------------------------------------------------------------------
# STEP 4: BUILD INDEX ("vector DB" = a dict holding a list + an array)
# Fully implemented IF chunk_text() works - this just wires 1-3 together.
# -------------------------------------------------------------------
def build_index(root_dir, model):
    files = load_files(root_dir)
    if not files:
        raise ValueError(f"No files found under {root_dir} with extensions {SOURCE_EXTENSIONS}")

    all_chunks = []
    for f in files:
        all_chunks.extend(chunk_text(f))

    if not all_chunks:
        raise ValueError("No chunks produced - check chunk_text()")

    texts = [c["content"] for c in all_chunks]
    embeddings = embed_texts(model, texts)

    return {"chunks": all_chunks, "embeddings": embeddings}


# -------------------------------------------------------------------
# STEP 5: COSINE SIMILARITY + RETRIEVAL  <-- TODO (Day 3 concept here)
# -------------------------------------------------------------------
def cosine_similarity(vec_a, vec_b):
    """
    Input:  two 1D numpy vectors of the same length
    Output: a single float, normally between -1 and 1

    TODO - implement BY HAND. Do not call a library function that
    computes cosine similarity directly (np.dot and np.linalg.norm
    are fine to use as building blocks).

    Formula:
        cos(theta) = (A . B) / (||A|| * ||B||)

    where:
        A . B  = dot product            -> np.dot(vec_a, vec_b)
        ||A||  = L2 norm (length) of A  -> np.linalg.norm(vec_a)
        ||B||  = L2 norm (length) of B  -> np.linalg.norm(vec_b)

    Guard against division by zero (return 0.0 if either norm is 0).
    """
    raise NotImplementedError("Implement cosine similarity by hand")


def retrieve_top_k(query_embedding, index, k=TOP_K):
    """
    Input:  query_embedding (1D numpy vector), index (from build_index)
    Output: list of k chunk dicts, sorted by similarity descending,
            each with an added "score" key (float).

    TODO:
      1. For i in range(len(index["chunks"])):
             score = cosine_similarity(query_embedding, index["embeddings"][i])
             attach this score to a COPY of index["chunks"][i]
      2. Sort all scored chunks by "score", descending.
      3. Return the first k.

    NOTE ON SCALE: this is brute-force O(n) - you compare the query
    against every single chunk. Fine for a few hundred chunks (this
    project). A real vector DB (pgvector, Chroma, Pinecone) uses
    approximate nearest-neighbor indexes (e.g. HNSW) to avoid this
    full scan at millions of vectors. You don't need to implement
    that - just be ready to explain WHY it exists and what tradeoff
    it makes (speed vs. exactness).
    """
    raise NotImplementedError("Implement top-k retrieval")


# -------------------------------------------------------------------
# STEP 6: PROMPT ASSEMBLY  <-- TODO (Day 7 hallucination guardrail here)
# -------------------------------------------------------------------
def build_prompt(question, retrieved_chunks):
    """
    Input:  question (str), retrieved_chunks (list from retrieve_top_k)
    Output: a single string - the full prompt to send to Gemini

    TODO - the prompt should:
      1. State the model's role: it answers questions about THIS
         specific codebase, using ONLY the context provided below.
      2. Explicitly instruct: if the answer is not contained in the
         context, say so clearly instead of guessing. This is your
         hallucination guardrail from Day 7 - test it deliberately
         with an off-topic question.
      3. Include each retrieved chunk, labeled with its file path
         and chunk_id, so you can later verify which chunk the model
         actually used.
      4. End with the user's question, clearly marked.

    DEBUG TIP: the first few times you run this, print(prompt) in
    full before sending it to Gemini. Reading the EXACT text the
    model receives is the fastest way to debug "why did it answer
    that?" - a skill you'll use constantly in real LLM app work.
    """
    raise NotImplementedError("Implement prompt assembly")


# -------------------------------------------------------------------
# STEP 7: CALL GEMINI (fully implemented - API plumbing, not the
# learning focus of this exercise)
# -------------------------------------------------------------------
def call_gemini(prompt):
    from google import genai

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("Set the GEMINI_API_KEY environment variable first")

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt
    )
    return response.text


# -------------------------------------------------------------------
# MAIN: interactive loop
# -------------------------------------------------------------------
def main():
    if len(sys.argv) < 2:
        print("Usage: python mini_rag.py /path/to/chatbot-fanpage")
        sys.exit(1)

    root_dir = sys.argv[1]

    print("Loading embedding model (first run downloads ~80MB)...")
    model = load_embedding_model()

    print(f"Indexing files under {root_dir} ...")
    index = build_index(root_dir, model)
    print(f"Indexed {len(index['chunks'])} chunks from "
          f"{len({c['path'] for c in index['chunks']})} files.")

    while True:
        question = input("\nQuestion (or 'quit'): ").strip()
        if question.lower() in ("quit", "exit", ""):
            break

        query_embedding = embed_texts(model, [question])[0]
        top_chunks = retrieve_top_k(query_embedding, index)

        print("\n--- Retrieved chunks ---")
        for c in top_chunks:
            print(f"  [{c['score']:.3f}] {c['path']} (chunk {c['chunk_id']})")

        prompt = build_prompt(question, top_chunks)
        answer = call_gemini(prompt)

        print("\n--- Answer ---")
        print(answer)


if __name__ == "__main__":
    main()
