import concurrent.futures
from decimal import Decimal
import pytest


def test_concurrent_bids_serialized_cleanly(client, buyer_token, buyer2_token):
    """
    Test two concurrent bids submitted at the exact same moment on the same auction.
    Verifies that MySQL row-level locking (SELECT ... FOR UPDATE) handles concurrency cleanly.
    """
    auction_id = 7  # Abstract Canvas: current_price 72000, increment 2000 -> min 74000
    target_bid = 75000.00

    def submit_bid(token, amount):
        return client.post(
            f"/api/v1/bids/auctions/{auction_id}",
            json={"bid_amount": amount},
            headers={"Authorization": f"Bearer {token}"},
        )

    # Both buyers simultaneously submit the exact same bid amount
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        future1 = executor.submit(submit_bid, buyer_token, target_bid)
        future2 = executor.submit(submit_bid, buyer2_token, target_bid)
        res1 = future1.result()
        res2 = future2.result()

    statuses = [res1.status_code, res2.status_code]

    # Exactly one bid must succeed (201), and the second must be rejected (422) because the price moved
    assert 201 in statuses, "At least one concurrent bid must be accepted"
    assert 422 in statuses or 400 in statuses, "The competing identical bid must be rejected once price moves"

    # Confirm auction state is consistent
    auc_res = client.get(f"/api/v1/auctions/{auction_id}")
    assert auc_res.status_code == 200
    assert float(auc_res.json()["current_price"]) == target_bid


def test_transaction_rollback_preserves_state(client, buyer_token):
    """Confirm failed bids roll back completely without leaving partial records or altering price."""
    # Auction 8: Leica M3, current_price is 135000
    initial_res = client.get("/api/v1/auctions/8")
    initial_price = initial_res.json()["current_price"]

    # Count bids
    initial_bids = client.get("/api/v1/bids/auctions/8").json()
    initial_bid_count = len(initial_bids)

    # Submit an invalid low bid (130000 < 135000)
    failed_res = client.post(
        "/api/v1/bids/auctions/8",
        json={"bid_amount": 130000.00},
        headers={"Authorization": f"Bearer {buyer_token}"},
    )
    assert failed_res.status_code == 422

    # Verify price did NOT change
    after_res = client.get("/api/v1/auctions/8")
    assert after_res.json()["current_price"] == initial_price

    # Verify no phantom bid record was created
    after_bids = client.get("/api/v1/bids/auctions/8").json()
    assert len(after_bids) == initial_bid_count
