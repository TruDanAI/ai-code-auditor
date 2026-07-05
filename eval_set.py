"""
eval_set.py — Ngày 9: BÀI THI CÓ ĐÁP ÁN cho tầng retrieval (golden set).

Ý tưởng 1 câu: ta KHÔNG tự viết lại RAG ở đây. Ta IMPORT lại các hàm đã làm
ở mini_rag.py (build_index, embed_texts, retrieve_top_k) rồi chỉ THÊM một
vòng lặp chấm điểm. Mỗi câu hỏi đã biết trước "đáp án đúng nằm ở file nào +
có chữ gì" => chấm tự động => ra MỘT con số precision@3 (điểm / tổng câu).

Con số này là VẠCH XUẤT PHÁT. Ngày 10 đổi MiniLM -> Qwen3 thì chạy lại file
này, so 2 con số -> biết model mới tốt lên THẬT hay chỉ cảm giác.
"""

import os
import sys
import time
import pickle

# Import lại "bộ não" đã viết — KHÔNG copy code (kỷ luật từ Ngày 8: chroma_rag).
# Ngày 11: thêm rerank + load_reranker (tầng 2 cross-encoder).
from mini_rag import (
    load_embedding_model, build_index, embed_texts, retrieve_top_k,
    rerank, load_reranker,
    rrf_fuse, build_bm25, bm25_search,        # Ngày 13: hybrid BM25 + RRF
    soft_boost_by_type, hard_filter_type,     # Ngày 14: chặn distractor doc
)

# Kho code đem ra audit (nằm NGOÀI Build CV).
ROOT_DIR = r"C:\Users\Pc\Desktop\chatbot-fanpage"

# Mỗi câu được lôi ra mấy mảnh để xét? '@3' = top-3.
K = 3

# Ngày 10: tên model lấy từ dòng lệnh -> đổi model KHÔNG cần sửa code.
#   python eval_set.py                       -> MiniLM (baseline Ngày 9)
#   python eval_set.py BAAI/bge-m3           -> BGE-M3
#   python eval_set.py Qwen/Qwen3-Embedding-0.6B  -> Qwen3
MODEL_NAME = sys.argv[1] if len(sys.argv) > 1 else "all-MiniLM-L6-v2"

# Ngày 11: đối số THỨ HAI = kích thước rổ ứng viên cho reranker (tầng 2).
#   python eval_set.py BAAI/bge-m3        -> KHÔNG rerank (baseline Ngày 10, 40%)
#   python eval_set.py BAAI/bge-m3 50     -> 2 tầng, rổ N=50
#   python eval_set.py BAAI/bge-m3 150    -> 2 tầng, rổ N=150 (kỳ vọng RBAC sống lại)
# CÓ đối số -> bật rerank; KHÔNG có -> chạy thuần bi-encoder để đối chiếu.
K_RETRIEVE = int(sys.argv[2]) if len(sys.argv) > 2 else None
USE_RERANK = K_RETRIEVE is not None

# Ngày 13-14: các CỜ tùy chọn sau argv[2] — KHÔNG phụ thuộc thứ tự (quét cả list).
#   hybrid   -> bật kênh BM25 + trộn RRF (Ngày 13).
#   lam=X    -> soft-boost: TRỪ X (logit) vào rerank_score mọi chunk .md (Ngày 14).
#   hard     -> ablation: vứt sạch chunk doc TRƯỚC rerank (đo lệch cứng-vs-mềm).
# Lưới 2x2 Ngày 14 (đổi ĐÚNG 1 biến/lần):
#   python eval_set.py BAAI/bge-m3 50                 -> filter TẮT, hybrid TẮT (baseline 40%)
#   python eval_set.py BAAI/bge-m3 50 lam=1           -> filter BẬT (soft λ=1), hybrid TẮT
#   python eval_set.py BAAI/bge-m3 50 hybrid          -> filter TẮT, hybrid BẬT (Ngày 13, 20%)
#   python eval_set.py BAAI/bge-m3 50 hybrid lam=1    -> filter BẬT + hybrid BẬT
#   python eval_set.py BAAI/bge-m3 50 hard            -> ablation hard-filter (chỉ code)
_flags = [a.lower() for a in sys.argv[3:]]
USE_HYBRID = "hybrid" in _flags
USE_HARD_FILTER = "hard" in _flags
# λ đọc từ token 'lam=X'; không có -> 0.0 (=baseline, chốt chặn sanity λ=0).
LAMBDA = next((float(a.split("=", 1)[1]) for a in _flags if a.startswith("lam=")), 0.0)
USE_SOFT_FILTER = LAMBDA > 0.0

# Tên reranker đặt cứng (không cần swap như embedding) — model CPU-friendly Ngày 11.
RERANKER_NAME = "BAAI/bge-reranker-v2-m3"

# CẠM BẪY Qwen3 — model BẤT ĐỐI XỨNG: query phải kèm "lời dặn", document để trần.
# Bỏ bước này Qwen3 vẫn chạy nhưng điểm THẤP hơn tiềm năng -> chấm oan cho nó.
# (BGE-M3 / MiniLM không cần -> chỉ áp khi tên model có 'qwen3'.)
QWEN_QUERY_INSTRUCT = (
    "Instruct: Given a question, retrieve code or documentation that answers it\nQuery: "
)


def embed_query(model, model_name, question):
    """Embed 1 câu hỏi. Riêng Qwen3 thì gắn lời dặn trước câu hỏi."""
    if "qwen3" in model_name.lower():
        question = QWEN_QUERY_INSTRUCT + question
    return embed_texts(model, [question])[0]


# ---------------------------------------------------------------------------
# BÀI THI. Mỗi phần tử:
#   question            : câu người dùng hỏi.
#   expected_path_substr: 1 mẩu đường dẫn để nhận ra ĐÚNG FILE chứa đáp án.
#   expected_keywords   : vài chữ mà chunk ĐÚNG chắc chắn phải có (case-insensitive).
#
# QUY TẮC CHẤM (đọc kỹ — đây là "định nghĩa đúng" của ta):
#   1 mảnh được tính là "mảnh vàng" khi nó VỪA thuộc đúng file (path khớp)
#   VỪA chứa >= 1 keyword. Câu ĐẬU nếu top-3 có ÍT NHẤT 1 mảnh vàng.
#
# CHỈ chứa câu IN-SCOPE (có đáp án thật trong code). Câu off-topic (Stripe/
# Zalo/Redis) KHÔNG vào đây — chúng đo "rào chắn từ chối", việc của stress_test.py.
#
# 6 câu dưới đã GREP VERIFY thật trong chatbot-fanpage (không đoán theo tên file).
# TODO Ngày 9: grep thêm 9 câu in-scope nữa cho đủ 15.
# ---------------------------------------------------------------------------
EVAL_SET = [
    {
        "question": "verifySignature dùng thuật toán gì để xác thực webhook?",
        "expected_path_substr": "webhook.js",
        "expected_keywords": ["createHmac", "timingSafeEqual", "sha256"],
    },
    {
        "question": "credential được mã hoá bằng thuật toán/mode nào?",
        "expected_path_substr": "page-credentials.js",
        "expected_keywords": ["aes-256-gcm"],
    },
    {
        # SỬA Ngày 9: ground-truth ban đầu trỏ tests/admin-routes.test.js — nhưng
        # IGNORE_DIRS loại 'tests' nên chunk đó KHÔNG có trong index (gold_rank báo
        # KHÔNG TÌM THẤY). Vai trò RBAC cũng được định nghĩa thật ở core/admin-auth.js
        # (ROLE_PERMISSIONS) -> trỏ lại đây, file này CÓ được index.
        "question": "hệ thống phân quyền admin (RBAC) có những vai trò nào?",
        "expected_path_substr": "admin-auth.js",
        "expected_keywords": ["viewer", "support", "maintainer", "owner"],
    },
    {
        "question": "lead parser trích số điện thoại của khách bằng cách nào?",
        "expected_path_substr": "lead-parser.js",
        "expected_keywords": ["PHONE_LABEL_PATTERN", "extractLabeledLeadValue", "sđt"],
    },
    # RÚT Ngày 9: "framework unit test nào?" — đáp án DUY NHẤT nằm ở tests/harness.js,
    # mà IGNORE_DIRS loại 'tests'. Không có nguồn hợp lệ trong corpus -> bỏ khỏi bài thi.
    # PHÁT HIỆN: corpus đang bỏ tests/, trong khi tests chứa "sự thật quyền lực"
    # (vai trò RBAC, hành vi mong đợi). Cân nhắc index cả tests ở giai đoạn sau.
    {
        "question": "cơ chế cô lập nhiều cửa hàng (multi-shop isolation) hoạt động ra sao?",
        "expected_path_substr": "multi-shop-rollout.md",
        "expected_keywords": ["dry_run"],
    },
]


def is_gold_chunk(chunk, item):
    """1 mảnh có phải 'mảnh vàng' của câu hỏi không?

    True khi: path khớp file đáp án  VÀ  content chứa >= 1 keyword.
    (Siết cả 2 điều kiện để bớt false-positive: 'chunk nam châm' admin/views.js
     vô tình chứa 1 keyword vẫn KHÔNG được tính nếu sai file.)
    """
    path_ok = item["expected_path_substr"].lower() in chunk["path"].lower()
    content_lower = chunk["content"].lower()
    keyword_ok = any(kw.lower() in content_lower for kw in item["expected_keywords"])
    return path_ok and keyword_ok


def gold_rank(query_emb, index, item):
    """Mảnh vàng của câu này đang nằm HẠNG MẤY trong TOÀN BỘ kho?

    Mẹo: gọi lại retrieve_top_k nhưng k = TẤT CẢ chunk -> được danh sách
    3308 mảnh đã xếp hạng sẵn. Dò từ trên xuống, gặp mảnh vàng đầu tiên thì
    trả về (hạng, điểm). Không có mảnh vàng nào -> (None, None) = thảm hoạ (B):
    đáp án không hề được index, hoặc keyword/path của ta sai.
    """
    full_ranking = retrieve_top_k(query_emb, index, k=len(index["chunks"]))
    for rank, chunk in enumerate(full_ranking, start=1):   # hạng đếm từ 1
        if is_gold_chunk(chunk, item):
            return rank, chunk["score"]
    return None, None


def build_index_cached(root_dir, model, model_name):
    """Như build_index nhưng CACHE bộ vector ra đĩa, khóa theo tên model.

    Vì sao: embed 3308 chunk bằng BGE-M3 trên CPU ~40 phút/lần. Chạy lại để
    đổi N (50 vs 150) hay bật/tắt rerank KHÔNG đổi vector -> embed lại là phí.
    Lần đầu: embed + lưu .pkl. Lần sau: nạp .pkl tức thì (chunking vẫn chạy lại
    nhưng nhanh; embedding mới là phần đắt được bỏ qua).

    Cache khóa theo MODEL_NAME -> mỗi model 1 file riêng, không lẫn lộn.
    Xóa file để buộc embed lại (vd sau khi sửa chunking).
    """
    # AN TOÀN pickle: file này do CHÍNH script ghi rồi đọc lại (local, tự sinh),
    # KHÔNG phải dữ liệu từ nguồn ngoài -> không có rủi ro thực thi mã lạ.
    safe = model_name.replace("/", "_").replace("\\", "_")
    cache_path = f".index_cache_{safe}.pkl"          # nhớ thêm vào .gitignore (file ~13MB)
    if os.path.exists(cache_path):
        print(f"[cache] nạp vector sẵn từ {cache_path} (bỏ qua embed)")
        with open(cache_path, "rb") as f:
            return pickle.load(f)

    print(f"[cache] chưa có -> embed 1 lần rồi lưu vào {cache_path}")
    index = build_index(root_dir, model)
    with open(cache_path, "wb") as f:
        pickle.dump(index, f)
    return index


def _rerank_stage(reranker, question, candidates):
    """TẦNG 2 + filter Ngày 14, dùng chung cho cả nhánh dense-only lẫn hybrid.

    Thứ tự BẮT BUỘC:
      1. HARD-filter (nếu bật): vứt doc khỏi rổ TRƯỚC rerank (ablation).
      2. rerank CHẤM CẢ RỔ (top_k=len) — KHÔNG cắt top-K vội, để chunk code còn
         cơ hội vượt lên sau khi doc bị phạt.
      3. SOFT-boost: trừ λ vào doc rồi cắt top-K. λ=0 -> y hệt rerank gốc.
    """
    if USE_HARD_FILTER:
        candidates = hard_filter_type(candidates, keep="code")
    reranked_full = rerank(reranker, question, candidates, top_k=len(candidates))
    return soft_boost_by_type(reranked_full, lam=LAMBDA, top_k=K)


def main():
    if USE_HYBRID and not USE_RERANK:
        sys.exit("Hybrid cần kích thước rổ N + rerank. Chạy: python eval_set.py <model> <N> hybrid")
    # Ngày 14: filter (soft/hard) sống Ở TẦNG rerank -> vô nghĩa nếu không rerank.
    if (USE_SOFT_FILTER or USE_HARD_FILTER) and not USE_RERANK:
        sys.exit("Filter cần rerank. Thêm N: python eval_set.py <model> <N> lam=1  (hoặc ... hard)")
    print(f"MODEL: {MODEL_NAME}")
    if USE_HARD_FILTER:
        print("FILTER: HARD (ablation) — vứt sạch chunk doc TRƯỚC rerank (chỉ giữ code)")
    elif USE_SOFT_FILTER:
        print(f"FILTER: SOFT — trừ λ={LAMBDA:g} (logit) vào rerank_score mọi chunk .md")
    else:
        print("FILTER: TẮT (λ=0) — chốt chặn: phải ra y baseline rerank")
    if USE_HYBRID:
        print(f"HYBRID: BẬT — BM25 + dense (mỗi kênh top-{K_RETRIEVE}) -> RRF -> {RERANKER_NAME} xếp lại top-{K}")
    elif USE_RERANK:
        print(f"RERANK: BẬT — bi-encoder lấy top-{K_RETRIEVE} -> {RERANKER_NAME} xếp lại top-{K}")
    else:
        print(f"RERANK: TẮT — bi-encoder thuần, lấy thẳng top-{K} (baseline đối chiếu)")
    print(f"Nạp model + dựng index từ: {ROOT_DIR}")
    # Ngày 11 (GPU 4GB): VRAM trống ~3.45GB KHÔNG đủ chứa BGE-M3 (~2.2GB) +
    # reranker (~2.27GB) cùng lúc -> OOM. Khi rerank: ép embedding model xuống
    # CPU (đã cache nên chỉ embed 1 câu hỏi/lần, nhẹ), nhường trọn VRAM cho reranker.
    import torch
    have_cuda = torch.cuda.is_available()
    embed_device = "cpu" if (USE_RERANK and have_cuda) else None   # None = tự chọn (GPU)
    print(f"GPU: {'CÓ' if have_cuda else 'KHÔNG'} | embed trên: {embed_device or 'auto'} | reranker: {'GPU' if (USE_RERANK and have_cuda) else 'CPU/auto'}")

    model = load_embedding_model(MODEL_NAME, device=embed_device)   # Ngày 10–11: model + thiết bị
    index = build_index_cached(ROOT_DIR, model, MODEL_NAME)   # Ngày 11: embed 1 lần, cache lại
    print(f"Index xong: {len(index['chunks'])} chunks.")

    # Ngày 13: dựng BM25 + map key->chunk MỘT lần, chỉ khi chạy hybrid.
    #   build_bm25 tokenize toàn corpus (nhanh, vài giây) — KHÔNG đụng embeddings.
    #   key_to_chunk: tra ngược (path, chunk_id) -> chunk gốc (có 'content' cho reranker).
    bm25 = build_bm25(index["chunks"]) if USE_HYBRID else None
    key_to_chunk = {(c["path"], c["chunk_id"]): c for c in index["chunks"]} if USE_HYBRID else None

    # Tải reranker MỘT lần trước vòng lặp (đắt ~600MB) — chỉ khi cần.
    reranker = load_reranker(RERANKER_NAME) if USE_RERANK else None
    print()

    correct = 0
    total_retrieval_time = 0.0          # cộng dồn để ra thời gian TB/câu (số trade-off CV)
    for item in EVAL_SET:
        # embed 1 câu hỏi -> vector 1D. (Qwen3 được gắn lời dặn bên trong embed_query.)
        query_emb = embed_query(model, MODEL_NAME, item["question"])

        t0 = time.perf_counter()
        if USE_HYBRID:
            # TẦNG 1a dense (cosine) top-N  +  TẦNG 1b BM25 (keyword) top-N.
            dense_ranked = retrieve_top_k(query_emb, index, k=K_RETRIEVE)
            bm25_ranked = bm25_search(bm25, index["chunks"], item["question"], k=K_RETRIEVE)
            # rút KEY (path, chunk_id) -> RRF trộn theo THỨ HẠNG -> giữ rổ N để rerank.
            dense_keys = [(c["path"], c["chunk_id"]) for c in dense_ranked]
            bm25_keys = [(c["path"], c["chunk_id"]) for c in bm25_ranked]
            fused_keys = rrf_fuse(dense_keys, bm25_keys, k=60)[:K_RETRIEVE]
            candidates = [key_to_chunk[key] for key in fused_keys]   # key -> chunk gốc (có content)
            top_chunks = _rerank_stage(reranker, item["question"], candidates)
        elif USE_RERANK:
            # TẦNG 1: bi-encoder lọc thô rổ N lớn -> TẦNG 2: cross-encoder xếp lại top-K.
            candidates = retrieve_top_k(query_emb, index, k=K_RETRIEVE)
            top_chunks = _rerank_stage(reranker, item["question"], candidates)
        else:
            top_chunks = retrieve_top_k(query_emb, index, k=K)
        total_retrieval_time += time.perf_counter() - t0

        # Câu ĐẬU nếu BẤT KỲ mảnh nào trong top-K là 'mảnh vàng'.
        hit = any(is_gold_chunk(c, item) for c in top_chunks)

        if hit:
            correct += 1
            print(f"[ĐẬU ] {item['question']}")
        else:
            # In ra top-K đã lôi nhầm gì -> để debug retrieval (đúng bài Ngày 6).
            # Khi rerank: hiện CẢ rerank_score (xếp hạng cuối) LẪN score cosine tầng 1.
            print(f"[RỚT ] {item['question']}")
            for c in top_chunks:
                if "rerank_score" in c:
                    cos = c.get("score")   # hybrid: chunk lấy từ key_to_chunk có thể CHƯA có cosine
                    cos_str = f"{cos:.3f}" if cos is not None else "  -  "
                    # Ngày 14: hiện boosted_score (điểm SAU phạt λ) + [type] -> đọc được
                    # λ đang đạp doc xuống hạng nào, code có vượt lên không.
                    b = c.get("boosted_score")
                    b_str = f" boost={b:+.2f}" if b is not None else ""
                    print(f"         rr={c['rerank_score']:+.2f}{b_str} cos={cos_str}  "
                          f"[{c.get('type','?'):4}] {c['path']}  (chunk {c['chunk_id']})")
                else:
                    print(f"         {c['score']:.3f}  [{c.get('type','?'):4}] {c['path']}  (chunk {c['chunk_id']})")
            # Chẩn đoán: mảnh vàng thật nằm hạng mấy Ở TẦNG 1 (bi-encoder)?
            rank, score = gold_rank(query_emb, index, item)
            if rank is None:
                print(f"         -> mảnh vàng: KHÔNG TÌM THẤY trong index (kiểm tra lại path/keyword!)")
            else:
                msg = f"         -> mảnh vàng nằm HẠNG {rank}/{len(index['chunks'])} ở tầng 1 (cos {score:.3f})"
                # Insight Ngày 11: rerank chỉ xếp lại NHỮNG GÌ tầng 1 đưa vào rổ.
                if USE_RERANK and rank > K_RETRIEVE:
                    msg += f"  <-- NGOÀI rổ top-{K_RETRIEVE}: reranker không hề thấy nó (trần recall tầng 1!)"
                elif USE_RERANK:
                    msg += f"  <-- trong rổ nhưng reranker vẫn dìm (xem chunk có thật chứa câu trả lời?)"
                print(msg)

    total = len(EVAL_SET)
    avg_ms = total_retrieval_time / total * 1000
    if USE_HYBRID:
        tag = f"HYBRID bm25+dense->rrf->rerank top-{K_RETRIEVE}"
    elif USE_RERANK:
        tag = f"rerank top-{K_RETRIEVE}"
    else:
        tag = "no-rerank"
    # Ngày 14: đính nhãn filter vào tag -> mỗi ô của lưới 2x2 in ra tự-mô-tả.
    if USE_HARD_FILTER:
        tag += " +hardfilter"
    elif USE_SOFT_FILTER:
        tag += f" +soft(λ={LAMBDA:g})"
    print(f"\n[{MODEL_NAME} | {tag}] precision@{K}: {correct}/{total} = {correct / total * 100:.1f}%")
    print(f"Thời gian retrieval TB: {avg_ms:.0f} ms/câu  (số trade-off tốc độ vs N)")


if __name__ == "__main__":
    main()
