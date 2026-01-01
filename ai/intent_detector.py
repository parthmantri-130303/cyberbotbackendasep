import re

def detect_intent(message: str) -> str:
    msg = message.lower()

    # 1️⃣ NEWS
    news_keywords = [
        "news", "latest", "recent", "breach",
        "attack", "incident", "update", "today"
    ]
    if any(word in msg for word in news_keywords):
        return "news"

    # 2️⃣ PHISHING (URL present)
    if re.search(r"https?://\S+", msg):
        return "phishing"

    # 3️⃣ SPAM
    spam_keywords = [
        "win", "free", "offer", "click",
        "urgent", "otp", "bank", "lottery"
    ]
    if any(word in msg for word in spam_keywords):
        return "spam"

    # 4️⃣ LEARNING / EDUCATIONAL
    learning_keywords = [
        "what is", "explain", "how to",
        "define", "meaning", "difference"
    ]
    if any(word in msg for word in learning_keywords):
        return "learning"

    # 5️⃣ DEFAULT → AI
    return "ai"
