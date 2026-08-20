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

# Thêm cạnh FALLBACK_CHUNK_SIZE (phần CONFIG):
MERGE_TARGET_SIZE = 600        # Ngày 12: gộp chunk ngữ nghĩa liền kề tới ~ngưỡng này

# Thêm hàm mới (đặt ngay trên chunk_text):
def _merge_small_chunks(chunks, target=MERGE_TARGET_SIZE):
    """Tầng 2: GỘP các chunk liền kề bị vụn. Input/Output: list[str]."""
    merged = []
    buf = ""                                     # "rổ" đang gom
    for c in chunks:
        if not buf:
            buf = c                              # rổ rỗng -> đặt mảnh đầu
        elif len(buf) + len(c) + 1 <= target:    # +1 cho ký tự '\n' nối
            buf = buf + "\n" + c                 # còn chỗ -> dồn NGUYÊN mảnh
        else:
            merged.append(buf)                   # rổ đầy -> chốt, mở rổ mới
            buf = c
    if buf:
        merged.append(buf)                       # đừng quên rổ cuối
    return merged

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
        pattern = r'(?m)^[ \t]*(?:(?:async\s+)?function\s+\w+|(?:const|let|var)\s+\w+\s*=\s*(?:async\s*)?\(|router\.(?:get|post|put|delete|patch)\(|app\.(?:get|post|put|delete|patch)\(|module\.exports)'
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

    # TẦNG 2 (Ngày 12): gộp chunk vụn TRƯỚC khi fallback xét độ dài
    chunks = _merge_small_chunks(chunks)

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

    # Ngày 14: nhãn 'type' suy TỪ ĐUÔI FILE (không hardcode!) — .md=doc, còn lại=code.
    # Đặt ở đây (chỗ khai sinh chunk) -> mọi consumer (build_index, bm25,
    # chroma_rag import chunk_text, test) TỰ thừa hưởng -> một nguồn sự thật.
    chunk_type = "doc" if path.endswith(".md") else "code"

    # đánh chunk_id chạy từ 0 cho mỗi file
    return [
        {"path": path, "chunk_id": i, "content": c, "type": chunk_type}
        for i, c in enumerate(final_chunks)
    ]


# -------------------------------------------------------------------
# STEP 3: EMBEDDING MODEL (fully implemented - setup only, the
# interesting part is what you DO with the vectors in step 5)
# -------------------------------------------------------------------
def load_embedding_model(model_name=EMBEDDING_MODEL_NAME, device=None):
    # Ngày 10: thêm tham số model_name (mặc định = MiniLM) để swap "bộ não"
    # embedding mà KHÔNG sửa logic. eval_set.py truyền tên model vào đây.
    # Ngày 11 (GPU 4GB): thêm device — None = tự chọn (cuda nếu có), "cpu" = ép CPU
    # để nhường VRAM cho reranker khi chạy 2 model cùng lúc.
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(model_name, device=device)


def embed_texts(model, texts):
    """
    Input:  list of strings, length n
    Output: numpy array, shape (n, embedding_dim)
    """
    # Ngày 10: bật thanh tiến trình — embed model nặng (Qwen3 decoder, CPU) lâu,
    # không có tín hiệu sống thì tưởng treo. Tác vụ dài PHẢI hiện tiến độ.
    return model.encode(texts, convert_to_numpy=True, show_progress_bar=True)


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

def rrf_fuse(list_a, list_b, k=60):
    """
    list_a, list_b: mỗi cái là list các KEY chunk ĐÃ XẾP HẠNG
        (phần tử [0] = hạng 1). key = thứ nhận diện 1 chunk, vd (path, chunk_id).
    Trả về: list key xếp lại theo điểm RRF giảm dần.

    Công thức:  RRF(key) = Σ_qua_các_list  1/(k + rank_trong_list)
        - rank đếm TỪ 1 (hạng 1, 2, 3...), KHÔNG từ 0.
        - key có ở cả 2 list -> CỘNG DỒN cả 2 phần.
        - key chỉ ở 1 list -> vẫn tính (chỉ cộng 1 phần).
    """
    scores = {}                                # cuốn sổ: key -> điểm RRF cộng dồn
    # MẸO: gói 2 list vào 1 tuple rồi lặp -> KHỎI viết 2 lần thân vòng lặp.
    #      Chính vì cùng dùng 1 dict 'scores' mà key ở cả 2 list được cộng dồn tự nhiên.
    for ranked_list in (list_a, list_b):
        # enumerate(..., start=1): trả (1, key_đầu), (2, key_kế)... -> rank đếm TỪ 1.
        for rank, key in enumerate(ranked_list, start=1):
            # .get(key, 0.0): nếu key CHƯA có trong sổ thì coi như 0 rồi cộng
            #                 -> đây chính là "dict khởi tạo 0" mà không cần khai báo trước.
            scores[key] = scores.get(key, 0.0) + 1.0 / (k + rank)

    # Sắp các key theo điểm giảm dần. key=lambda... bảo sorted "so theo điểm trong sổ".
    fused = sorted(scores.keys(), key=lambda key: scores[key], reverse=True)
    return fused


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
# STEP 5b (Ngày 13): HYBRID — kênh keyword BM25 (bù khuyết cho dense)
# Dense embedding mù với token hiếm/định danh (tên hàm, ID, aes-256-gcm).
# BM25 chấm theo khớp mặt chữ + độ hiếm (IDF) -> kéo thẳng chunk chứa đúng
# 'verifySignature' lên. Hai kênh trộn bằng rrf_fuse() ở trên (chỉ dùng thứ hạng).
# -------------------------------------------------------------------
def tokenize_for_bm25(text):
    r"""Tách token thô cho BM25: chữ thường + cắt theo \w+.
    \w trong Python 3 mặc định Unicode -> token tiếng Việt CÓ DẤU vẫn giữ nguyên.
    ĐÁNH ĐỔI cần đo: camelCase 'verifySignature' -> 1 token 'verifysignature'.
       Query 'verifySignature' khớp; nhưng 'verify signature' (2 từ rời) thì KHÔNG.
       -> đo trên golden set rồi mới quyết có tách camelCase hay không."""
    return re.findall(r"\w+", text.lower())


def build_bm25(chunks):
    """Dựng BM25 trên CHÍNH list chunk của index (không re-chunk, không copy).
    get_scores() sau này trả mảng điểm KHỚP CHỈ SỐ 'chunks' (chunk i <-> điểm i)."""
    from rank_bm25 import BM25Okapi      # import cục bộ: file vẫn import được nếu chưa cài lib
    corpus = [tokenize_for_bm25(c["content"]) for c in chunks]
    return BM25Okapi(corpus)


def bm25_search(bm25, chunks, question, k=TOP_K):
    """Trả top-k chunk theo điểm BM25, đã xếp hạng. Mỗi chunk là BẢN SAO + 'bm25_score'.
    'chunks' PHẢI là đúng list đã dựng bm25 (chỉ số phải khớp tuyệt đối)."""
    scores = bm25.get_scores(tokenize_for_bm25(question))   # mảng điểm, khớp chỉ số chunks
    top_idx = np.argsort(scores)[::-1][:k]                  # argsort tăng dần -> đảo -> lấy top-k
    results = []
    for i in top_idx:
        c = dict(chunks[int(i)])                            # SAO CHÉP, không sửa index gốc
        c["bm25_score"] = float(scores[i])
        results.append(c)
    return results


def load_reranker(model_name="BAAI/bge-reranker-v2-m3", device=None):
    """Tải cross-encoder MỘT lần rồi tái dùng (giống load_embedding_model).
    Tách riêng để KHÔNG tải lại 600MB mỗi câu hỏi.
    device: None = tự chọn (cuda nếu có) — reranker là nút thắt tốc độ nên ưu tiên GPU."""
    from sentence_transformers import CrossEncoder
    return CrossEncoder(model_name, device=device)


def rerank(reranker, question, candidates, top_k=TOP_K):
    """
    candidates = output của retrieve_top_k với k=N LỚN (50/150) — đã có 'content'.
    Trả về top_k chunk, xếp lại theo điểm cross-encoder.

    TODO bạn điền (4 bước):
      1. pairs = list các CẶP (question, c["content"]) cho từng candidate.
      2. scores = reranker.predict(pairs)         # numpy array, 1 điểm/cặp
      3. gắn float(score) vào BẢN SAO mỗi chunk, key MỚI 'rerank_score'
         (ĐỪNG đè 'score' cũ — giữ lại để so bi-encoder vs cross-encoder).
      4. sort theo 'rerank_score' giảm dần, return top_k.
    """
    # B1: dựng các CẶP (question, content). predict ăn cặp, KHÔNG ăn vector.
    pairs = [(question, c["content"]) for c in candidates]

    # B2: 1 forward/cặp -> mảng điểm liên quan (logit, càng cao càng hợp).
    #     Thứ tự scores KHỚP thứ tự pairs -> zip lại là gắn đúng chunk.
    scores = reranker.predict(pairs)

    # B3: gắn điểm vào BẢN SAO mỗi chunk (dict(c)) -> KHÔNG đụng list/đict gốc
    #     của caller. Giữ luôn key 'score' cũ (cosine bi-encoder) để còn so sánh.
    scored = [
        {**dict(c), "rerank_score": float(s)}
        for c, s in zip(candidates, scores)
    ]

    # B4: .sort() tại chỗ Ở ĐÂY an toàn vì 'scored' ĐÃ là list mới của riêng hàm
    #     (caller không cầm tham chiếu tới nó) -> list gốc 'candidates' nguyên vẹn.
    scored.sort(key=lambda x: x["rerank_score"], reverse=True)
    return scored[:top_k]


# -------------------------------------------------------------------
# STEP 5c (Ngày 14): CHẶN DISTRACTOR DOC bằng nhãn 'type'
# Reranker coi code/doc như nhau -> bị prose .md "nói VỀ" đánh lừa (Ngày 12-13).
# CHÍNH TA áp cấu trúc: phạt điểm chunk doc để chunk code thắng sát nút vượt lên.
# -------------------------------------------------------------------
def soft_boost_by_type(reranked, lam=0.0, top_k=TOP_K, penalize="doc"):
    """SOFT filter: TRỪ λ vào rerank_score của chunk type==penalize, rồi xếp lại.

    reranked : output rerank() chấm TOÀN RỔ (chưa cắt top_k) — mỗi chunk có
               'rerank_score' + 'type'. Phải chấm cả rổ TRƯỚC khi phạt, nếu không
               chunk code bị cắt mất trước khi kịp vượt lên (xem ghi chú Ngày 14).
    lam      : λ, CÙNG ĐƠN VỊ với rerank_score (logit, KHÔNG phải %). λ=0 -> y hệt
               xếp hạng rerank gốc (chốt chặn sanity). λ lớn -> tiến dần về hard-filter.
    KHÔNG mutate: mỗi chunk là bản sao + key mới 'boosted_score'.
    """
    boosted = []
    for c in reranked:
        pen = lam if c.get("type") == penalize else 0.0   # chỉ doc bị trừ, code trừ 0
        boosted.append({**dict(c), "boosted_score": c["rerank_score"] - pen})
    boosted.sort(key=lambda x: x["boosted_score"], reverse=True)
    return boosted[:top_k]


def hard_filter_type(candidates, keep="code"):
    """HARD filter (chỉ để ABLATION): vứt sạch chunk type != keep TRƯỚC khi rerank.
    Đo độ lệch cứng-vs-mềm. Rủi ro: giết câu doc-hợp-lệ -> KHÔNG phải lựa chọn chính.
    An toàn rỗng: nếu lọc xong không còn gì thì trả nguyên rổ (khỏi rerank list rỗng)."""
    filtered = [c for c in candidates if c.get("type") == keep]
    return filtered if filtered else candidates


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
