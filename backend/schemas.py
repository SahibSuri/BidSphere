from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from backend.models import (
    UserRole,
    AuctionStatus,
    BidStatus,
    ResultStatus,
    PaymentMethod,
    PaymentStatus,
    NotificationType,
    AuditOperation,
)


# -----------------------------------------------------------------------------
# Base Schema Configuration
# -----------------------------------------------------------------------------
class ORMBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# -----------------------------------------------------------------------------
# User Schemas
# -----------------------------------------------------------------------------
class UserRegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)
    full_name: str = Field(..., min_length=2, max_length=100)
    role: UserRole = UserRole.BUYER
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None


class UserLoginRequest(BaseModel):
    username_or_email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    username: str
    email: str
    full_name: str
    role: UserRole


class UserOut(ORMBase):
    user_id: int
    username: str
    email: str
    full_name: str
    role: UserRole
    phone: Optional[str] = None
    address: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None


# -----------------------------------------------------------------------------
# Category Schemas
# -----------------------------------------------------------------------------
class CategoryOut(ORMBase):
    category_id: int
    name: str
    description: Optional[str] = None
    icon: str
    created_at: datetime


class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    description: Optional[str] = Field(None, max_length=255)
    icon: str = Field("tag", max_length=50)


# -----------------------------------------------------------------------------
# Auction Schemas
# -----------------------------------------------------------------------------
class AuctionCreate(BaseModel):
    category_id: int
    title: str = Field(..., min_length=3, max_length=150)
    description: str = Field(..., min_length=10)
    starting_price: Decimal = Field(..., gt=0)
    bid_increment: Decimal = Field(Decimal("50.00"), gt=0)
    start_time: datetime
    end_time: datetime
    image_url: Optional[str] = Field(None, max_length=500)


class AuctionUpdate(BaseModel):
    category_id: Optional[int] = None
    title: Optional[str] = Field(None, min_length=3, max_length=150)
    description: Optional[str] = Field(None, min_length=10)
    starting_price: Optional[Decimal] = Field(None, gt=0)
    bid_increment: Optional[Decimal] = Field(None, gt=0)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    image_url: Optional[str] = Field(None, max_length=500)


class AuctionOut(ORMBase):
    auction_id: int
    seller_id: int
    category_id: int
    title: str
    description: str
    starting_price: Decimal
    current_price: Decimal
    bid_increment: Decimal
    status: AuctionStatus
    start_time: datetime
    end_time: datetime
    image_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    category_name: Optional[str] = None
    seller_username: Optional[str] = None
    total_bids: Optional[int] = 0
    is_in_watchlist: Optional[bool] = False


class AuctionDetailOut(AuctionOut):
    seller_full_name: Optional[str] = None
    min_next_bid: Decimal
    seconds_remaining: Optional[int] = 0
    highest_bidder_id: Optional[int] = None
    highest_bidder_username: Optional[str] = None


# -----------------------------------------------------------------------------
# Bid Schemas
# -----------------------------------------------------------------------------
class BidCreate(BaseModel):
    bid_amount: Decimal = Field(..., gt=0)


class BidOut(ORMBase):
    bid_id: int
    auction_id: int
    bidder_id: int
    bid_amount: Decimal
    bid_time: datetime
    status: BidStatus
    created_at: datetime
    bidder_username: Optional[str] = None


class PlaceBidResponse(BaseModel):
    status_code: int
    status_message: str
    bid_id: Optional[int] = None
    current_price: Optional[Decimal] = None


# -----------------------------------------------------------------------------
# Watchlist Schemas
# -----------------------------------------------------------------------------
class WatchlistOut(ORMBase):
    watchlist_id: int
    user_id: int
    auction_id: int
    created_at: datetime
    auction: Optional[AuctionOut] = None


# -----------------------------------------------------------------------------
# Auction Result Schemas
# -----------------------------------------------------------------------------
class AuctionResultOut(ORMBase):
    result_id: int
    auction_id: int
    winner_id: Optional[int] = None
    winning_bid_id: Optional[int] = None
    final_price: Decimal
    closed_at: datetime
    result_status: ResultStatus
    created_at: datetime
    winner_username: Optional[str] = None
    winner_email: Optional[str] = None
    auction_title: Optional[str] = None
    payment_status: Optional[str] = "NOT_INITIATED"
    payment_id: Optional[int] = None


class CloseAuctionResponse(BaseModel):
    status_code: int
    status_message: str
    result_id: Optional[int] = None


# -----------------------------------------------------------------------------
# Payment Schemas
# -----------------------------------------------------------------------------
class PaymentCreate(BaseModel):
    result_id: int
    payment_method: PaymentMethod = PaymentMethod.SIMULATED_UPI


class PaymentOut(ORMBase):
    payment_id: int
    result_id: int
    buyer_id: int
    amount: Decimal
    payment_method: PaymentMethod
    status: PaymentStatus
    transaction_reference: str
    paid_at: Optional[datetime] = None
    created_at: datetime
    auction_title: Optional[str] = None


# -----------------------------------------------------------------------------
# Notification Schemas
# -----------------------------------------------------------------------------
class NotificationOut(ORMBase):
    notification_id: int
    user_id: int
    auction_id: Optional[int] = None
    title: str
    message: str
    is_read: bool
    notification_type: NotificationType
    created_at: datetime


# -----------------------------------------------------------------------------
# Audit Log Schemas
# -----------------------------------------------------------------------------
class AuditLogOut(ORMBase):
    log_id: int
    table_name: str
    operation: AuditOperation
    record_id: int
    changed_by: Optional[str] = None
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    action_timestamp: datetime


# -----------------------------------------------------------------------------
# Dashboard & Admin Metrics Schemas
# -----------------------------------------------------------------------------
class AdminKPIs(BaseModel):
    total_users: int
    total_buyers: int
    total_sellers: int
    total_auctions: int
    active_auctions: int
    closed_auctions: int
    unsold_auctions: int
    total_bids: int
    total_sales_volume: Decimal
    successful_payments_amount: Decimal


class CategoryDistribution(BaseModel):
    category_id: int
    category_name: str
    auction_count: int


class SellerPerformance(BaseModel):
    seller_id: int
    seller_username: str
    total_listings: int
    closed_listings: int
    total_volume: Decimal


class BuyerActivity(BaseModel):
    buyer_id: int
    buyer_username: str
    total_bids: int
    auctions_participated: int
    auctions_won: int
    total_spent: Decimal


class PaymentStatusSummary(BaseModel):
    status: str
    count: int
    total_amount: Decimal


class AdminDashboardData(BaseModel):
    kpis: AdminKPIs
    category_distribution: List[CategoryDistribution]
    seller_performance: List[SellerPerformance]
    payment_summary: List[PaymentStatusSummary]
    recent_audit_logs: List[AuditLogOut]


# -----------------------------------------------------------------------------
# System Health Schema
# -----------------------------------------------------------------------------
class HealthResponse(BaseModel):
    status: str
    app_name: str
    environment: str
    database: Dict[str, Any]
    timestamp: datetime
