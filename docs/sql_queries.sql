-- =============================================================================
-- BidSphere Online Auction Management System
-- Academic DBMS Demonstration SQL Queries (16 Queries)
-- =============================================================================

USE bidsphere_db;

-- -----------------------------------------------------------------------------
-- Query 1: Basic SELECT, WHERE, ORDER BY and DISTINCT
-- Retrieve all active users who are registered as Sellers, ordered by name
-- -----------------------------------------------------------------------------
SELECT DISTINCT 
    user_id, 
    username, 
    email, 
    full_name, 
    role, 
    phone, 
    created_at
FROM users
WHERE role = 'SELLER' AND is_active = TRUE
ORDER BY full_name ASC;

-- -----------------------------------------------------------------------------
-- Query 2: INNER JOIN
-- Retrieve all active auctions along with their category name and seller username
-- -----------------------------------------------------------------------------
SELECT 
    a.auction_id,
    a.title,
    c.name AS category_name,
    u.username AS seller_username,
    a.starting_price,
    a.current_price,
    a.end_time
FROM auctions a
INNER JOIN categories c ON a.category_id = c.category_id
INNER JOIN users u ON a.seller_id = u.user_id
WHERE a.status = 'ACTIVE'
ORDER BY a.end_time ASC;

-- -----------------------------------------------------------------------------
-- Query 3: LEFT OUTER JOIN
-- Retrieve all auctions and their total placed bids, including auctions with 0 bids
-- -----------------------------------------------------------------------------
SELECT 
    a.auction_id,
    a.title,
    a.status,
    COUNT(b.bid_id) AS total_bids_count
FROM auctions a
LEFT JOIN bids b ON a.auction_id = b.auction_id
GROUP BY a.auction_id, a.title, a.status
ORDER BY total_bids_count DESC;

-- -----------------------------------------------------------------------------
-- Query 4: GROUP BY and HAVING
-- Find auctions with high bidding competition (more than 3 accepted bids)
-- -----------------------------------------------------------------------------
SELECT 
    a.auction_id,
    a.title,
    a.current_price,
    COUNT(b.bid_id) AS accepted_bids_count
FROM auctions a
JOIN bids b ON a.auction_id = b.auction_id
WHERE b.status IN ('ACCEPTED', 'OUTBID')
GROUP BY a.auction_id, a.title, a.current_price
HAVING COUNT(b.bid_id) >= 3
ORDER BY accepted_bids_count DESC;

-- -----------------------------------------------------------------------------
-- Query 5: Aggregate Functions (COUNT, SUM, AVG, MIN, MAX)
-- Bidding statistics summary across all placed bids
-- -----------------------------------------------------------------------------
SELECT 
    COUNT(*) AS total_bids_placed,
    MIN(bid_amount) AS lowest_bid_inr,
    MAX(bid_amount) AS highest_bid_inr,
    ROUND(AVG(bid_amount), 2) AS average_bid_inr,
    SUM(bid_amount) AS total_bidding_activity_volume
FROM bids;

-- -----------------------------------------------------------------------------
-- Query 6: Correlated Subquery
-- Retrieve the highest accepted bid details for each active auction
-- -----------------------------------------------------------------------------
SELECT 
    b.auction_id,
    b.bid_id,
    b.bidder_id,
    u.username AS leading_bidder,
    b.bid_amount,
    b.bid_time
FROM bids b
JOIN users u ON b.bidder_id = u.user_id
WHERE b.bid_amount = (
    SELECT MAX(b2.bid_amount)
    FROM bids b2
    WHERE b2.auction_id = b.auction_id
      AND b2.status = 'ACCEPTED'
);

-- -----------------------------------------------------------------------------
-- Query 7: Auctions with No Bids (Subquery with NOT IN / NOT EXISTS)
-- Identify auctions that currently have zero bids
-- -----------------------------------------------------------------------------
SELECT 
    a.auction_id,
    a.title,
    c.name AS category_name,
    a.starting_price,
    a.status,
    a.start_time,
    a.end_time
FROM auctions a
JOIN categories c ON a.category_id = c.category_id
WHERE NOT EXISTS (
    SELECT 1 FROM bids b WHERE b.auction_id = a.auction_id
);

-- -----------------------------------------------------------------------------
-- Query 8: Seller Performance & Revenue Realization
-- Aggregates listings created, closed lots, and total revenue realized per seller
-- -----------------------------------------------------------------------------
SELECT 
    u.user_id AS seller_id,
    u.username AS seller_username,
    u.full_name AS seller_name,
    COUNT(DISTINCT a.auction_id) AS total_listings,
    SUM(CASE WHEN a.status = 'CLOSED' THEN 1 ELSE 0 END) AS successful_sales,
    COALESCE(SUM(r.final_price), 0.00) AS total_revenue_realized
FROM users u
JOIN auctions a ON u.user_id = a.seller_id
LEFT JOIN auction_results r ON a.auction_id = r.auction_id AND r.result_status = 'WON'
GROUP BY u.user_id, u.username, u.full_name
ORDER BY total_revenue_realized DESC;

-- -----------------------------------------------------------------------------
-- Query 9: Buyer Bidding Activity & Engagement
-- Detailed breakdown of buyer participation, total bids submitted, and winning record
-- -----------------------------------------------------------------------------
SELECT 
    u.user_id AS buyer_id,
    u.username AS buyer_username,
    u.email,
    COUNT(b.bid_id) AS total_bids_placed,
    COUNT(DISTINCT b.auction_id) AS auctions_participated_in,
    COUNT(DISTINCT r.result_id) AS auctions_won,
    COALESCE(SUM(r.final_price), 0.00) AS total_expenditure
FROM users u
LEFT JOIN bids b ON u.user_id = b.bidder_id
LEFT JOIN auction_results r ON u.user_id = r.winner_id AND r.result_status = 'WON'
WHERE u.role IN ('BUYER', 'ADMIN')
GROUP BY u.user_id, u.username, u.email
ORDER BY total_bids_placed DESC;

-- -----------------------------------------------------------------------------
-- Query 10: Winning Auction Summaries & Value Multipliers
-- Compares starting price vs final price to determine value appreciation
-- -----------------------------------------------------------------------------
SELECT 
    r.result_id,
    a.title,
    u_seller.username AS seller,
    u_winner.username AS winner,
    a.starting_price,
    r.final_price,
    (r.final_price - a.starting_price) AS absolute_value_gain,
    ROUND(((r.final_price - a.starting_price) / a.starting_price) * 100, 2) AS appreciation_percentage,
    r.closed_at
FROM auction_results r
JOIN auctions a ON r.auction_id = a.auction_id
JOIN users u_seller ON a.seller_id = u_seller.user_id
JOIN users u_winner ON r.winner_id = u_winner.user_id
WHERE r.result_status = 'WON'
ORDER BY absolute_value_gain DESC;

-- -----------------------------------------------------------------------------
-- Query 11: Payment Status Summary
-- Summarizes payment settlement distribution across won lots
-- -----------------------------------------------------------------------------
SELECT 
    p.status AS payment_status,
    p.payment_method,
    COUNT(p.payment_id) AS transaction_count,
    SUM(p.amount) AS total_amount_inr,
    ROUND(AVG(p.amount), 2) AS average_transaction_inr
FROM payments p
GROUP BY p.status, p.payment_method
ORDER BY total_amount_inr DESC;

-- -----------------------------------------------------------------------------
-- Query 12: Watchlist Demand Analytics
-- Ranks auctions based on user demand bookmark count
-- -----------------------------------------------------------------------------
SELECT 
    a.auction_id,
    a.title,
    c.name AS category_name,
    a.current_price,
    COUNT(w.watchlist_id) AS bookmark_count
FROM auctions a
JOIN categories c ON a.category_id = c.category_id
LEFT JOIN watchlist w ON a.auction_id = w.auction_id
GROUP BY a.auction_id, a.title, c.name, a.current_price
HAVING COUNT(w.watchlist_id) > 0
ORDER BY bookmark_count DESC, a.current_price DESC;

-- -----------------------------------------------------------------------------
-- Query 13: Category Revenue & Volume Analysis
-- Calculates gross inventory volume and sales velocity per category
-- -----------------------------------------------------------------------------
SELECT 
    c.category_id,
    c.name AS category_name,
    COUNT(a.auction_id) AS total_auctions_listed,
    SUM(CASE WHEN a.status = 'ACTIVE' THEN 1 ELSE 0 END) AS active_auctions,
    SUM(CASE WHEN a.status = 'CLOSED' THEN 1 ELSE 0 END) AS sold_auctions,
    COALESCE(SUM(r.final_price), 0.00) AS total_realized_revenue
FROM categories c
LEFT JOIN auctions a ON c.category_id = a.category_id
LEFT JOIN auction_results r ON a.auction_id = r.auction_id AND r.result_status = 'WON'
GROUP BY c.category_id, c.name
ORDER BY total_realized_revenue DESC;

-- -----------------------------------------------------------------------------
-- Query 14: Window Function - Bid Rank within Each Auction (MySQL 8.0+)
-- Uses DENSE_RANK() to rank bids for each auction by amount
-- -----------------------------------------------------------------------------
SELECT 
    b.auction_id,
    a.title,
    u.username AS bidder_name,
    b.bid_amount,
    b.bid_time,
    DENSE_RANK() OVER (
        PARTITION BY b.auction_id 
        ORDER BY b.bid_amount DESC
    ) AS bid_rank
FROM bids b
JOIN auctions a ON b.auction_id = a.auction_id
JOIN users u ON b.bidder_id = u.user_id
WHERE b.status IN ('ACCEPTED', 'OUTBID')
ORDER BY b.auction_id, bid_rank ASC;

-- -----------------------------------------------------------------------------
-- Query 15: Common Table Expression (CTE) - Top 3 Leading Bidders
-- Identifies the top 3 highest spending bidders using a CTE
-- -----------------------------------------------------------------------------
WITH BidderAggregates AS (
    SELECT 
        u.user_id,
        u.username,
        u.full_name,
        COUNT(r.result_id) AS won_count,
        COALESCE(SUM(r.final_price), 0.00) AS total_won_spend
    FROM users u
    JOIN auction_results r ON u.user_id = r.winner_id
    WHERE r.result_status = 'WON'
    GROUP BY u.user_id, u.username, u.full_name
)
SELECT 
    username,
    full_name,
    won_count,
    total_won_spend
FROM BidderAggregates
ORDER BY total_won_spend DESC
LIMIT 3;

-- -----------------------------------------------------------------------------
-- Query 16: System Audit Log Analysis
-- Summarizes audit events by table and operation type
-- -----------------------------------------------------------------------------
SELECT 
    table_name,
    operation,
    COUNT(*) AS event_count,
    MIN(action_timestamp) AS first_event,
    MAX(action_timestamp) AS latest_event
FROM audit_logs
GROUP BY table_name, operation
ORDER BY event_count DESC;
