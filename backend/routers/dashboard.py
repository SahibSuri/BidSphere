from decimal import Decimal
from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
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
)
from backend.schemas import (
    AuctionOut,
    AuctionResultOut,
    BidOut,
)
from backend.dependencies import get_current_user
from backend.services.auction_service import list_auctions

router = APIRouter(prefix="/dashboard", tags=["Dashboards & Results"])


@router.get("/seller")
def get_seller_dashboard(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Retrieves seller dashboard metrics, listings and bidding activity."""
    # Seller listings
    listings = list_auctions(db=db, seller_id=current_user.user_id, sort_by="newest")

    # Counts
    total_listings = len(listings)
    active_listings = sum(1 for a in listings if a.status == AuctionStatus.ACTIVE)
    closed_listings = sum(1 for a in listings if a.status == AuctionStatus.CLOSED)

    # Total volume from closed won auctions
    won_volume = (
        db.query(func.coalesce(func.sum(AuctionResult.final_price), 0))
        .join(Auction, AuctionResult.auction_id == Auction.auction_id)
        .filter(Auction.seller_id == current_user.user_id, AuctionResult.result_status == ResultStatus.WON)
        .scalar()
    )

    # Recent bids on seller's items
    recent_bids_rows = (
        db.query(Bid, User.username.label("bidder_username"), Auction.title.label("auction_title"))
        .join(User, Bid.bidder_id == User.user_id)
        .join(Auction, Bid.auction_id == Auction.auction_id)
        .filter(Auction.seller_id == current_user.user_id)
        .order_by(desc(Bid.bid_time))
        .limit(10)
        .all()
    )

    recent_bids = [
        {
            "bid_id": b.bid_id,
            "auction_id": b.auction_id,
            "auction_title": title,
            "bidder_username": uname,
            "bid_amount": b.bid_amount,
            "bid_time": b.bid_time,
            "status": b.status,
        }
        for b, uname, title in recent_bids_rows
    ]

    return {
        "total_listings": total_listings,
        "active_listings": active_listings,
        "closed_listings": closed_listings,
        "total_sales_volume": Decimal(str(won_volume or 0)),
        "listings": listings,
        "recent_bids": recent_bids,
    }


@router.get("/buyer")
def get_buyer_dashboard(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Retrieves buyer dashboard metrics, active bids, and won auctions."""
    # All bids placed by buyer
    total_bids = db.query(Bid).filter(Bid.bidder_id == current_user.user_id).count()

    # Active auctions where user has active bids
    active_bids_auctions = (
        db.query(Auction, func.max(Bid.bid_amount).label("my_highest_bid"))
        .join(Bid, Auction.auction_id == Bid.auction_id)
        .filter(Bid.bidder_id == current_user.user_id, Auction.status == AuctionStatus.ACTIVE)
        .group_by(Auction.auction_id)
        .all()
    )

    active_participations = [
        {
            "auction_id": a.auction_id,
            "title": a.title,
            "current_price": a.current_price,
            "my_highest_bid": my_bid,
            "end_time": a.end_time,
            "is_winning": (a.current_price == my_bid),
        }
        for a, my_bid in active_bids_auctions
    ]

    # Won auctions
    won_rows = (
        db.query(
            AuctionResult,
            Auction.title.label("auction_title"),
            Payment.payment_id,
            Payment.status.label("payment_status"),
        )
        .join(Auction, AuctionResult.auction_id == Auction.auction_id)
        .outerjoin(Payment, AuctionResult.result_id == Payment.result_id)
        .filter(AuctionResult.winner_id == current_user.user_id, AuctionResult.result_status == ResultStatus.WON)
        .all()
    )

    won_auctions = [
        {
            "result_id": r.result_id,
            "auction_id": r.auction_id,
            "auction_title": title,
            "final_price": r.final_price,
            "closed_at": r.closed_at,
            "payment_id": pid,
            "payment_status": p_status.value if p_status else "PENDING_PAYMENT",
        }
        for r, title, pid, p_status in won_rows
    ]

    return {
        "total_bids_placed": total_bids,
        "active_auctions_count": len(active_participations),
        "won_auctions_count": len(won_auctions),
        "active_participations": active_participations,
        "won_auctions": won_auctions,
    }


@router.get("/results", response_model=List[AuctionResultOut])
def get_all_auction_results(db: Session = Depends(get_db)):
    """Retrieve all final auction closure results."""
    rows = (
        db.query(
            AuctionResult,
            Auction.title.label("auction_title"),
            User.username.label("winner_username"),
            User.email.label("winner_email"),
            Payment.payment_id,
            Payment.status.label("payment_status"),
        )
        .join(Auction, AuctionResult.auction_id == Auction.auction_id)
        .outerjoin(User, AuctionResult.winner_id == User.user_id)
        .outerjoin(Payment, AuctionResult.result_id == Payment.result_id)
        .order_by(desc(AuctionResult.closed_at))
        .all()
    )

    out = []
    for r, title, uname, uemail, pid, pstatus in rows:
        out.append(
            AuctionResultOut(
                result_id=r.result_id,
                auction_id=r.auction_id,
                winner_id=r.winner_id,
                winning_bid_id=r.winning_bid_id,
                final_price=r.final_price,
                closed_at=r.closed_at,
                result_status=r.result_status,
                created_at=r.created_at,
                winner_username=uname,
                winner_email=uemail,
                auction_title=title,
                payment_id=pid,
                payment_status=pstatus.value if pstatus else "NOT_INITIATED",
            )
        )
    return out
