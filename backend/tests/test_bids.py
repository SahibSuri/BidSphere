import pytest


def test_seller_cannot_bid_on_own_auction(client, seller_token):
    """Test that sellers are strictly prohibited from bidding on their own listing."""
    # Auction 1 is owned by seller_id 2 ('aravind_tech')
    res = client.post(
        "/api/v1/bids/auctions/1",
        json={"bid_amount": 300000.00},
        headers={"Authorization": f"Bearer {seller_token}"},
    )
    assert res.status_code == 403
    assert "strictly prohibited" in res.json()["detail"].lower()


def test_bid_below_minimum_rejection(client, buyer_token):
    """Test that a bid below the required minimum is rejected."""
    # Auction 2: current_price 42000, increment 1000 -> min bid is 43000
    res = client.post(
        "/api/v1/bids/auctions/2",
        json={"bid_amount": 42500.00},
        headers={"Authorization": f"Bearer {buyer_token}"},
    )
    assert res.status_code == 422
    assert "below minimum required bid" in res.json()["detail"].lower()


def test_bid_on_closed_auction_rejection(client, buyer_token):
    """Test bidding on an already closed auction is rejected."""
    # Auction 11 is CLOSED
    res = client.post(
        "/api/v1/bids/auctions/11",
        json={"bid_amount": 150000.00},
        headers={"Authorization": f"Bearer {buyer_token}"},
    )
    assert res.status_code == 400
    assert "not open for bidding" in res.json()["detail"].lower()


def test_valid_bid_acceptance(client, buyer_token):
    """Test placing a valid bid updates current_price and creates bid record."""
    # Auction 4: Stamp Collection, current_price is 31000, increment 1000 -> min 32000
    valid_amount = 35000.00
    res = client.post(
        "/api/v1/bids/auctions/4",
        json={"bid_amount": valid_amount},
        headers={"Authorization": f"Bearer {buyer_token}"},
    )
    assert res.status_code == 201
    data = res.json()
    assert data["status_code"] == 200
    assert "accepted successfully" in data["status_message"].lower()

    # Verify auction current_price updated
    auc_res = client.get("/api/v1/auctions/4")
    assert auc_res.status_code == 200
    assert float(auc_res.json()["current_price"]) == valid_amount
