import json
import os

BASE_DIR = os.path.join(os.path.dirname(__file__), "knowledge_base")

def load_knowledge_base():
    knowledge = {}

    for filename in os.listdir(BASE_DIR):
        if filename.endswith(".json"):
            filepath = os.path.join(BASE_DIR, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                knowledge.update(data)

    return knowledge


KNOWLEDGE_DB = load_knowledge_base()


def get_knowledge_answer(user_message: str):
    user_message = user_message.lower().strip()

    for question, answer in KNOWLEDGE_DB.items():
        if question in user_message:
            return answer

    return None
