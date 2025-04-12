import pandas as pd
import numpy as np
import torch
from torch.utils.data import DataLoader
from transformers import BertTokenizer, BertForSequenceClassification, get_scheduler
from torch.optim import AdamW
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score
from datasets import Dataset
import joblib
from tqdm import tqdm

# Check for GPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Load and preprocess datasets
print("Loading datasets...")
train_df = pd.read_csv("cyberbullying_tweets Training.csv")
val_df = pd.read_csv("cyberbullying_tweets Validating.csv")

# Encode labels
label_encoder = LabelEncoder()
train_df["labels"] = label_encoder.fit_transform(train_df["cyberbullying_type"])
val_df["labels"] = label_encoder.transform(val_df["cyberbullying_type"])

# Save label encoder for inference
joblib.dump(label_encoder, "./app/ml/label_encoder.joblib")
print("Label encoder saved.")

# Load tokenizer
tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")

def tokenize_function(examples):
    if "tweet_text" not in examples:
        raise KeyError(f"'tweet_text' key not found in examples: {examples.keys()}")
    tokens = tokenizer(examples["tweet_text"], truncation=True, padding="max_length", max_length=128)
    tokens["labels"] = examples["labels"]
    return tokens

# Convert DataFrames to HuggingFace datasets
train_dataset = Dataset.from_pandas(train_df[["tweet_text", "labels"]])
val_dataset = Dataset.from_pandas(val_df[["tweet_text", "labels"]])

print(f"📎 Sample keys in train_dataset: {train_dataset[0].keys()}")

# Tokenize datasets
train_dataset = train_dataset.map(tokenize_function, batched=True)
val_dataset = val_dataset.map(tokenize_function, batched=True)

# Set format for PyTorch
train_dataset.set_format(type='torch', columns=['input_ids', 'attention_mask', 'labels'])
val_dataset.set_format(type='torch', columns=['input_ids', 'attention_mask', 'labels'])

# Create dataloaders
train_loader = DataLoader(train_dataset, batch_size=8, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=8)

# Load pre-trained model
model = BertForSequenceClassification.from_pretrained("bert-base-uncased", num_labels=len(label_encoder.classes_))
model.to(device)

# Define optimizer and scheduler
optimizer = AdamW(model.parameters(), lr=2e-5)
epochs = 3
num_training_steps = epochs * len(train_loader)
scheduler = get_scheduler("linear", optimizer=optimizer, num_warmup_steps=0, num_training_steps=num_training_steps)

# Training loop
print("Starting training loop...")
for epoch in range(epochs):
    print(f"\n Epoch {epoch + 1}/{epochs}")
    model.train()

    total_loss = 0
    correct = 0
    total = 0

    for batch in tqdm(train_loader, desc="Training", leave=False):
        batch = {k: v.to(device) for k, v in batch.items()}
        outputs = model(**batch)
        loss = outputs.loss
        logits = outputs.logits

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        scheduler.step()

        total_loss += loss.item()
        predictions = torch.argmax(logits, dim=-1)
        labels = batch["labels"]
        correct += (predictions == labels).sum().item()
        total += labels.size(0)

    avg_loss = total_loss / len(train_loader)
    accuracy = correct / total

    print(f"Epoch {epoch + 1} Complete: Average Loss = {avg_loss:.4f}, Accuracy = {accuracy:.4f}")

print(" Training completed.")
# Save the fine-tuned model
model.save_pretrained("bert_model")
tokenizer.save_pretrained("bert_model")
print("Model saved to bert_model/")

# Evaluate
print("Evaluating model...")
model.eval()
preds, labels = [], []
with torch.no_grad():
    for batch in val_loader:
        batch = {k: v.to(device) for k, v in batch.items()}
        outputs = model(**batch)
        logits = outputs.logits
        preds.extend(torch.argmax(logits, axis=1).cpu().numpy())
        labels.extend(batch["labels"].cpu().numpy())

acc = accuracy_score(labels, preds)
print(f"Validation Accuracy: {acc:.4f}")
print("Classification Report (Validation):")
print(classification_report(labels, preds, target_names=label_encoder.classes_))
