from datetime import datetime, timedelta
import pytest


def test_auction_creation_permission(client, buyer_token, seller_token):
    """Test that buyers are prohibited from creating auctions, but sellers can."""
    start = datetime.now() + timedelta(hours=1)
    end = datetime.now() + timedelta(days=3)

    payload = {
        "category_id": 1,
        "title": "Automated Test iPad Pro",
        "description": "Brand new sealed iPad Pro M4 256GB Wi-Fi model.",
        "starting_price": 75000.00,
        "bid_increment": 1000.00,
        "start_time": start.isoformat(),
        "end_time": end.isoformat(),
    }

    # Buyer attempt -> 403 Forbidden
    res_buyer = client.post(
        "/api/v1/auctions",
        json=payload,
        headers={"Authorization": f"Bearer {buyer_token}"},
    )
    assert res_buyer.status_code == 403

    # Seller attempt -> 201 Created
    res_seller = client.post(
        "/api/v1/auctions",
        json=payload,
        headers={"Authorization": f"Bearer {seller_token}"},
    )
    assert res_seller.status_code == 201
    data = res_seller.json()
    assert data["title"] == "Automated Test iPad Pro"
    assert float(data["starting_price"]) == 75000.00


def test_auction_invalid_dates_rejected(client, seller_token):
    """Test validation fails if end time is before start time."""
    start = datetime.now() + timedelta(days=2)
    end = datetime.now() + timedelta(days=1)  # Invalid

    payload = {
        "category_id": 1,
        "title": "Invalid Date Listing",
        "description": "Test description text here.",
        "starting_price": 10000.00,
        "bid_increment": 500.00,
        "start_time": start.isoformat(),
        "end_time": end.isoformat(),
    }
    res = client.post(
        "/api/v1/auctions",
        json=payload,
        headers={"Authorization": f"Bearer {seller_token}"},
    )
    assert res.status_code == 422


def test_auction_search_and_filters(client):
    """Test searching by keyword and filtering by category."""
    # Search by keyword
    res = client.get("/api/v1/auctions?search=MacBook")
    assert res.status_code == 200
    items = res.json()
    assert len(items) >= 1
    assert "macbook" in items[0]["title"].lower()

    # Filter by category 1 (Consumer Electronics)
    res_cat = client.get("/api/v1/auctions?category_id=1")
    assert res_cat.status_code == 200
    for a in res_cat.json():
        assert a["category_id"] == 1


def test_cannot_edit_auction_with_bids(client, seller_token):
    """Test that editing an auction once bidding has begun is rejected."""
    # Auction 1 already has multiple bids in seed data
    res = client.put(
        "/api/v1/auctions/1",
        json={"title": "Hacked Title Change"},
        headers={"Authorization": f"Bearer {seller_token}"},
    )
    assert res.status_code == 400
    assert "bidding has commenced" in res.json()["detail"].lower()
