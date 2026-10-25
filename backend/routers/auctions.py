from decimal import Decimal
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import User, UserRole, Category
from backend.schemas import (
    AuctionCreate,
    AuctionUpdate,
    AuctionOut,
    AuctionDetailOut,
    CategoryOut,
    CloseAuctionResponse,
)
from backend.dependencies import (
    get_current_user,
    get_optional_current_user,
    require_role,
)
from backend.services.auction_service import (
    list_auctions,
    get_auction_detail,
    create_auction,
    update_auction,
    cancel_auction,
    close_auction_transactional,
    auto_close_expired_auctions,
)

router = APIRouter(prefix="/auctions", tags=["Auctions"])


@router.get("/categories", response_model=List[CategoryOut])
def get_all_categories(db: Session = Depends(get_db)):
    """Fetch all auction categories."""
    return db.query(Category).order_by(Category.name).all()


@router.get("", response_model=List[AuctionOut])
def get_auctions(
    status: Optional[str] = Query(None, description="Filter by status: ACTIVE, SCHEDULED, CLOSED, etc."),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    search: Optional[str] = Query(None, description="Search keyword in title or description"),
    min_price: Optional[Decimal] = Query(None, description="Minimum price filter"),
    max_price: Optional[Decimal] = Query(None, description="Maximum price filter"),
    sort_by: Optional[str] = Query("closing_soon", description="closing_soon, price_low_high, price_high_low, newest"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    """Retrieve marketplace auctions with rich search, filters and sorting."""
    # Check for auto-closing any expired auctions in real-time
    auto_close_expired_auctions(db)

    user_id = current_user.user_id if current_user else None
    return list_auctions(
        db=db,
        status_filter=status,
        category_id=category_id,
        search=search,
        min_price=min_price,
        max_price=max_price,
        sort_by=sort_by,
        current_user_id=user_id,
    )


@router.post("", response_model=AuctionOut, status_code=status.HTTP_201_CREATED)
def create_new_auction(
    req: AuctionCreate,
    current_user: User = Depends(require_role(UserRole.SELLER, UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    """Create a new auction listing (Seller or Admin only)."""
    auction = create_auction(db=db, seller_id=current_user.user_id, req=req)
    return get_auction_detail(db, auction.auction_id, current_user.user_id)


@router.get("/{auction_id}", response_model=AuctionDetailOut)
def get_auction(
    auction_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    """Get full details of an auction including current highest bid and time remaining."""
    user_id = current_user.user_id if current_user else None
    return get_auction_detail(db, auction_id, user_id)


@router.put("/{auction_id}", response_model=AuctionDetailOut)
def update_auction_listing(
    auction_id: int,
    req: AuctionUpdate,
    current_user: User = Depends(require_role(UserRole.SELLER, UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    """Edit auction listing before bidding starts (Seller owner or Admin)."""
    is_admin = current_user.role == UserRole.ADMIN
    auction = update_auction(
        db=db,
        auction_id=auction_id,
        seller_id=current_user.user_id,
        req=req,
        is_admin=is_admin,
    )
    return get_auction_detail(db, auction.auction_id, current_user.user_id)


@router.post("/{auction_id}/cancel", response_model=AuctionDetailOut)
def cancel_auction_listing(
    auction_id: int,
    current_user: User = Depends(require_role(UserRole.SELLER, UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    """Cancel an auction listing (Seller or Admin)."""
    is_admin = current_user.role == UserRole.ADMIN
    auction = cancel_auction(
        db=db,
        auction_id=auction_id,
        user_id=current_user.user_id,
        is_admin=is_admin,
    )
    return get_auction_detail(db, auction.auction_id, current_user.user_id)


@router.post("/{auction_id}/close", response_model=CloseAuctionResponse)
def trigger_auction_closure(
    auction_id: int,
    current_user: User = Depends(require_role(UserRole.SELLER, UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    """
    Trigger transactional closure of an auction (Admin or Seller owner).
    Determines highest bidder, creates auction_result, updates status, and dispatches notifications.
    """
    return close_auction_transactional(db, auction_id)
