# backend/ai/spam_model.py

import os
import requests

# Hugging Face Spam Detection Model
SPAM_MODEL_URL = "https://api-inference.huggingface.co/models/mrm8488/bert-tiny-finetuned-sms-spam-detection"

HF_API_TOKEN = os.getenv("HF_API_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {HF_API_TOKEN}"
}


def check_spam(text: str) -> dict:
    """
    Detects whether a message is spam or not.
    Returns structured response.
    """

    if not HF_API_TOKEN:
        return {
            "label": "unknown",
            "message": "Spam detection service unavailable."
        }

    try:
        response = requests.post(
            SPAM_MODEL_URL,
            headers=HEADERS,
            json={"inputs": text},
            timeout=10
        )

        result = response.json()

        if isinstance(result, list) and len(result) > 0:
            label = result[0]["label"].lower()
            confidence = round(result[0]["score"] * 100, 2)

            if label == "spam":
                return {
                    "label": "spam",
                    "message": f"🚨 This message is SPAM (confidence {confidence}%)."
                }

            return {
                "label": "ham",
                "message": f"✅ This message looks safe (confidence {confidence}%)."
            }

        return {
            "label": "unknown",
            "message": "Unable to analyze this message."
        }

    except Exception:
        return {
            "label": "error",
            "message": "Spam detection service temporarily unavailable."
        }
