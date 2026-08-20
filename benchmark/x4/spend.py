"""In tong chi phi da tieu, doc thang tu raw/**/*.json - nguon su that duy nhat.

Cong don bang bien bash de desync im lang (bug cu: mot cu goi python hong ->
bien rong -> tran ngan sach chet ma vong lap van chay).
"""
import glob
import json
import os

root = os.path.join(os.path.dirname(__file__), "raw")
total = 0.0
for path in glob.glob(os.path.join(root, "**", "*.json"), recursive=True):
    try:
        with open(path, encoding="utf-8") as fh:
            total += float(json.load(fh).get("total_cost_usd") or 0)
    except Exception:
        pass  # file rong / rach = 0 dong, khong duoc lam sap bo dem
print(f"{total:.6f}")
