import json
import os
import re

# ================= PATH SETUP =================
BASE_DIR = os.path.dirname(__file__)
KB_PATH = os.path.join(BASE_DIR, "knowledge_base.json")

# ================= LOAD KNOWLEDGE BASE =================
# Safe load (prevents crash if file is empty or missing)
if os.path.exists(KB_PATH):
    with open(KB_PATH, "r", encoding="utf-8") as f:
        try:
            KNOWLEDGE_BASE = json.load(f)
        except json.JSONDecodeError:
            KNOWLEDGE_BASE = {}
else:
    KNOWLEDGE_BASE = {}

# ================= NORMALIZATION =================
def normalize(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", "", text)   # remove punctuation
    text = re.sub(r"\s+", " ", text)     # normalize spaces
    return text

# ================= MAIN LOOKUP FUNCTION =================
def get_knowledge_answer(user_input: str):
    """
    Returns:
    - answer (str) if found
    - None if not found (VERY IMPORTANT)
    """

    if not user_input or not KNOWLEDGE_BASE:
        return None

    query = normalize(user_input)

    # 1️⃣ EXACT MATCH
    if query in KNOWLEDGE_BASE:
        return KNOWLEDGE_BASE[query]

    # 2️⃣ PARTIAL MATCH (user asks longer sentence)
    for key, answer in KNOWLEDGE_BASE.items():
        if key in query:
            return answer

    # 3️⃣ REVERSE PARTIAL (short query)
    for key, answer in KNOWLEDGE_BASE.items():
        if query in key:
            return answer

    # 4️⃣ NO MATCH → LET AI / OTHER LOGIC HANDLE
    return None
