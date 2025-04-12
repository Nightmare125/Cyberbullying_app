from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from datetime import datetime
from app.db import models, database

router = APIRouter()

# Dependency for database session
get_db = database.get_db


# ✅ Submit a report for a post
@router.post("/{post_id}")
def report_post(post_id: int, db: Session = Depends(get_db)):
    # Prevent duplicate reports
    existing = db.query(models.Report).filter_by(PostID=post_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="This post has already been reported.")

    report = models.Report(
        PostID=post_id,
        Status=False,
        Timestamp=datetime.utcnow()
    )
    db.add(report)
    db.commit()
    return {"message": "Post reported successfully"}


# ✅ View all reports (admin only)
@router.get("")
def list_reports(request: Request, db: Session = Depends(get_db)):
    # Simulated admin check
    is_admin = request.session.get("is_admin", False)
    if not is_admin:
        raise HTTPException(status_code=403, detail="Admins only")

    # Join reports with posts and users
    reports = (
        db.query(models.Report, models.Post.Content, models.User.Username)
        .join(models.Post, models.Report.PostID == models.Post.PostID)
        .join(models.User, models.Post.UserID == models.User.UserID)
        .order_by(models.Report.Timestamp.desc())
        .all()
    )

    result = []
    for report, content, username in reports:
        result.append({
            "report_id": report.ReportID,
            "post_id": report.PostID,
            "status": report.Status,
            "timestamp": report.Timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "content": content,
            "username": username
        })

    return result


# ✅ Resolve a report (mark as reviewed)
@router.put("/{report_id}")
def resolve_report(report_id: int, db: Session = Depends(get_db)):
    report = db.query(models.Report).filter_by(ReportID=report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    report.Status = True
    db.commit()
    return {"message": "Report marked as resolved"}


# ✅ Delete a post and all reports associated with it
@router.delete("/post/{post_id}")
def delete_reported_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter_by(PostID=post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Delete associated reports
    db.query(models.Report).filter_by(PostID=post_id).delete()

    # Delete the post
    db.delete(post)
    db.commit()
    return {"message": "Post and related reports deleted"}
