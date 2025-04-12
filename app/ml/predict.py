# predict.py
import torch
from transformers import BertTokenizer, BertForSequenceClassification
import joblib
import numpy as np

# Load the trained BERT model and tokenizer
model_path = "./bert_model"
model = BertForSequenceClassification.from_pretrained(model_path)
tokenizer = BertTokenizer.from_pretrained(model_path)
model.eval()  # Set model to evaluation mode

# Load label encoder to decode predictions
label_encoder = joblib.load("./app/ml/label_encoder.joblib")

def predict_cyberbullying(text: str) -> dict:
    """
    Run inference on input text using the fine-tuned BERT model
    Returns prediction label and probabilities.
    """
    with torch.no_grad():
        inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=128)
        outputs = model(**inputs)
        logits = outputs.logits
        probabilities = torch.softmax(logits, dim=1).detach().numpy()[0]
        predicted_class_id = np.argmax(probabilities)
        predicted_label = label_encoder.inverse_transform([predicted_class_id])[0]

        return {
            "label": predicted_label,
            "confidence": float(np.max(probabilities))
        }

# Example usage
if __name__ == "__main__":
    sample_text = "You're such a loser, nobody likes you."
    result = predict_cyberbullying(sample_text)
    print("Prediction:", result)
