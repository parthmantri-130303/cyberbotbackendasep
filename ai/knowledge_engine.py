import json
import os
import re

BASE_DIR = os.path.dirname(__file__)
KB_DIR = os.path.join(BASE_DIR, "knowledge_base")

KNOWLEDGE_BASE = {}

# ================= LOAD ALL JSON FILES =================
if os.path.exists(KB_DIR):
    for file in os.listdir(KB_DIR):
        if file.endswith(".json"):
            file_path = os.path.join(KB_DIR, file)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        KNOWLEDGE_BASE.update(data)
            except Exception as e:
                print(f"Error loading {file}: {e}")

def normalize(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", "", text)
    return text

def get_knowledge_answer(user_input: str):
    if not user_input or not KNOWLEDGE_BASE:
        return None

    query = normalize(user_input)

    # 1️⃣ Exact match
    if query in KNOWLEDGE_BASE:
        return KNOWLEDGE_BASE[query]

    # 2️⃣ Partial match
    for key, answer in KNOWLEDGE_BASE.items():
        if key in query or query in key:
            return answer

    return None
