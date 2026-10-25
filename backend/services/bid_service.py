from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import HTTPException
from backend.models import Auction, Bid
from backend.schemas import PlaceBidResponse


def place_bid_transactional(
    db: Session, auction_id: int, bidder_id: int, bid_amount: Decimal
) -> PlaceBidResponse:
    """
    Invokes MySQL stored procedure PlaceBid.
    Executes within an atomic transaction with row-level locking (SELECT ... FOR UPDATE).
    """
    try:
        # Call stored procedure with OUT parameters
        db.execute(
            text(
                "CALL PlaceBid(:auction_id, :bidder_id, :bid_amount, "
                "@out_status_code, @out_status_message, @out_bid_id);"
            ),
            {
                "auction_id": auction_id,
                "bidder_id": bidder_id,
                "bid_amount": float(bid_amount),
            },
        )

        # Retrieve OUT parameters
        result = db.execute(
            text(
                "SELECT @out_status_code AS status_code, "
                "@out_status_message AS status_message, "
                "@out_bid_id AS bid_id;"
            )
        ).fetchone()

        db.commit()

        status_code = result.status_code if result else 500
        status_message = result.status_message if result else "No response from database."
        bid_id = result.bid_id if result else None

        if status_code != 200:
            raise HTTPException(status_code=status_code, detail=status_message)

        # Fetch updated price
        auction = db.query(Auction).filter(Auction.auction_id == auction_id).first()
        current_price = auction.current_price if auction else bid_amount

        return PlaceBidResponse(
            status_code=200,
            status_message=status_message,
            bid_id=bid_id,
            current_price=current_price,
        )

    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Transactional bidding failed: {str(exc)}",
        )
