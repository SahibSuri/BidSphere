import enum
from datetime import datetime
from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    String,
    Text,
    Numeric,
    DateTime,
    Boolean,
    ForeignKey,
    Enum,
    TIMESTAMP,
    JSON,
    text,
)
from sqlalchemy.orm import relationship
from backend.database import Base


class UserRole(str, enum.Enum):
    BUYER = "BUYER"
    SELLER = "SELLER"
    ADMIN = "ADMIN"


class AuctionStatus(str, enum.Enum):
    SCHEDULED = "SCHEDULED"
    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"
    UNSOLD = "UNSOLD"


class BidStatus(str, enum.Enum):
    ACCEPTED = "ACCEPTED"
    OUTBID = "OUTBID"
    CANCELLED = "CANCELLED"


class ResultStatus(str, enum.Enum):
    WON = "WON"
    UNSOLD = "UNSOLD"
    CANCELLED = "CANCELLED"


class PaymentMethod(str, enum.Enum):
    SIMULATED_UPI = "SIMULATED_UPI"
    SIMULATED_NETBANKING = "SIMULATED_NETBANKING"
    SIMULATED_CARD = "SIMULATED_CARD"


class PaymentStatus(str, enum.Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class NotificationType(str, enum.Enum):
    BID_PLACED = "BID_PLACED"
    OUTBID = "OUTBID"
    AUCTION_WON = "AUCTION_WON"
    AUCTION_CLOSED = "AUCTION_CLOSED"
    AUCTION_UNSOLD = "AUCTION_UNSOLD"
    PAYMENT_RECEIVED = "PAYMENT_RECEIVED"


class AuditOperation(str, enum.Enum):
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


class User(Base):
    __tablename__ = "users"

    user_id = Column(BigInteger, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False, unique=True, index=True)
    email = Column(String(100), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.BUYER)
    phone = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    updated_at = Column(
        TIMESTAMP,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
        nullable=False,
    )

    auctions_created = relationship("Auction", back_populates="seller")
    bids = relationship("Bid", back_populates="bidder")
    watchlist = relationship("Watchlist", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="buyer")
    auctions_won = relationship("AuctionResult", back_populates="winner")


class Category(Base):
    __tablename__ = "categories"

    category_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(String(255), nullable=True)
    icon = Column(String(50), nullable=False, default="tag")
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), nullable=False)

    auctions = relationship("Auction", back_populates="category")


class Auction(Base):
    __tablename__ = "auctions"

    auction_id = Column(BigInteger, primary_key=True, autoincrement=True)
    seller_id = Column(BigInteger, ForeignKey("users.user_id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.category_id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False)
    title = Column(String(150), nullable=False)
    description = Column(Text, nullable=False)
    starting_price = Column(Numeric(12, 2), nullable=False)
    current_price = Column(Numeric(12, 2), nullable=False)
    bid_increment = Column(Numeric(10, 2), nullable=False, default=50.00)
    status = Column(Enum(AuctionStatus), nullable=False, default=AuctionStatus.SCHEDULED)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    image_url = Column(String(500), nullable=True)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    updated_at = Column(
        TIMESTAMP,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
        nullable=False,
    )

    seller = relationship("User", back_populates="auctions_created")
    category = relationship("Category", back_populates="auctions")
    bids = relationship("Bid", back_populates="auction", cascade="all, delete-orphan")
    watchlist_entries = relationship("Watchlist", back_populates="auction", cascade="all, delete-orphan")
    result = relationship("AuctionResult", back_populates="auction", uselist=False)


class Bid(Base):
    __tablename__ = "bids"

    bid_id = Column(BigInteger, primary_key=True, autoincrement=True)
    auction_id = Column(BigInteger, ForeignKey("auctions.auction_id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    bidder_id = Column(BigInteger, ForeignKey("users.user_id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False)
    bid_amount = Column(Numeric(12, 2), nullable=False)
    bid_time = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    status = Column(Enum(BidStatus), nullable=False, default=BidStatus.ACCEPTED)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), nullable=False)

    auction = relationship("Auction", back_populates="bids")
    bidder = relationship("User", back_populates="bids")


class Watchlist(Base):
    __tablename__ = "watchlist"

    watchlist_id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.user_id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    auction_id = Column(BigInteger, ForeignKey("auctions.auction_id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), nullable=False)

    user = relationship("User", back_populates="watchlist")
    auction = relationship("Auction", back_populates="watchlist_entries")


class AuctionResult(Base):
    __tablename__ = "auction_results"

    result_id = Column(BigInteger, primary_key=True, autoincrement=True)
    auction_id = Column(BigInteger, ForeignKey("auctions.auction_id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False, unique=True)
    winner_id = Column(BigInteger, ForeignKey("users.user_id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=True)
    winning_bid_id = Column(BigInteger, ForeignKey("bids.bid_id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=True)
    final_price = Column(Numeric(12, 2), nullable=False, default=0.00)
    closed_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    result_status = Column(Enum(ResultStatus), nullable=False)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), nullable=False)

    auction = relationship("Auction", back_populates="result")
    winner = relationship("User", back_populates="auctions_won")
    winning_bid = relationship("Bid")
    payments = relationship("Payment", back_populates="result")


class Payment(Base):
    __tablename__ = "payments"

    payment_id = Column(BigInteger, primary_key=True, autoincrement=True)
    result_id = Column(BigInteger, ForeignKey("auction_results.result_id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False)
    buyer_id = Column(BigInteger, ForeignKey("users.user_id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    payment_method = Column(Enum(PaymentMethod), nullable=False, default=PaymentMethod.SIMULATED_UPI)
    status = Column(Enum(PaymentStatus), nullable=False, default=PaymentStatus.PENDING)
    transaction_reference = Column(String(100), nullable=False, unique=True)
    paid_at = Column(DateTime, nullable=True)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), nullable=False)

    result = relationship("AuctionResult", back_populates="payments")
    buyer = relationship("User", back_populates="payments")


class Notification(Base):
    __tablename__ = "notifications"

    notification_id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.user_id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    auction_id = Column(BigInteger, ForeignKey("auctions.auction_id", ondelete="SET NULL", onupdate="CASCADE"), nullable=True)
    title = Column(String(150), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, nullable=False, default=False)
    notification_type = Column(Enum(NotificationType), nullable=False)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), nullable=False)

    user = relationship("User", back_populates="notifications")
    auction = relationship("Auction")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    log_id = Column(BigInteger, primary_key=True, autoincrement=True)
    table_name = Column(String(50), nullable=False)
    operation = Column(Enum(AuditOperation), nullable=False)
    record_id = Column(BigInteger, nullable=False)
    changed_by = Column(String(100), nullable=True)
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    action_timestamp = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
