# app/routers/posts.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import database, models
from datetime import datetime
from transformers import BertTokenizer, BertForSequenceClassification
import torch
import joblib

router = APIRouter()

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load fine-tuned BERT model
model_path = "bert_model"
model = BertForSequenceClassification.from_pretrained(model_path)
tokenizer = BertTokenizer.from_pretrained(model_path)
model.to(device)
model.eval()

# Load label encoder
label_encoder = joblib.load("app/ml/label_encoder.joblib")


@router.post("")
def create_post(post: dict, db: Session = Depends(database.get_db)):
    username = post.get("Username")
    content = post.get("Content")

    if not username or not content:
        raise HTTPException(status_code=400, detail="Missing username or content")
    
    user = db.query(models.User).filter_by(Username=username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Run BERT model inference
    tokens = tokenizer(content, return_tensors="pt", truncation=True, padding=True, max_length=128)
    tokens = {k: v.to(device) for k, v in tokens.items()}
    with torch.no_grad():
        outputs = model(**tokens)
        predicted_class_id = outputs.logits.argmax(dim=-1).item()

    # Decode the class label
    predicted_label = label_encoder.inverse_transform([predicted_class_id])[0]
    is_abusive = predicted_label != "not_cyberbullying"

    if is_abusive:
        return {
            "message": f"Post blocked due to detected cyberbullying: {predicted_label}",
            "prediction": predicted_label,
            "is_abusive": True
        }
    
     # Only save safe posts
    new_post = models.Post(
        UserID=user.UserID,
        Content=content,
        Timestamp=datetime.utcnow(),
        IsAbusive=False
    )
    

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return {
        "message": "Post submitted successfully",
        "prediction": predicted_label,
        "is_abusive": False
    }



@router.get("/all")
def get_all_posts(db: Session = Depends(database.get_db)):
    results = (
        db.query(models.Post, models.User.Username)
        .join(models.User, models.User.UserID == models.Post.UserID)
        .order_by(models.Post.Timestamp.desc())
        .all()
    )

    return {
        "posts": [
            {
                "post_id": post.PostID,
                "username": username or "anonymous",
                "content": post.Content,
                "timestamp": post.Timestamp.strftime("%Y-%m-%d %H:%M:%S")
            }
            for post, username in results
        ]
    }

