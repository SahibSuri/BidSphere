from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from backend.database import get_db
from backend.models import User, UserRole, Bid, Auction
from backend.schemas import BidCreate, BidOut, PlaceBidResponse
from backend.dependencies import get_current_user, require_role
from backend.services.bid_service import place_bid_transactional

router = APIRouter(prefix="/bids", tags=["Bidding"])


@router.post("/auctions/{auction_id}", response_model=PlaceBidResponse, status_code=status.HTTP_201_CREATED)
def place_bid(
    auction_id: int,
    req: BidCreate,
    current_user: User = Depends(require_role(UserRole.BUYER, UserRole.SELLER, UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    """
    Submit a bid on an auction.
    Executed through MySQL stored procedure PlaceBid with row-level locking (SELECT ... FOR UPDATE).
    """
    return place_bid_transactional(
        db=db,
        auction_id=auction_id,
        bidder_id=current_user.user_id,
        bid_amount=req.bid_amount,
    )


@router.get("/auctions/{auction_id}", response_model=List[BidOut])
def get_auction_bids(auction_id: int, db: Session = Depends(get_db)):
    """Retrieve full bid history for a specific auction in reverse chronological order."""
    bids = (
        db.query(Bid, User.username.label("bidder_username"))
        .join(User, Bid.bidder_id == User.user_id)
        .filter(Bid.auction_id == auction_id)
        .order_by(desc(Bid.bid_time))
        .all()
    )

    result = []
    for bid, username in bids:
        b_dict = {
            "bid_id": bid.bid_id,
            "auction_id": bid.auction_id,
            "bidder_id": bid.bidder_id,
            "bid_amount": bid.bid_amount,
            "bid_time": bid.bid_time,
            "status": bid.status,
            "created_at": bid.created_at,
            "bidder_username": username,
        }
        result.append(BidOut(**b_dict))
    return result


@router.get("/my-bids", response_model=List[BidOut])
def get_my_bids(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Retrieve all bids placed by the currently authenticated user."""
    bids = (
        db.query(Bid, User.username.label("bidder_username"))
        .join(User, Bid.bidder_id == User.user_id)
        .filter(Bid.bidder_id == current_user.user_id)
        .order_by(desc(Bid.bid_time))
        .all()
    )

    result = []
    for bid, username in bids:
        b_dict = {
            "bid_id": bid.bid_id,
            "auction_id": bid.auction_id,
            "bidder_id": bid.bidder_id,
            "bid_amount": bid.bid_amount,
            "bid_time": bid.bid_time,
            "status": bid.status,
            "created_at": bid.created_at,
            "bidder_username": username,
        }
        result.append(BidOut(**b_dict))
    return result
