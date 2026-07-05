"""
chroma_rag.py - Ngày 8: migrate kho lưu trữ từ list Python (mini_rag.py)
sang Vector DB thật (ChromaDB), rồi SO top-3 hai bên xem có khớp không.

NGUYÊN TẮC: KHÔNG copy-paste mini_rag.py. Import lại các hàm đã có,
chỉ viết thêm phần Chroma. Sửa pipeline 1 chỗ -> cả 2 file cùng đúng.

CÁCH SO CÔNG BẰNG (apples-to-apples, né "bẫy 1"):
  cả hai bên phải dùng CÙNG embedding (sentence-transformers all-MiniLM),
  nên ta TỰ embed rồi BƠM vector vào Chroma, không để Chroma tự embed.

RUN:
    python chroma_rag.py C:\\Users\\Pc\\Desktop\\chatbot-fanpage
"""

import sys
import chromadb

# Tái dùng đồ đã viết Tuần 1 — không nhân bản code.
from mini_rag import (
    load_files,
    chunk_text,
    load_embedding_model,
    embed_texts,
    retrieve_top_k,
    TOP_K,
)


def build_chunks_and_embeddings(root_dir, model):
    """Dùng lại pipeline cũ: load -> chunk -> embed. Trả về (chunks, embeddings)."""
    files = load_files(root_dir)
    all_chunks = []
    for f in files:
        all_chunks.extend(chunk_text(f))
    texts = [c["content"] for c in all_chunks]
    embeddings = embed_texts(model, texts)          # ma trận (n, 384), giống mini_rag
    return all_chunks, embeddings


def build_chroma_collection(all_chunks, embeddings):
    """
    Dựng collection Chroma và NHỒI sẵn vector ta đã tự tính.

    metadata={"hnsw:space": "cosine"} -> ép Chroma đo bằng cosine cho khớp
    hàm cosine tay của bạn (mặc định nó là 'l2'; nhớ Ngày 3: vector đã
    normalize thì l2 và cosine xếp hạng y hệt, nhưng đặt cosine cho khỏi nghĩ).
    """
    client = chromadb.Client()                       # in-memory, local
    collection = client.create_collection(
        name="code_chunks",
        metadata={"hnsw:space": "cosine"},
    )

    ids = [f"{c['path']}_{c['chunk_id']}" for c in all_chunks]
    metadatas = [{"path": c["path"], "chunk_id": c["chunk_id"]} for c in all_chunks]
    documents = [c["content"] for c in all_chunks]   # lưu để in ra đối chiếu

    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        # né bẫy 1: bơm CHÍNH vector ta tự tính (sentence-transformers),
        # KHÔNG để Chroma tự embed lại bằng ONNX. .tolist() vì Chroma
        # muốn list thuần, không nhận numpy array.
        embeddings=embeddings.tolist(),
    )
    return collection


def chroma_top_k(collection, query_embedding, k=TOP_K):
    """Hỏi Chroma top-k. Trả list (path, chunk_id, distance)."""
    res = collection.query(
        # né bẫy 1: hỏi bằng VECTOR tự embed, KHÔNG query_texts=[...]
        # (query_texts để Chroma tự embed -> lệch model -> so sai).
        query_embeddings=[query_embedding.tolist()],
        n_results=k,
    )
    # Chroma trả dict lồng list-trong-list (1 list/1 query). Lấy query thứ 0:
    out = []
    for meta, dist in zip(res["metadatas"][0], res["distances"][0]):
        out.append((meta["path"], meta["chunk_id"], dist))
    return out


def main():
    if len(sys.argv) < 2:
        print("Usage: python chroma_rag.py /path/to/chatbot-fanpage")
        sys.exit(1)
    root_dir = sys.argv[1]

    print("Load embedding model...")
    model = load_embedding_model()

    print(f"Index {root_dir} ...")
    all_chunks, embeddings = build_chunks_and_embeddings(root_dir, model)
    print(f"  {len(all_chunks)} chunks.")

    # kho kiểu CŨ (cho retrieve_top_k tay dùng)
    index = {"chunks": all_chunks, "embeddings": embeddings}
    # kho kiểu MỚI (Chroma)
    collection = build_chroma_collection(all_chunks, embeddings)

    # Vài câu test — trộn câu đã biết kết quả từ NOTES Ngày 5-6
    questions = [
        "verifySignature HMAC SHA256",
        "cách phân quyền admin RBAC",
        "lead parser",
    ]
    for q in questions:
        q_emb = embed_texts(model, [q])[0]
        mine = retrieve_top_k(q_emb, index)                  # bản tay (cosine)
        theirs = chroma_top_k(collection, q_emb)             # bản Chroma

        print(f"\n=== Q: {q} ===")
        print("  [mini_rag - cosine tay]")
        for c in mine:
            print(f"    {c['score']:.3f}  {c['path']} #{c['chunk_id']}")
        print("  [chroma - distance]")
        for path, cid, dist in theirs:
            print(f"    {dist:.3f}  {path} #{cid}")


if __name__ == "__main__":
    main()
