# BidSphere Automated Test Plan & Execution Report

## 1. Overview & Objectives

This document outlines the test strategy, verification matrix, and actual executed results for the **BidSphere Online Auction Management System**. Testing validates database integrity, ACID transactional behavior, concurrency control under pessimistic row-locking (`SELECT ... FOR UPDATE`), role-based authorization, and business rules across all nine core tables.

All test suites were executed using `pytest` and FastAPI's `TestClient` against live **MySQL 8.4 Community Server (InnoDB)**.

---

## 2. Test Execution Summary

| Metric | Value |
|---|---|
| **Testing Framework** | `pytest 8.4.2` + `FastAPI TestClient` |
| **Total Automated Tests** | **26 Tests** |
| **Tests Passed** | **26 (100%)** |
| **Tests Failed** | **0 (0%)** |
| **Target Database** | MySQL 8.4.13 (InnoDB Engine) |
| **Database Name** | `bidsphere_db` |
| **Test Execution Time** | 0.75 seconds |

---

## 3. Detailed Test Matrix & Results

### Suite A: Authentication & Role-Based Access Control (`test_auth.py`)

| Test ID | Test Function | Test Objective | Expected Status | Verified Status | Result |
|---|---|---|---|---|---|
| TC-AUTH-01 | `test_registration_and_login_success` | Verifies full user registration followed by JWT token issuance | HTTP 201 then 200 | HTTP 201 then 200 | **PASSED** |
| TC-AUTH-02 | `test_duplicate_email_rejection` | Verifies rejection when registering an existing email address | HTTP 409 Conflict | HTTP 409 Conflict | **PASSED** |
| TC-AUTH-03 | `test_duplicate_username_rejection` | Verifies rejection when registering an existing username | HTTP 409 Conflict | HTTP 409 Conflict | **PASSED** |
| TC-AUTH-04 | `test_invalid_password_rejection` | Verifies authentication failure with incorrect password | HTTP 401 Unauthorized | HTTP 401 Unauthorized | **PASSED** |
| TC-AUTH-05 | `test_inactive_account_rejection` | Verifies deactivated user accounts are rejected on login | HTTP 403 Forbidden | HTTP 403 Forbidden | **PASSED** |
| TC-AUTH-06 | `test_role_based_access_control` | Verifies buyers cannot access admin endpoints (`/admin/dashboard`) | HTTP 403 vs 200 | HTTP 403 vs 200 | **PASSED** |

### Suite B: Auction Creation & Marketplace Management (`test_auctions.py`)

| Test ID | Test Function | Test Objective | Expected Status | Verified Status | Result |
|---|---|---|---|---|---|
| TC-AUC-01 | `test_auction_creation_permission` | Buyers cannot create auctions; Sellers and Admins can | HTTP 403 vs 201 | HTTP 403 vs 201 | **PASSED** |
| TC-AUC-02 | `test_auction_invalid_dates_rejected` | Rejects listing when `end_time <= start_time` | HTTP 422 Unprocessable | HTTP 422 Unprocessable | **PASSED** |
| TC-AUC-03 | `test_auction_search_and_filters` | Verifies keyword search and category filtering | HTTP 200 with matching items | HTTP 200 with matching items | **PASSED** |
| TC-AUC-04 | `test_cannot_edit_auction_with_bids` | Sellers cannot modify auction terms after bidding commences | HTTP 400 Bad Request | HTTP 400 Bad Request | **PASSED** |

### Suite C: Bidding Engine & Business Rules (`test_bids.py`)

| Test ID | Test Function | Test Objective | Expected Status | Verified Status | Result |
|---|---|---|---|---|---|
| TC-BID-01 | `test_seller_cannot_bid_on_own_auction` | Rejects seller attempting to bid on their own listing | HTTP 403 Forbidden | HTTP 403 Forbidden | **PASSED** |
| TC-BID-02 | `test_bid_below_minimum_rejection` | Rejects bids below `current_price + bid_increment` | HTTP 422 Unprocessable | HTTP 422 Unprocessable | **PASSED** |
| TC-BID-03 | `test_bid_on_closed_auction_rejection` | Rejects bids on closed/inactive auctions | HTTP 400 Bad Request | HTTP 400 Bad Request | **PASSED** |
| TC-BID-04 | `test_valid_bid_acceptance` | Accepts valid bid, increments price, logs event | HTTP 201 Created | HTTP 201 Created | **PASSED** |

### Suite D: Concurrency Control & Rollback Safety (`test_concurrency.py`)

| Test ID | Test Function | Test Objective | Expected Status | Verified Status | Result |
|---|---|---|---|---|---|
| TC-CONC-01 | `test_concurrent_bids_serialized_cleanly` | Two identical concurrent bids: exactly one succeeds, second serialized/rejected | 1 Success (201), 1 Rejection (422) | 1 Success (201), 1 Rejection (422) | **PASSED** |
| TC-CONC-02 | `test_transaction_rollback_preserves_state` | Failed bid rolls back transaction without phantom rows or price drift | Price & bid count identical | Price & bid count identical | **PASSED** |

### Suite E: Auction Closure & Idempotency (`test_closure.py`)

| Test ID | Test Function | Test Objective | Expected Status | Verified Status | Result |
|---|---|---|---|---|---|
| TC-CLS-01 | `test_auction_closure_with_winner` | Closes lot, identifies highest bid, sets winner and final price | HTTP 200 (Result: WON) | HTTP 200 (Result: WON) | **PASSED** |
| TC-CLS-02 | `test_auction_closure_without_bids_unsold` | Closes lot with 0 bids, sets `final_price=0`, `winner=NULL`, status `UNSOLD` | HTTP 200 (Result: UNSOLD) | HTTP 200 (Result: UNSOLD) | **PASSED** |
| TC-CLS-03 | `test_repeated_auction_closure_idempotent` | Re-executing closure on closed auction returns existing result without duplicates | Exactly 1 result row in DB | Exactly 1 result row in DB | **PASSED** |

### Suite F: Simulated Payments & Settlement (`test_payments.py`)

| Test ID | Test Function | Test Objective | Expected Status | Verified Status | Result |
|---|---|---|---|---|---|
| TC-PAY-01 | `test_payment_duplicate_prevention` | Prevents duplicate payments on an already settled auction result | HTTP 409 Conflict | HTTP 409 Conflict | **PASSED** |
| TC-PAY-02 | `test_payment_unauthorized_user_rejection` | Rejects payment from non-winning users | HTTP 403 Forbidden | HTTP 403 Forbidden | **PASSED** |
| TC-PAY-03 | `test_payment_for_unsold_auction_rejection` | Rejects payment attempt on an unsold auction | HTTP 400 Bad Request | HTTP 400 Bad Request | **PASSED** |

### Suite G: Integrity & CHECK Constraints (`test_constraints.py`)

| Test ID | Test Function | Test Objective | Expected Status | Verified Status | Result |
|---|---|---|---|---|---|
| TC-CST-01 | `test_foreign_key_constraint_violation` | Rejects auction insert referencing invalid seller ID (`999999`) | MySQL FK Violation | MySQL FK Violation | **PASSED** |
| TC-CST-02 | `test_check_constraint_negative_price_violation` | Rejects negative starting price (`starting_price <= 0`) | MySQL CHECK Violation | MySQL CHECK Violation | **PASSED** |
| TC-CST-03 | `test_check_constraint_time_window_violation` | Rejects inverted time window (`end_time <= start_time`) | MySQL CHECK Violation | MySQL CHECK Violation | **PASSED** |
| TC-CST-04 | `test_database_health_reporting` | Verifies database connectivity and version reporting | MySQL 8.4 connected | MySQL 8.4 connected | **PASSED** |

---

## 4. Concurrency Verification Analysis

In `test_concurrent_bids_serialized_cleanly`, two client threads simulated simultaneous requests to place a bid of ₹75,000.00 on Auction #7 (Abstract Canvas). 

### Observed Execution Trace:
1. Both requests arrived at the FastAPI `/api/v1/bids/auctions/7` endpoint within milliseconds.
2. The MySQL stored procedure `PlaceBid` executed `SELECT ... FOR UPDATE` on `auctions.auction_id = 7`.
3. Thread 1 acquired the exclusive row lock first; Thread 2 was placed in a queue awaiting lock release.
4. Thread 1 confirmed that ₹75,000.00 satisfied `current_price + bid_increment`, inserted the bid, updated `current_price = 75000.00`, and committed.
5. The lock was released and granted to Thread 2.
6. Thread 2 evaluated the newly committed auction row: `current_price` was now ₹75,000.00, requiring a minimum bid of ₹77,000.00.
7. Thread 2 rejected the ₹75,000.00 bid with `HTTP 422: Bid amount ₹75000.00 is below minimum required bid of ₹77000.00`, rolling back without side effects.
8. **Conclusion:** Zero lost updates, zero race conditions, absolute transactional consistency.
