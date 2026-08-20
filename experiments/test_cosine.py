#test_cosine.py
from sentence_transformers import SentenceTransformer
import numpy as np
from mini_rag import cosine_similarity

model = SentenceTransformer("all-MiniLM-L6-v2")

sentences = [
    "kiểm tra chữ ký webhook",                       # 0    
    "verify signature from Facebook",                # 1 - đồng nghĩa với 0
    "cách nấu phở bò Hà Nội",                        # 2 - rác, không liên qu
    "mã hoá credential bằng AES-256-GCM",            # 3
    "encrypt tokens using AES Galois Counter Mode",  # 4 - đồng nghĩa với 3
]

embeddings = model.encode(sentences)

#In ma trận hàng i so với cột j
print("Cosine similarity giữa các câu:")
for i in range(len(sentences)):
    for j in range(len(sentences)):
        score = cosine_similarity(embeddings[i], embeddings[j])
        print(f"{score:.3f}", end=" ")
    print(f"<-[{i}] {sentences[i][:35]}") 

# --- So sánh Cosine vs Euclidean: câu dài vs câu ngắn cùng nghĩa ---
long_sentence  = "Hệ thống xác thực và kiểm tra chữ ký số webhook gửi từ Facebook Messenger qua thuật toán HMAC-SHA256 với khóa bí mật"
short_sentence = "kiểm tra chữ ký webhook"

long_emb  = model.encode([long_sentence])[0]
short_emb = model.encode([short_sentence])[0]

cos_score = cosine_similarity(long_emb, short_emb)        # đo GÓC
euc_dist  = np.linalg.norm(long_emb - short_emb)          # đo KHOẢNG CÁCH thẳng

print(f"\nCosine similarity : {cos_score:.4f}   (càng GẦN 1 càng giống)")
print(f"Euclidean distance: {euc_dist:.4f}   (càng GẦN 0 càng giống)")

print(f"Độ dài long_emb : {np.linalg.norm(long_emb):.4f}")   # kỳ vọng ≈ 1.0000
print(f"Độ dài short_emb: {np.linalg.norm(short_emb):.4f}")  # kỳ vọng ≈ 1.0000
