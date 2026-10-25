from typing import List
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import User, Watchlist, Auction
from backend.schemas import WatchlistOut, AuctionOut
from backend.dependencies import get_current_user
from backend.services.auction_service import get_auction_detail

router = APIRouter(prefix="/watchlist", tags=["Watchlist"])


@router.post("/{auction_id}", status_code=status.HTTP_201_CREATED)
def add_to_watchlist(
    auction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add an auction to user's personal watchlist."""
    auction = db.query(Auction).filter(Auction.auction_id == auction_id).first()
    if not auction:
        raise HTTPException(status_code=404, detail="Auction not found.")

    existing = (
        db.query(Watchlist)
        .filter(Watchlist.user_id == current_user.user_id, Watchlist.auction_id == auction_id)
        .first()
    )
    if existing:
        return {"message": "Auction is already in your watchlist.", "watchlist_id": existing.watchlist_id}

    item = Watchlist(user_id=current_user.user_id, auction_id=auction_id)
    db.add(item)
    db.commit()
    db.refresh(item)
    return {"message": "Auction successfully added to watchlist.", "watchlist_id": item.watchlist_id}


@router.delete("/{auction_id}", status_code=status.HTTP_200_OK)
def remove_from_watchlist(
    auction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Remove an auction from user's personal watchlist."""
    item = (
        db.query(Watchlist)
        .filter(Watchlist.user_id == current_user.user_id, Watchlist.auction_id == auction_id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Auction is not in your watchlist.")

    db.delete(item)
    db.commit()
    return {"message": "Auction removed from watchlist."}


@router.get("", response_model=List[WatchlistOut])
def get_my_watchlist(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Retrieve all auctions currently bookmarked in user's watchlist."""
    watchlist_items = (
        db.query(Watchlist)
        .filter(Watchlist.user_id == current_user.user_id)
        .order_by(Watchlist.created_at.desc())
        .all()
    )

    out = []
    for item in watchlist_items:
        auc_detail = get_auction_detail(db, item.auction_id, current_user.user_id)
        out.append(
            WatchlistOut(
                watchlist_id=item.watchlist_id,
                user_id=item.user_id,
                auction_id=item.auction_id,
                created_at=item.created_at,
                auction=auc_detail,
            )
        )
    return out
