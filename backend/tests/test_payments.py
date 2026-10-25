import pytest


def test_payment_duplicate_prevention(client, buyer_token):
    """Test that a won auction result cannot be paid for twice."""
    # Result #1 (iPhone 15 Pro Max won by user 6 'vikram_b') was already paid in seed data
    res = client.post(
        "/api/v1/payments",
        json={"result_id": 1, "payment_method": "SIMULATED_UPI"},
        headers={"Authorization": f"Bearer {buyer_token}"},
    )
    assert res.status_code == 409
    assert "already been successfully paid" in res.json()["detail"].lower()


def test_payment_unauthorized_user_rejection(client, buyer2_token):
    """Test user who did not win the auction cannot submit payment for it."""
    # Result #1 was won by user 6 ('vikram_b'). Buyer2 ('sneha_rao') tries to pay -> 403
    res = client.post(
        "/api/v1/payments",
        json={"result_id": 1, "payment_method": "SIMULATED_UPI"},
        headers={"Authorization": f"Bearer {buyer2_token}"},
    )
    assert res.status_code == 403
    assert "not authorized" in res.json()["detail"].lower()


def test_payment_for_unsold_auction_rejection(client, buyer_token):
    """Test payment cannot be processed for an unsold auction."""
    # Result #4 is UNSOLD
    res = client.post(
        "/api/v1/payments",
        json={"result_id": 4, "payment_method": "SIMULATED_UPI"},
        headers={"Authorization": f"Bearer {buyer_token}"},
    )
    assert res.status_code in [400, 403]
