from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import text, desc, asc, func, or_
from fastapi import HTTPException, status
from backend.models import (
    Auction,
    AuctionStatus,
    Category,
    User,
    Bid,
    Watchlist,
    AuctionResult,
    ResultStatus,
)
from backend.schemas import (
    AuctionCreate,
    AuctionUpdate,
    AuctionOut,
    AuctionDetailOut,
    CloseAuctionResponse,
)


def list_auctions(
    db: Session,
    status_filter: Optional[str] = None,
    category_id: Optional[int] = None,
    search: Optional[str] = None,
    min_price: Optional[Decimal] = None,
    max_price: Optional[Decimal] = None,
    sort_by: Optional[str] = "closing_soon",
    current_user_id: Optional[int] = None,
    seller_id: Optional[int] = None,
) -> List[AuctionOut]:
    """Lists auctions with search, filtering, and sorting."""
    query = db.query(
        Auction,
        Category.name.label("category_name"),
        User.username.label("seller_username"),
        func.count(Bid.bid_id).label("total_bids"),
    ).join(Category, Auction.category_id == Category.category_id
    ).join(User, Auction.seller_id == User.user_id
    ).outerjoin(Bid, (Auction.auction_id == Bid.auction_id) & (Bid.status == "ACCEPTED")
    ).group_by(Auction.auction_id, Category.name, User.username)

    if status_filter:
        query = query.filter(Auction.status == status_filter.upper())
    if category_id:
        query = query.filter(Auction.category_id == category_id)
    if seller_id:
        query = query.filter(Auction.seller_id == seller_id)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(Auction.title.ilike(search_term), Auction.description.ilike(search_term))
        )
    if min_price is not None:
        query = query.filter(Auction.current_price >= min_price)
    if max_price is not None:
        query = query.filter(Auction.current_price <= max_price)

    # Sorting
    if sort_by == "closing_soon":
        query = query.order_by(asc(Auction.end_time))
    elif sort_by == "price_low_high":
        query = query.order_by(asc(Auction.current_price))
    elif sort_by == "price_high_low":
        query = query.order_by(desc(Auction.current_price))
    elif sort_by == "newest":
        query = query.order_by(desc(Auction.created_at))
    else:
        query = query.order_by(desc(Auction.auction_id))

    rows = query.all()

    # Get watchlist items for current user if authenticated
    watchlist_set = set()
    if current_user_id:
        watchlist_records = (
            db.query(Watchlist.auction_id)
            .filter(Watchlist.user_id == current_user_id)
            .all()
        )
        watchlist_set = {r[0] for r in watchlist_records}

    results = []
    for auction, cat_name, seller_name, bid_cnt in rows:
        results.append(
            AuctionOut(
                auction_id=auction.auction_id,
                seller_id=auction.seller_id,
                category_id=auction.category_id,
                title=auction.title,
                description=auction.description,
                starting_price=auction.starting_price,
                current_price=auction.current_price,
                bid_increment=auction.bid_increment,
                status=auction.status,
                start_time=auction.start_time,
                end_time=auction.end_time,
                image_url=auction.image_url,
                created_at=auction.created_at,
                updated_at=auction.updated_at,
                category_name=cat_name,
                seller_username=seller_name,
                total_bids=bid_cnt or 0,
                is_in_watchlist=auction.auction_id in watchlist_set,
            )
        )
    return results


def get_auction_detail(
    db: Session, auction_id: int, current_user_id: Optional[int] = None
) -> AuctionDetailOut:
    """Retrieves full details of a specific auction."""
    row = (
        db.query(
            Auction,
            Category.name.label("category_name"),
            User.username.label("seller_username"),
            User.full_name.label("seller_full_name"),
            func.count(Bid.bid_id).label("total_bids"),
        )
        .join(Category, Auction.category_id == Category.category_id)
        .join(User, Auction.seller_id == User.user_id)
        .outerjoin(Bid, (Auction.auction_id == Bid.auction_id) & (Bid.status == "ACCEPTED"))
        .filter(Auction.auction_id == auction_id)
        .group_by(Auction.auction_id, Category.name, User.username, User.full_name)
        .first()
    )

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Auction #{auction_id} not found.",
        )

    auction, cat_name, seller_username, seller_full_name, bid_cnt = row

    # Highest bid and bidder
    highest_bid = (
        db.query(Bid, User.username)
        .join(User, Bid.bidder_id == User.user_id)
        .filter(Bid.auction_id == auction_id, Bid.status == "ACCEPTED")
        .order_by(desc(Bid.bid_amount))
        .first()
    )

    highest_bidder_id = highest_bid[0].bidder_id if highest_bid else None
    highest_bidder_username = highest_bid[1] if highest_bid else None

    # Watchlist status
    is_in_watchlist = False
    if current_user_id:
        is_in_watchlist = bool(
            db.query(Watchlist)
            .filter(
                Watchlist.auction_id == auction_id, Watchlist.user_id == current_user_id
            )
            .first()
        )

    now = datetime.now()
    seconds_remaining = 0
    if auction.end_time and auction.end_time > now:
        seconds_remaining = int((auction.end_time - now).total_seconds())

    min_next_bid = (
        auction.starting_price
        if (bid_cnt or 0) == 0
        else auction.current_price + auction.bid_increment
    )

    return AuctionDetailOut(
        auction_id=auction.auction_id,
        seller_id=auction.seller_id,
        category_id=auction.category_id,
        title=auction.title,
        description=auction.description,
        starting_price=auction.starting_price,
        current_price=auction.current_price,
        bid_increment=auction.bid_increment,
        status=auction.status,
        start_time=auction.start_time,
        end_time=auction.end_time,
        image_url=auction.image_url,
        created_at=auction.created_at,
        updated_at=auction.updated_at,
        category_name=cat_name,
        seller_username=seller_username,
        seller_full_name=seller_full_name,
        total_bids=bid_cnt or 0,
        is_in_watchlist=is_in_watchlist,
        min_next_bid=min_next_bid,
        seconds_remaining=seconds_remaining,
        highest_bidder_id=highest_bidder_id,
        highest_bidder_username=highest_bidder_username,
    )


def create_auction(db: Session, seller_id: int, req: AuctionCreate) -> Auction:
    """Creates a new auction listing."""
    if req.end_time <= req.start_time:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Auction end time must be after start time.",
        )

    # Validate category exists
    cat = db.query(Category).filter(Category.category_id == req.category_id).first()
    if not cat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category #{req.category_id} not found.",
        )

    # Determine initial status
    now = datetime.now()
    initial_status = AuctionStatus.ACTIVE if req.start_time <= now else AuctionStatus.SCHEDULED

    auction = Auction(
        seller_id=seller_id,
        category_id=req.category_id,
        title=req.title,
        description=req.description,
        starting_price=req.starting_price,
        current_price=req.starting_price,
        bid_increment=req.bid_increment,
        status=initial_status,
        start_time=req.start_time,
        end_time=req.end_time,
        image_url=req.image_url,
    )
    db.add(auction)
    db.commit()
    db.refresh(auction)
    return auction


def update_auction(
    db: Session, auction_id: int, seller_id: int, req: AuctionUpdate, is_admin: bool = False
) -> Auction:
    """Updates an auction if no bids have been placed and auction is eligible."""
    auction = db.query(Auction).filter(Auction.auction_id == auction_id).first()
    if not auction:
        raise HTTPException(status_code=404, detail="Auction not found.")

    if not is_admin and auction.seller_id != seller_id:
        raise HTTPException(status_code=403, detail="You do not own this auction.")

    # Check if bids exist
    bid_count = db.query(Bid).filter(Bid.auction_id == auction_id).count()
    if bid_count > 0:
        raise HTTPException(
            status_code=400,
            detail="Cannot edit auction once bidding has commenced.",
        )

    if auction.status not in [AuctionStatus.SCHEDULED, AuctionStatus.ACTIVE]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot edit auction with status '{auction.status.value}'.",
        )

    if req.title is not None:
        auction.title = req.title
    if req.description is not None:
        auction.description = req.description
    if req.category_id is not None:
        auction.category_id = req.category_id
    if req.starting_price is not None:
        auction.starting_price = req.starting_price
        auction.current_price = req.starting_price
    if req.bid_increment is not None:
        auction.bid_increment = req.bid_increment
    if req.start_time is not None:
        auction.start_time = req.start_time
    if req.end_time is not None:
        auction.end_time = req.end_time
    if req.image_url is not None:
        auction.image_url = req.image_url

    if auction.end_time <= auction.start_time:
        raise HTTPException(
            status_code=422, detail="End time must be after start time."
        )

    db.commit()
    db.refresh(auction)
    return auction


def cancel_auction(
    db: Session, auction_id: int, user_id: int, is_admin: bool = False
) -> Auction:
    """Cancels an auction according to business rules."""
    auction = db.query(Auction).filter(Auction.auction_id == auction_id).first()
    if not auction:
        raise HTTPException(status_code=404, detail="Auction not found.")

    if not is_admin and auction.seller_id != user_id:
        raise HTTPException(status_code=403, detail="You do not own this auction.")

    if auction.status in [AuctionStatus.CLOSED, AuctionStatus.CANCELLED, AuctionStatus.UNSOLD]:
        raise HTTPException(
            status_code=400, detail=f"Auction already finalized as {auction.status.value}."
        )

    # Check bids
    bid_count = db.query(Bid).filter(Bid.auction_id == auction_id).count()
    if bid_count > 0 and not is_admin:
        raise HTTPException(
            status_code=400,
            detail="Sellers cannot cancel an auction after bids have been submitted. Contact admin.",
        )

    auction.status = AuctionStatus.CANCELLED
    db.commit()
    db.refresh(auction)
    return auction


def close_auction_transactional(db: Session, auction_id: int) -> CloseAuctionResponse:
    """Calls MySQL stored procedure CloseAuction transactionally."""
    try:
        db.execute(
            text(
                "CALL CloseAuction(:auction_id, @out_status_code, "
                "@out_status_message, @out_result_id);"
            ),
            {"auction_id": auction_id},
        )
        result = db.execute(
            text(
                "SELECT @out_status_code AS status_code, "
                "@out_status_message AS status_message, "
                "@out_result_id AS result_id;"
            )
        ).fetchone()

        db.commit()

        status_code = result.status_code if result else 500
        status_message = result.status_message if result else "Database error."
        result_id = result.result_id if result else None

        if status_code != 200:
            raise HTTPException(status_code=status_code, detail=status_message)

        return CloseAuctionResponse(
            status_code=200,
            status_message=status_message,
            result_id=result_id,
        )
    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Failed to close auction: {str(exc)}"
        )


def auto_close_expired_auctions(db: Session) -> int:
    """Closes all active auctions whose end_time has passed."""
    now = datetime.now()
    expired_auctions = (
        db.query(Auction.auction_id)
        .filter(Auction.status == AuctionStatus.ACTIVE, Auction.end_time <= now)
        .all()
    )
    closed_count = 0
    for (a_id,) in expired_auctions:
        try:
            close_auction_transactional(db, a_id)
            closed_count += 1
        except Exception:
            continue
    return closed_count
