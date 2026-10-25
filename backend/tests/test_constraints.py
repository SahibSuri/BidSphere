from datetime import datetime, timedelta
import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, OperationalError
from backend.database import check_database_health


def test_foreign_key_constraint_violation(db_session):
    """Test MySQL InnoDB foreign key constraint rejection on invalid foreign key ID."""
    with pytest.raises(IntegrityError) as exc_info:
        db_session.execute(
            text(
                "INSERT INTO auctions (seller_id, category_id, title, description, starting_price, "
                "current_price, bid_increment, status, start_time, end_time) "
                "VALUES (999999, 1, 'Ghost Seller Auction', 'Invalid seller foreign key test', 1000.00, "
                "1000.00, 50.00, 'SCHEDULED', NOW(), DATE_ADD(NOW(), INTERVAL 1 DAY));"
            )
        )
        db_session.commit()
    db_session.rollback()
    assert "foreign key constraint fails" in str(exc_info.value).lower()


def test_check_constraint_negative_price_violation(db_session):
    """Test MySQL 8.0+ CHECK constraint rejection on starting_price <= 0."""
    with pytest.raises((IntegrityError, OperationalError)) as exc_info:
        db_session.execute(
            text(
                "INSERT INTO auctions (seller_id, category_id, title, description, starting_price, "
                "current_price, bid_increment, status, start_time, end_time) "
                "VALUES (2, 1, 'Negative Price Auction', 'Invalid starting price test', -500.00, "
                "-500.00, 50.00, 'SCHEDULED', NOW(), DATE_ADD(NOW(), INTERVAL 1 DAY));"
            )
        )
        db_session.commit()
    db_session.rollback()
    assert "check" in str(exc_info.value).lower() or "constraint" in str(exc_info.value).lower()


def test_check_constraint_time_window_violation(db_session):
    """Test MySQL 8.0+ CHECK constraint rejection when end_time <= start_time."""
    with pytest.raises((IntegrityError, OperationalError)) as exc_info:
        db_session.execute(
            text(
                "INSERT INTO auctions (seller_id, category_id, title, description, starting_price, "
                "current_price, bid_increment, status, start_time, end_time) "
                "VALUES (2, 1, 'Inverted Time Auction', 'Invalid time window test', 1000.00, "
                "1000.00, 50.00, 'SCHEDULED', NOW(), DATE_SUB(NOW(), INTERVAL 1 DAY));"
            )
        )
        db_session.commit()
    db_session.rollback()
    assert "check" in str(exc_info.value).lower() or "constraint" in str(exc_info.value).lower()


def test_database_health_reporting():
    """Test database health check returns operational metrics."""
    health = check_database_health()
    assert health["connected"] is True
    assert health["status"] == "healthy"
    assert "8.4" in health["version"] or "8." in health["version"]
    assert health["database"] == "bidsphere_db"
