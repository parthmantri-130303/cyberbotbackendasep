from flask import Flask, request, jsonify
from flask_cors import CORS
import os, re, requests
from datetime import datetime
from pymongo import MongoClient
from openai import OpenAI

# ================= APP SETUP =================
app = Flask(__name__)
CORS(app)

# ================= ENV VARIABLES =================
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
HF_API_TOKEN = os.getenv("HF_API_TOKEN")
MONGODB_URI = os.getenv("MONGODB_URI")

# OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# Hugging Face headers
HF_HEADERS = {
    "Authorization": f"Bearer {HF_API_TOKEN}"
}

# ================= MONGODB (FIXED & SAFE) =================
mongo_client = MongoClient(
    MONGODB_URI.strip(),   # 🔥 removes \n and spaces
    w="majority"           # 🔥 forces valid write concern
)

db = mongo_client["cyberbot"]
logs_collection = db["chats"]   # matches MongoDB Atlas

# ================= MODELS =================
PHISHING_MODEL_URL = "https://api-inference.huggingface.co/models/ealvaradob/bert-finetuned-phishing"
SPAM_MODEL_URL = "https://api-inference.huggingface.co/models/mrm8488/bert-tiny-finetuned-sms-spam-detection"

# ================= CHATGPT =================
def chatgpt_reply(message):
    if not client:
        return "⚠️ AI service unavailable."

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are CyberBot, a cybersecurity assistant."},
                {"role": "user", "content": message}
            ],
            temperature=0.4
        )
        return response.choices[0].message.content
    except Exception:
        return "⚠️ AI limit reached. Please try later."

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

# ================= LOGGING (SAFE) =================
def save_log(user_message, bot_reply, msg_type):
    try:
        logs_collection.insert_one({
            "user_message": user_message,
            "bot_reply": bot_reply,
            "type": msg_type,
            "timestamp": datetime.utcnow()
        })
    except Exception as e:
        print("MongoDB log error:", e)

# ================= ROUTES =================
@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "running", "message": "CyberBot backend is live 🚀"})

@app.route("/chat", methods=["POST"])
def chat():
    message = request.json.get("message", "")

    url_pattern = re.compile(r"https?://\S+")
    spam_keywords = ["win", "free", "offer", "click", "urgent", "otp", "bank"]

    if url_pattern.search(message):
        reply = check_phishing(url_pattern.search(message).group())
        msg_type = "phishing"
    elif any(w in message.lower() for w in spam_keywords):
        reply = check_spam(message)
        msg_type = "spam"
    else:
        reply = chatgpt_reply(message)
        msg_type = "chat"

    save_log(message, reply, msg_type)
    return jsonify({"reply": reply})

@app.route("/history", methods=["GET"])
def history():
    logs = list(logs_collection.find({}, {"_id": 0}).sort("timestamp", 1))
    return jsonify(logs)

@app.route("/admin/logs", methods=["GET"])
def admin_logs():
    logs = list(logs_collection.find({}, {"_id": 0}).sort("timestamp", -1))
    return jsonify(logs)

# ================= RUN =================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
