from typing import List
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from backend.database import get_db
from backend.models import User, Notification
from backend.schemas import NotificationOut
from backend.dependencies import get_current_user

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=List[NotificationOut])
def get_user_notifications(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Retrieve all notifications for the currently logged-in user."""
    return (
        db.query(Notification)
        .filter(Notification.user_id == current_user.user_id)
        .order_by(desc(Notification.created_at))
        .all()
    )


@router.get("/unread-count")
def get_unread_notification_count(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get the count of unread notifications for the current user."""
    count = (
        db.query(Notification)
        .filter(
            Notification.user_id == current_user.user_id,
            Notification.is_read.is_(False),
        )
        .count()
    )
    return {"unread_count": count}


@router.put("/{notification_id}/read", response_model=NotificationOut)
def mark_notification_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Mark a specific notification as read."""
    notif = (
        db.query(Notification)
        .filter(
            Notification.notification_id == notification_id,
            Notification.user_id == current_user.user_id,
        )
        .first()
    )
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found.")

    notif.is_read = True
    db.commit()
    db.refresh(notif)
    return notif


@router.put("/mark-all-read")
def mark_all_notifications_read(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Mark all notifications of the current user as read."""
    db.query(Notification).filter(
        Notification.user_id == current_user.user_id, Notification.is_read.is_(False)
    ).update({"is_read": True})
    db.commit()
    return {"message": "All notifications marked as read."}
