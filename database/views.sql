-- =============================================================================
-- BidSphere Online Auction Management System
-- Analytical Views Definition
-- =============================================================================

USE bidsphere_db;

-- -----------------------------------------------------------------------------
-- 1. View: Active Auctions with dynamic metrics
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_active_auctions AS
SELECT 
    a.auction_id,
    a.title,
    a.description,
    c.category_id,
    c.name AS category_name,
    u.user_id AS seller_id,
    u.username AS seller_username,
    u.full_name AS seller_full_name,
    a.starting_price,
    a.current_price,
    a.bid_increment,
    (a.current_price + a.bid_increment) AS min_next_bid,
    a.status,
    a.start_time,
    a.end_time,
    TIMESTAMPDIFF(SECOND, NOW(), a.end_time) AS seconds_remaining,
    a.image_url,
    COUNT(b.bid_id) AS total_bids,
    COALESCE(MAX(b.bid_amount), a.starting_price) AS current_highest_bid,
    a.created_at
FROM auctions a
JOIN categories c ON a.category_id = c.category_id
JOIN users u ON a.seller_id = u.user_id
LEFT JOIN bids b ON a.auction_id = b.auction_id AND b.status = 'ACCEPTED'
WHERE a.status = 'ACTIVE' AND a.end_time > NOW()
GROUP BY 
    a.auction_id, a.title, a.description, c.category_id, c.name, 
    u.user_id, u.username, u.full_name, a.starting_price, a.current_price, 
    a.bid_increment, a.status, a.start_time, a.end_time, a.image_url, a.created_at;

-- -----------------------------------------------------------------------------
-- 2. View: Comprehensive Auction Bidding Summary
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_auction_bid_summary AS
SELECT 
    a.auction_id,
    a.title,
    c.name AS category_name,
    u.username AS seller_username,
    a.starting_price,
    a.current_price,
    a.status AS auction_status,
    COUNT(b.bid_id) AS total_bids,
    COUNT(DISTINCT b.bidder_id) AS unique_bidders,
    MIN(b.bid_amount) AS lowest_bid,
    MAX(b.bid_amount) AS highest_bid,
    ROUND(AVG(b.bid_amount), 2) AS average_bid,
    a.start_time,
    a.end_time
FROM auctions a
JOIN categories c ON a.category_id = c.category_id
JOIN users u ON a.seller_id = u.user_id
LEFT JOIN bids b ON a.auction_id = b.auction_id AND b.status = 'ACCEPTED'
GROUP BY 
    a.auction_id, a.title, c.name, u.username, 
    a.starting_price, a.current_price, a.status, a.start_time, a.end_time;

-- -----------------------------------------------------------------------------
-- 3. View: Final Auction Results & Settlement Summary
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_auction_results AS
SELECT 
    r.result_id,
    a.auction_id,
    a.title AS auction_title,
    c.name AS category_name,
    seller.username AS seller_username,
    seller.email AS seller_email,
    winner.user_id AS winner_id,
    winner.username AS winner_username,
    winner.full_name AS winner_full_name,
    winner.email AS winner_email,
    r.final_price,
    r.result_status,
    r.closed_at,
    p.payment_id,
    COALESCE(p.status, 'NOT_INITIATED') AS payment_status,
    p.payment_method,
    p.transaction_reference,
    p.paid_at
FROM auction_results r
JOIN auctions a ON r.auction_id = a.auction_id
JOIN categories c ON a.category_id = c.category_id
JOIN users seller ON a.seller_id = seller.user_id
LEFT JOIN users winner ON r.winner_id = winner.user_id
LEFT JOIN payments p ON r.result_id = p.result_id;
