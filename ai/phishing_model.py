from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

MODEL_NAME = "ealvaradob/bert-finetuned-phishing"

# Load once (important for performance)
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)

def check_phishing(url):
    inputs = tokenizer(url, return_tensors="pt", truncation=True)

    with torch.no_grad():
        outputs = model(**inputs)

    logits = outputs.logits
    prediction = torch.argmax(logits, dim=1).item()

    # Model labels:
    # 0 → legitimate
    # 1 → phishing
    if prediction == 1:
        return "⚠️ This URL is likely a PHISHING website."
    else:
        return "✅ This URL appears to be LEGITIMATE."
