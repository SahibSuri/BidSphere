from datetime import datetime, timedelta
import pytest


def test_auction_closure_with_winner(client, admin_token):
    """Test closing an auction with valid bids sets correct winner, final price and status."""
    # Auction 3 (Tanjore Painting) has highest bid from user 8 (amit_kumar) at 55000.00
    res = client.post(
        "/api/v1/auctions/3/close",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status_code"] == 200
    assert "successfully closed" in data["status_message"].lower()

    # Verify auction state is CLOSED
    auc_res = client.get("/api/v1/auctions/3")
    assert auc_res.status_code == 200
    assert auc_res.json()["status"] == "CLOSED"

    # Verify result record
    results = client.get("/api/v1/dashboard/results").json()
    match = [r for r in results if r["auction_id"] == 3]
    assert len(match) == 1
    assert match[0]["result_status"] == "WON"
    assert float(match[0]["final_price"]) == 55000.00
    assert match[0]["winner_username"] == "amit_kumar"


def test_auction_closure_without_bids_unsold(client, admin_token, seller_token):
    """Test closing an auction with zero bids records UNSOLD result."""
    # Create a fresh auction with zero bids
    start = datetime.now() - timedelta(days=2)
    end = datetime.now() - timedelta(hours=1)
    create_res = client.post(
        "/api/v1/auctions",
        json={
            "category_id": 1,
            "title": "Unsold Vintage Radio Test",
            "description": "Old radio with zero bids submitted.",
            "starting_price": 5000.00,
            "bid_increment": 200.00,
            "start_time": start.isoformat(),
            "end_time": end.isoformat(),
        },
        headers={"Authorization": f"Bearer {seller_token}"},
    )
    new_auc_id = create_res.json()["auction_id"]

    # Close the zero-bid auction
    close_res = client.post(
        f"/api/v1/auctions/{new_auc_id}/close",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert close_res.status_code == 200
    assert "unsold" in close_res.json()["status_message"].lower()

    # Verify result record
    results = client.get("/api/v1/dashboard/results").json()
    match = [r for r in results if r["auction_id"] == new_auc_id]
    assert len(match) == 1
    assert match[0]["result_status"] == "UNSOLD"
    assert match[0]["winner_id"] is None
    assert float(match[0]["final_price"]) == 0.00


def test_repeated_auction_closure_idempotent(client, admin_token):
    """Test repeating the closure operation on an already closed auction returns existing result without duplicates."""
    # Auction 11 is already closed with result_id 1
    res1 = client.post(
        "/api/v1/auctions/11/close",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res1.status_code == 200
    assert "already closed" in res1.json()["status_message"].lower()

    res2 = client.post(
        "/api/v1/auctions/11/close",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res2.status_code == 200
    assert res2.json()["result_id"] == res1.json()["result_id"]

    # Verify exactly one result exists in database
    results = client.get("/api/v1/dashboard/results").json()
    matches = [r for r in results if r["auction_id"] == 11]
    assert len(matches) == 1
