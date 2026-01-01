import json
import os
import re

BASE_DIR = os.path.dirname(__file__)
KB_PATH = os.path.join(BASE_DIR, "knowledge_base.json")

# Load knowledge base once
with open(KB_PATH, "r", encoding="utf-8") as f:
    KNOWLEDGE_BASE = json.load(f)

def normalize(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", "", text)   # remove punctuation
    return text

def get_knowledge_answer(user_input: str):
    if not user_input:
        return None

    query = normalize(user_input)

    # 1️⃣ Exact match
    if query in KNOWLEDGE_BASE:
        return KNOWLEDGE_BASE[query]

    # 2️⃣ Partial / fuzzy match
    for key, answer in KNOWLEDGE_BASE.items():
        if key in query or query in key:
            return answer

    # 3️⃣ NO match → return None (IMPORTANT)
    return None
