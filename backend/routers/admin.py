from decimal import Decimal
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, case
from backend.database import get_db
from backend.models import (
    User,
    UserRole,
    Auction,
    AuctionStatus,
    Bid,
    AuctionResult,
    ResultStatus,
    Payment,
    PaymentStatus,
    Category,
    AuditLog,
)
from backend.schemas import (
    AdminDashboardData,
    AdminKPIs,
    CategoryDistribution,
    SellerPerformance,
    PaymentStatusSummary,
    AuditLogOut,
    UserOut,
)
from backend.dependencies import require_role

router = APIRouter(prefix="/admin", tags=["Administrator Dashboard & Auditing"])


@router.get("/dashboard", response_model=AdminDashboardData)
def get_admin_dashboard(
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    """Retrieve complete live administrative dashboard metrics and analytics."""
    # User counts
    total_users = db.query(User).count()
    total_buyers = db.query(User).filter(User.role == UserRole.BUYER).count()
    total_sellers = db.query(User).filter(User.role == UserRole.SELLER).count()

    # Auction counts
    total_auctions = db.query(Auction).count()
    active_auctions = db.query(Auction).filter(Auction.status == AuctionStatus.ACTIVE).count()
    closed_auctions = db.query(Auction).filter(Auction.status == AuctionStatus.CLOSED).count()
    unsold_auctions = db.query(Auction).filter(Auction.status == AuctionStatus.UNSOLD).count()

    # Bid count
    total_bids = db.query(Bid).filter(Bid.status == "ACCEPTED").count()

    # Sales volume
    total_sales_volume = (
        db.query(func.coalesce(func.sum(AuctionResult.final_price), 0))
        .filter(AuctionResult.result_status == ResultStatus.WON)
        .scalar()
    )

    # Successful payments volume
    successful_payments_amount = (
        db.query(func.coalesce(func.sum(Payment.amount), 0))
        .filter(Payment.status == PaymentStatus.SUCCESS)
        .scalar()
    )

    kpis = AdminKPIs(
        total_users=total_users,
        total_buyers=total_buyers,
        total_sellers=total_sellers,
        total_auctions=total_auctions,
        active_auctions=active_auctions,
        closed_auctions=closed_auctions,
        unsold_auctions=unsold_auctions,
        total_bids=total_bids,
        total_sales_volume=Decimal(str(total_sales_volume or 0)),
        successful_payments_amount=Decimal(str(successful_payments_amount or 0)),
    )

    # Category distribution
    cat_rows = (
        db.query(
            Category.category_id,
            Category.name,
            func.count(Auction.auction_id).label("auction_count"),
        )
        .outerjoin(Auction, Category.category_id == Auction.category_id)
        .group_by(Category.category_id, Category.name)
        .order_by(desc("auction_count"))
        .all()
    )
    category_distribution = [
        CategoryDistribution(
            category_id=cid, category_name=cname, auction_count=cnt
        )
        for cid, cname, cnt in cat_rows
    ]

    # Seller performance
    seller_rows = (
        db.query(
            User.user_id,
            User.username,
            func.count(Auction.auction_id).label("total_listings"),
            func.sum(case((Auction.status == AuctionStatus.CLOSED, 1), else_=0)).label("closed_listings"),
            func.coalesce(func.sum(AuctionResult.final_price), 0).label("total_volume"),
        )
        .join(Auction, User.user_id == Auction.seller_id)
        .outerjoin(AuctionResult, (Auction.auction_id == AuctionResult.auction_id) & (AuctionResult.result_status == ResultStatus.WON))
        .group_by(User.user_id, User.username)
        .order_by(desc("total_volume"))
        .all()
    )
    seller_performance = [
        SellerPerformance(
            seller_id=uid,
            seller_username=uname,
            total_listings=int(tot or 0),
            closed_listings=int(cls_cnt or 0),
            total_volume=Decimal(str(vol or 0)),
        )
        for uid, uname, tot, cls_cnt, vol in seller_rows
    ]

    # Payment summary
    pay_rows = (
        db.query(
            Payment.status,
            func.count(Payment.payment_id).label("pay_count"),
            func.coalesce(func.sum(Payment.amount), 0).label("pay_amount"),
        )
        .group_by(Payment.status)
        .all()
    )
    payment_summary = [
        PaymentStatusSummary(
            status=status.value if hasattr(status, "value") else str(status),
            count=cnt,
            total_amount=Decimal(str(amt or 0)),
        )
        for status, cnt, amt in pay_rows
    ]

    # Recent audit logs
    audit_rows = (
        db.query(AuditLog)
        .order_by(desc(AuditLog.action_timestamp))
        .limit(20)
        .all()
    )
    recent_audit_logs = [AuditLogOut.model_validate(log) for log in audit_rows]

    return AdminDashboardData(
        kpis=kpis,
        category_distribution=category_distribution,
        seller_performance=seller_performance,
        payment_summary=payment_summary,
        recent_audit_logs=recent_audit_logs,
    )


@router.get("/users", response_model=List[UserOut])
def list_all_users(
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    """List all registered users in the database."""
    return db.query(User).order_by(User.user_id).all()


@router.put("/users/{user_id}/toggle-active", response_model=UserOut)
def toggle_user_active_status(
    user_id: int,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    """Toggle a user account active/deactivated status."""
    if user_id == current_user.user_id:
        raise HTTPException(
            status_code=400, detail="Cannot deactivate your own administrator account."
        )

    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    user.is_active = not user.is_active
    db.commit()
    db.refresh(user)
    return user


@router.get("/audit-logs", response_model=List[AuditLogOut])
def get_audit_logs(
    limit: int = 50,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    """Retrieve recent system audit trail events."""
    return (
        db.query(AuditLog)
        .order_by(desc(AuditLog.action_timestamp))
        .limit(limit)
        .all()
    )
