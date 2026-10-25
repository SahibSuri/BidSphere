-- =============================================================================
-- BidSphere Online Auction Management System
-- Database Indexes Definition (Performance & Optimization)
-- =============================================================================

USE bidsphere_db;

-- Stored procedure to safely add index if not present
DROP PROCEDURE IF EXISTS AddIndexIfNotExists;

DELIMITER $$
CREATE PROCEDURE AddIndexIfNotExists(
    IN p_table_name VARCHAR(64),
    IN p_index_name VARCHAR(64),
    IN p_index_def VARCHAR(255)
)
BEGIN
    DECLARE v_index_exists INT DEFAULT 0;

    SELECT COUNT(*) INTO v_index_exists
    FROM information_schema.statistics
    WHERE table_schema = DATABASE()
      AND table_name = p_table_name
      AND index_name = p_index_name;

    IF v_index_exists = 0 THEN
        SET @sql = CONCAT('CREATE INDEX ', p_index_name, ' ON ', p_table_name, ' (', p_index_def, ')');
        PREPARE stmt FROM @sql;
        EXECUTE stmt;
        DEALLOCATE PREPARE stmt;
    END IF;
END$$
DELIMITER ;

-- Indexes on Auctions Table
CALL AddIndexIfNotExists('auctions', 'idx_auctions_status_end_time', 'status, end_time');
CALL AddIndexIfNotExists('auctions', 'idx_auctions_category_status', 'category_id, status');
CALL AddIndexIfNotExists('auctions', 'idx_auctions_seller', 'seller_id, status');
CALL AddIndexIfNotExists('auctions', 'idx_auctions_current_price', 'current_price');

-- Indexes on Bids Table
CALL AddIndexIfNotExists('bids', 'idx_bids_auction_amount', 'auction_id, bid_amount DESC');
CALL AddIndexIfNotExists('bids', 'idx_bids_bidder_time', 'bidder_id, bid_time DESC');
CALL AddIndexIfNotExists('bids', 'idx_bids_auction_status', 'auction_id, status');

-- Indexes on Watchlist Table
CALL AddIndexIfNotExists('watchlist', 'idx_watchlist_user', 'user_id');
CALL AddIndexIfNotExists('watchlist', 'idx_watchlist_auction', 'auction_id');

-- Indexes on Auction Results Table
CALL AddIndexIfNotExists('auction_results', 'idx_results_winner', 'winner_id');
CALL AddIndexIfNotExists('auction_results', 'idx_results_status', 'result_status');

-- Indexes on Payments Table
CALL AddIndexIfNotExists('payments', 'idx_payments_buyer_status', 'buyer_id, status');
CALL AddIndexIfNotExists('payments', 'idx_payments_result', 'result_id');

-- Indexes on Notifications Table
CALL AddIndexIfNotExists('notifications', 'idx_notifications_user_unread', 'user_id, is_read, created_at DESC');

-- Indexes on Audit Logs Table
CALL AddIndexIfNotExists('audit_logs', 'idx_audit_table_record', 'table_name, record_id');
CALL AddIndexIfNotExists('audit_logs', 'idx_audit_timestamp', 'action_timestamp DESC');

DROP PROCEDURE IF EXISTS AddIndexIfNotExists;
