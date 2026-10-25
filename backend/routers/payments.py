import uuid
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from backend.database import get_db
from backend.models import (
    User,
    UserRole,
    AuctionResult,
    ResultStatus,
    Payment,
    PaymentStatus,
    Auction,
)
from backend.schemas import PaymentCreate, PaymentOut
from backend.dependencies import get_current_user

router = APIRouter(prefix="/payments", tags=["Simulated Payments"])


@router.post("", response_model=PaymentOut, status_code=status.HTTP_201_CREATED)
def submit_simulated_payment(
    req: PaymentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Submits a simulated payment for a won auction result.
    Enforces business rules:
    - User must be the winning bidder.
    - Auction result must be 'WON'.
    - Cannot pay twice for an already settled auction.
    """
    result = (
        db.query(AuctionResult)
        .filter(AuctionResult.result_id == req.result_id)
        .first()
    )
    if not result:
        raise HTTPException(status_code=404, detail="Auction result record not found.")

    if result.winner_id != current_user.user_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to make a payment for this auction result.",
        )

    if result.result_status != ResultStatus.WON:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot process payment for an auction with result status '{result.result_status.value}'.",
        )

    # Check for existing successful payment
    existing_success = (
        db.query(Payment)
        .filter(Payment.result_id == req.result_id, Payment.status == PaymentStatus.SUCCESS)
        .first()
    )
    if existing_success:
        raise HTTPException(
            status_code=409,
            detail=f"This auction result has already been successfully paid for (Ref: {existing_success.transaction_reference}).",
        )

    # Generate unique simulated transaction reference
    prefix = {
        "SIMULATED_UPI": "UPI",
        "SIMULATED_NETBANKING": "NB",
        "SIMULATED_CARD": "CARD",
    }.get(req.payment_method.value, "TXN")
    tx_ref = f"{prefix}/{datetime.now().strftime('%Y%m%d')}/BSPHR{uuid.uuid4().hex[:8].upper()}"

    # Record payment (status SUCCESS for simulation)
    payment = Payment(
        result_id=req.result_id,
        buyer_id=current_user.user_id,
        amount=result.final_price,
        payment_method=req.payment_method,
        status=PaymentStatus.SUCCESS,
        transaction_reference=tx_ref,
        paid_at=datetime.now(),
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)

    # Trigger will automatically send notification!
    auction = db.query(Auction).filter(Auction.auction_id == result.auction_id).first()
    auction_title = auction.title if auction else "Auction"

    return PaymentOut(
        payment_id=payment.payment_id,
        result_id=payment.result_id,
        buyer_id=payment.buyer_id,
        amount=payment.amount,
        payment_method=payment.payment_method,
        status=payment.status,
        transaction_reference=payment.transaction_reference,
        paid_at=payment.paid_at,
        created_at=payment.created_at,
        auction_title=auction_title,
    )


@router.get("/my-payments", response_model=List[PaymentOut])
def get_my_payments(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """List all simulated payments executed by the current user."""
    payments = (
        db.query(Payment, Auction.title.label("auction_title"))
        .join(AuctionResult, Payment.result_id == AuctionResult.result_id)
        .join(Auction, AuctionResult.auction_id == Auction.auction_id)
        .filter(Payment.buyer_id == current_user.user_id)
        .order_by(desc(Payment.created_at))
        .all()
    )

    out = []
    for p, title in payments:
        out.append(
            PaymentOut(
                payment_id=p.payment_id,
                result_id=p.result_id,
                buyer_id=p.buyer_id,
                amount=p.amount,
                payment_method=p.payment_method,
                status=p.status,
                transaction_reference=p.transaction_reference,
                paid_at=p.paid_at,
                created_at=p.created_at,
                auction_title=title,
            )
        )
    return out


@router.get("/{payment_id}", response_model=PaymentOut)
def get_payment_detail(
    payment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve receipt details for a specific payment."""
    row = (
        db.query(Payment, Auction.title.label("auction_title"))
        .join(AuctionResult, Payment.result_id == AuctionResult.result_id)
        .join(Auction, AuctionResult.auction_id == Auction.auction_id)
        .filter(Payment.payment_id == payment_id)
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Payment record not found.")

    p, title = row
    if p.buyer_id != current_user.user_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Access denied to this payment receipt.")

    return PaymentOut(
        payment_id=p.payment_id,
        result_id=p.result_id,
        buyer_id=p.buyer_id,
        amount=p.amount,
        payment_method=p.payment_method,
        status=p.status,
        transaction_reference=p.transaction_reference,
        paid_at=p.paid_at,
        created_at=p.created_at,
        auction_title=title,
    )
