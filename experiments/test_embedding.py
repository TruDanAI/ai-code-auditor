from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")

sentences = [
    "kiểm tra chữ ký webhook",                       # 0
    "verify signature from Facebook",                # 1 - đồng nghĩa với 0
    "mã hoá credential bằng AES-256-GCM",            # 2
    "encrypt tokens using AES Galois Counter Mode",  # 3 - đồng nghĩa với 2
    "cách nấu phở bò Hà Nội",                        # 4 - rác, không liên quan
    "thời tiết hôm nay thế nào",                     # 5 - rác, không liên quan
]

# encode() biến 6 câu -> ma trận (6,384): 6 hàng, mỗi hàng 1 vector embedding 384 chiều
embeddings = model.encode(sentences)

print(f"Số chiều vector: {embeddings.shape[1]}")  # 384
print(f"Kích thước mảng: {embeddings.shape}")  # (6, 384)

# In 5 số đầu của mỗi vector để thấy "text đã thành số"
for i, s in enumerate(sentences):
    print(f"[{i}] {s[:40]:40s} -> {embeddings[i][:5]}")

# --- Buổi chiều: thí nghiệm giới hạn embedding ---
extra = [
    "đơn hàng #1234 trạng thái gì",        # 6
    "đơn hàng #5678 trạng thái gì",        # 7 - khác SỐ nhưng cùng pattern
    "order status for order number 1234",  # 8 - cùng nghĩa câu 6, khác ngôn ngữ
]

extra_emb = model.encode(extra)

from numpy.linalg import norm   # norm = độ dài vector

# cosine: gần 1.0 = rất giống nghĩa, gần 0 = không liên quan
def quick_cosine(a, b):
    return np.dot(a, b) / (norm(a) * norm(b))

print(f"\n#1234 vs #5678 (khác số): {quick_cosine(extra_emb[0], extra_emb[1]):.4f}")
print(f"#1234 vi vs #1234 en:     {quick_cosine(extra_emb[0], extra_emb[2]):.4f}")
