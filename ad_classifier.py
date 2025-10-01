import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

class AdClassifier:
    def __init__(self, model_name: str = "jmvcoelho/ad-classifier-v0.1"):
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.device = device

        # Load model and tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.model.to(self.device)
        self.model.eval()

    def predict(self, text: str) -> int:
        """Return 1 if ad, 0 if not ad"""
        inputs = self.tokenizer(
            text,
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors="pt"
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            prediction = torch.argmax(logits, dim=-1).item()

        return prediction

