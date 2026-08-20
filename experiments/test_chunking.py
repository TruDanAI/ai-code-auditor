# test_chunking.py
from mini_rag import chunk_text

path = r"C:\Users\Pc\Desktop\New folder\chatbot-fanpage\DESIGN.md"   # đổi nếu tên file khác
with open(path, "r", encoding="utf-8") as f:
    md_file = {"path": "DESIGN.md", "text": f.read()}

md_chunks = chunk_text(md_file)
print(f"DESIGN.md -> {len(md_chunks)} chunks")
for c in md_chunks:
    print(f"  chunk {c['chunk_id']}: {len(c['content'])} chars | {c['content'][:80]}...")
