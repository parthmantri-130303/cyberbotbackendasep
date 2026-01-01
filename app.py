from flask import Flask, request, jsonify
from flask_cors import CORS
import os, re, requests
from datetime import datetime
from pymongo import MongoClient
from openai import OpenAI

# ================= INTERNAL MODULES =================
from ai.knowledge_engine import get_knowledge_answer
from ai.intent_detector import detect_intent
from news.news_fetcher import fetch_and_store_news

# ================= APP SETUP =================
app = Flask(__name__)
CORS(app)

# ================= ENV VARIABLES =================
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
HF_API_TOKEN = os.getenv("HF_API_TOKEN")
MONGODB_URI = os.getenv("MONGODB_URI")

# ================= OPENAI =================
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# ================= HUGGING FACE =================
HF_HEADERS = {
    "Authorization": f"Bearer {HF_API_TOKEN}"
}

PHISHING_MODEL_URL = "https://api-inference.huggingface.co/models/ealvaradob/bert-finetuned-phishing"
SPAM_MODEL_URL = "https://api-inference.huggingface.co/models/mrm8488/bert-tiny-finetuned-sms-spam-detection"

# ================= MONGODB =================
mongo_client = MongoClient(MONGODB_URI.strip())
db = mongo_client["cyberbot"]
logs_collection = db["chats"]
news_collection = db["news"]

# ================= OPENAI FALLBACK =================
def chatgpt_reply(message):
    if not client:
        return "⚠️ AI service unavailable. Using built-in cybersecurity tips."

    try:
        res = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are CyberBot, a cybersecurity assistant."},
                {"role": "user", "content": message}
            ],
            temperature=0.4
        )
        return res.choices[0].message.content
    except Exception:
        return (
            "⚠️ AI limit reached.\n"
            "• Never share OTPs\n"
            "• Avoid urgent payment requests\n"
            "• Verify links before clicking"
        )

# ================= PHISHING =================
def check_phishing(url):
    try:
        r = requests.post(PHISHING_MODEL_URL, headers=HF_HEADERS, json={"inputs": url}, timeout=10)
        res = r.json()
        if isinstance(res, list) and res[0]["label"].lower() == "phishing":
            return "⚠️ This URL is likely a PHISHING website."
        return "✅ This URL appears LEGITIMATE."
    except Exception:
        return "❌ Phishing detection unavailable."

# ================= SPAM =================
def check_spam(text):
    try:
        r = requests.post(SPAM_MODEL_URL, headers=HF_HEADERS, json={"inputs": text}, timeout=10)
        res = r.json()
        if isinstance(res, list) and res[0]["label"].lower() == "spam":
            return "🚨 This message is SPAM."
        return "✅ This message is NOT spam."
    except Exception:
        return "❌ Spam detection unavailable."

# ================= LOGGING =================
def save_log(user, bot, intent):
    try:
        logs_collection.insert_one({
            "user_message": user,
            "bot_reply": bot,
            "intent": intent,
            "timestamp": datetime.utcnow()
        })
    except Exception as e:
        print("MongoDB log error:", e)

# ================= ROUTES =================
@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "running", "message": "CyberBot backend is live 🚀"})

# ================= CHAT =================
@app.route("/chat", methods=["POST"])
def chat():
    message = request.json.get("message", "").strip()
    intent = detect_intent(message)

    # LEARNING
    if intent == "learning":
        reply = get_knowledge_answer(message) or "📘 Please ask a cybersecurity question."
        save_log(message, reply, intent)
        return jsonify({"reply": reply, "intent": intent})

    # NEWS
    if intent == "news":
        fetch_and_store_news()
        news = list(news_collection.find({}, {"_id": 0}).sort("timestamp", -1).limit(5))
        reply = "📰 Latest Cybersecurity News:\n\n"
        for n in news:
            reply += f"• {n['title']}\n{n['link']}\n\n"
        save_log(message, reply, intent)
        return jsonify({"reply": reply, "intent": intent})

    # PHISHING
    if intent == "phishing":
        url = re.search(r"https?://\S+", message)
        reply = check_phishing(url.group()) if url else "⚠️ Please provide a valid URL."
        save_log(message, reply, intent)
        return jsonify({"reply": reply, "intent": intent})

    # SPAM
    if intent == "spam":
        reply = check_spam(message)
        save_log(message, reply, intent)
        return jsonify({"reply": reply, "intent": intent})

    # AI
    reply = chatgpt_reply(message)
    save_log(message, reply, "ai")
    return jsonify({"reply": reply, "intent": "ai"})

# ================= HISTORY =================
@app.route("/history", methods=["GET"])
def history():
    return jsonify(list(logs_collection.find({}, {"_id": 0}).sort("timestamp", 1)))

# ================= RUN =================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
