import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

model_id = "jmvcoelho/ad-classifier-v0.1"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForSequenceClassification.from_pretrained(model_id)

device = torch.device("cpu")  # Force CPU first
model.to(device).eval()

inputs = tokenizer("Test input", return_tensors="pt").to(device)
with torch.no_grad():
    outputs = model(**inputs)
print("Logits:", outputs.logits)
