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
    path = file_dict["path"]
    text = file_dict["text"]
    chunks = []

    if path.endswith(".md"):
        # A) MARKDOWN: cắt theo heading. Pattern CÓ ngoặc -> re.split giữ lại
        #    chính dòng heading trong kết quả (xem ví dụ ta vừa thử).
        parts = re.split(r'(?m)^(#{1,6} .+)$', text)
        current = parts[0].strip()        # phần text TRƯỚC heading đầu tiên (nếu có)
        i = 1
        while i < len(parts):             # duyệt theo từng CẶP: heading, body
            heading = parts[i]
            body = parts[i + 1] if i + 1 < len(parts) else ""
            section = (heading + "\n" + body).strip()   # dán heading dính vào body
            if section:
                chunks.append(section)
            i += 2                         # nhảy 2 bước vì mỗi vòng ăn 2 phần tử
        if current:
            chunks.insert(0, current)      # đặt preamble lên đầu cho đúng thứ tự

    elif path.endswith(".js"):
        # B) JAVASCRIPT: tìm VỊ TRÍ BẮT ĐẦU của mỗi hàm/route, không cắt rời chữ.
        pattern = r'(?m)^(?:(?:async\s+)?function\s+\w+|(?:const|let|var)\s+\w+\s*=\s*(?:async\s*)?\(|router\.(?:get|post|put|delete|patch)\(|app\.(?:get|post|put|delete|patch)\(|module\.exports)'
        boundaries = [m.start() for m in re.finditer(pattern, text)]  # các mốc cắt

        if boundaries:
            if boundaries[0] > 0:                       # có code đứng trước hàm đầu tiên?
                preamble = text[:boundaries[0]].strip() # = phần import/biến top-level
                if preamble:
                    chunks.append(preamble)
            for idx, start in enumerate(boundaries):
                # mỗi chunk chạy từ mốc này đến mốc kế tiếp (hoặc hết file)
                end = boundaries[idx + 1] if idx + 1 < len(boundaries) else len(text)
                chunk = text[start:end].strip()
                if chunk:
                    chunks.append(chunk)
        else:
            chunks.append(text)            # file JS không khớp ranh giới nào -> để nguyên
    else:
        chunks.append(text)                # loại file khác -> 1 chunk, để fallback lo

    # C) FALLBACK: chunk nào QUÁ DÀI thì cắt cứng theo số ký tự,
    #    để không bao giờ lọt 1 chunk khổng lồ làm hỏng bước embedding.
    final_chunks = []
    for chunk in chunks:
        if len(chunk) > FALLBACK_CHUNK_SIZE * 2:        # ngưỡng: dài gấp đôi mới cắt
            for i in range(0, len(chunk), FALLBACK_CHUNK_SIZE):
                piece = chunk[i:i + FALLBACK_CHUNK_SIZE].strip()
                if piece:
                    final_chunks.append(piece)
        else:
            final_chunks.append(chunk)

    # đánh chunk_id chạy từ 0 cho mỗi file
    return [
        {"path": path, "chunk_id": i, "content": c}
        for i, c in enumerate(final_chunks)
    ]


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
    dot_product = np.dot(vec_a, vec_b)
    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot_product / (norm_a * norm_b)


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
    scored = []                                          # nơi chứa chunk đã chấm điểm
    for i in range(len(index["chunks"])):               # duyệt TỪNG chunk trong kho
        # vector chunk thứ i nằm ở dòng i của ma trận embeddings (khớp chỉ số)
        score = cosine_similarity(query_embedding, index["embeddings"][i])
        chunk_copy = dict(index["chunks"][i])           # SAO CHÉP, không sửa index gốc
        chunk_copy["score"] = float(score)              # ép về float Python thường
        scored.append(chunk_copy)

    scored.sort(key=lambda x: x["score"], reverse=True)  # giống nhất lên đầu
    return scored[:k]                                    # lấy K chunk điểm cao nhất



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
    # B1: ghép từng chunk thành 1 khối context, MỖI chunk dán nhãn nguồn
    context_parts = []
    for c in retrieved_chunks:
        context_parts.append(
            # nhãn file + chunk_id + điểm -> để TRUY VẾT model dùng đoạn nào
            f"--- File: {c['path']} | Chunk {c['chunk_id']} | Relevance: {c['score']:.3f} ---\n"
            f"{c['content']}\n"
        )
    context_text = "\n".join(context_parts)   # nối các chunk, cách nhau 1 dòng trống

    # B2: khung prompt. Phần "NGUYÊN TẮC" chính là rào chắn chống bịa.
    prompt = f"""Bạn là trợ lý chuyên phân tích codebase. Trả lời câu hỏi DUY NHẤT dựa trên context bên dưới.

NGUYÊN TẮC BẮT BUỘC:
1. Chỉ dùng thông tin từ context. KHÔNG bịa thêm code, hàm, hoặc logic không có trong context.
2. Nếu context không chứa thông tin liên quan, trả lời: "Tôi không tìm thấy thông tin này trong các đoạn code/tài liệu được cung cấp."
3. Khi trích dẫn, ghi rõ file và chunk number.

CONTEXT:
{context_text}

CÂU HỎI: {question}

TRẢ LỜI:"""
    return prompt



# -------------------------------------------------------------------
# STEP 7: CALL GEMINI (fully implemented - API plumbing, not the
# learning focus of this exercise)
# -------------------------------------------------------------------
def call_gemini(prompt):
    from google import genai

    # Hai backend, CÙNG một SDK — chỉ phần khởi tạo Client đổi (config-swap, xem architect A8).
    # Lật qua lại bằng env var, không hardcode. Phần generate_content bên dưới GIỮ NGUYÊN.
    if os.environ.get("GOOGLE_GENAI_USE_VERTEXAI"):
        # Vertex AI (paid GCP): SDK tự đọc GOOGLE_CLOUD_PROJECT + GOOGLE_CLOUD_LOCATION từ env;
        # xác thực bằng ADC (chạy 1 lần: gcloud auth application-default login). KHÔNG cần api key.
        client = genai.Client()
    else:
        # AI Studio (free tier 20 req/ngày): cần GEMINI_API_KEY.
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "Chưa set backend LLM. Vertex: set GOOGLE_GENAI_USE_VERTEXAI=True "
                "+ GOOGLE_CLOUD_PROJECT + GOOGLE_CLOUD_LOCATION (đã gcloud auth). "
                "Hoặc AI Studio: set GEMINI_API_KEY."
            )
        client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",   # rẻ cho vòng lặp; đổi 1 dòng khi cần model mạnh hơn
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
