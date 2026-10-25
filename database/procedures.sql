-- =============================================================================
-- BidSphere Online Auction Management System
-- Stored Procedures Definition (Transactional & Concurrency Control)
-- =============================================================================

USE bidsphere_db;

DROP PROCEDURE IF EXISTS PlaceBid;
DROP PROCEDURE IF EXISTS CloseAuction;

DELIMITER $$

-- -----------------------------------------------------------------------------
-- Stored Procedure: PlaceBid
-- Atomically validates and places a bid using row-level locking (FOR UPDATE)
-- -----------------------------------------------------------------------------
CREATE PROCEDURE PlaceBid(
    IN p_auction_id BIGINT,
    IN p_bidder_id BIGINT,
    IN p_bid_amount DECIMAL(12, 2),
    OUT p_status_code INT,
    OUT p_status_message VARCHAR(255),
    OUT p_bid_id BIGINT
)
proc_label: BEGIN
    -- Local variables
    DECLARE v_seller_id BIGINT;
    DECLARE v_current_price DECIMAL(12, 2);
    DECLARE v_starting_price DECIMAL(12, 2);
    DECLARE v_bid_increment DECIMAL(10, 2);
    DECLARE v_auction_status VARCHAR(20);
    DECLARE v_start_time DATETIME;
    DECLARE v_end_time DATETIME;
    DECLARE v_bidder_active INT DEFAULT 0;
    DECLARE v_min_valid_bid DECIMAL(12, 2);
    DECLARE v_prev_highest_bidder BIGINT DEFAULT NULL;
    DECLARE v_prev_bid_id BIGINT DEFAULT NULL;

    -- Error handler for unexpected SQL exceptions
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_status_code = 500;
        SET p_status_message = 'Internal database error during bid placement. Transaction rolled back.';
        SET p_bid_id = NULL;
    END;

    -- Start Transaction
    START TRANSACTION;

    -- 1. Validate Bidder Existence and Active Status
    SELECT COUNT(*), is_active INTO v_bidder_active, v_bidder_active
    FROM users 
    WHERE user_id = p_bidder_id
    GROUP BY is_active;

    IF v_bidder_active IS NULL OR v_bidder_active = 0 THEN
        ROLLBACK;
        SET p_status_code = 404;
        SET p_status_message = 'Bidder not found or account is deactivated.';
        SET p_bid_id = NULL;
        LEAVE proc_label;
    END IF;

    -- 2. Acquire Row Lock on Auction record (Pessimistic Concurrency Control)
    SELECT seller_id, current_price, starting_price, bid_increment, 
           status, start_time, end_time
    INTO v_seller_id, v_current_price, v_starting_price, v_bid_increment,
         v_auction_status, v_start_time, v_end_time
    FROM auctions
    WHERE auction_id = p_auction_id
    FOR UPDATE;

    -- Verify auction exists
    IF v_seller_id IS NULL THEN
        ROLLBACK;
        SET p_status_code = 404;
        SET p_status_message = 'Auction listing does not exist.';
        SET p_bid_id = NULL;
        LEAVE proc_label;
    END IF;

    -- 3. Verify Auction is ACTIVE
    IF v_auction_status != 'ACTIVE' THEN
        ROLLBACK;
        SET p_status_code = 400;
        SET p_status_message = CONCAT('Auction is not open for bidding. Current status: ', v_auction_status);
        SET p_bid_id = NULL;
        LEAVE proc_label;
    END IF;

    -- 4. Verify Timing (Start and End Window)
    IF NOW() < v_start_time THEN
        ROLLBACK;
        SET p_status_code = 400;
        SET p_status_message = 'Auction has not started yet.';
        SET p_bid_id = NULL;
        LEAVE proc_label;
    END IF;

    IF NOW() > v_end_time THEN
        ROLLBACK;
        SET p_status_code = 400;
        SET p_status_message = 'Auction has ended. No further bids accepted.';
        SET p_bid_id = NULL;
        LEAVE proc_label;
    END IF;

    -- 5. Business Rule: Seller cannot bid on own auction
    IF v_seller_id = p_bidder_id THEN
        ROLLBACK;
        SET p_status_code = 403;
        SET p_status_message = 'Sellers are strictly prohibited from bidding on their own listings.';
        SET p_bid_id = NULL;
        LEAVE proc_label;
    END IF;

    -- 6. Check existing highest bid to establish minimum valid bid
    SELECT bidder_id, bid_id INTO v_prev_highest_bidder, v_prev_bid_id
    FROM bids
    WHERE auction_id = p_auction_id AND status = 'ACCEPTED'
    ORDER BY bid_amount DESC, bid_time ASC
    LIMIT 1;

    IF v_prev_highest_bidder IS NULL THEN
        -- First bid must meet starting_price
        SET v_min_valid_bid = v_starting_price;
    ELSE
        -- Subsequent bid must exceed current highest bid by at least bid_increment
        SET v_min_valid_bid = v_current_price + v_bid_increment;
        
        -- Prevent outbidding oneself needlessly if desired, or allow higher bid
    END IF;

    IF p_bid_amount < v_min_valid_bid THEN
        ROLLBACK;
        SET p_status_code = 422;
        SET p_status_message = CONCAT('Bid amount ₹', p_bid_amount, ' is below minimum required bid of ₹', v_min_valid_bid);
        SET p_bid_id = NULL;
        LEAVE proc_label;
    END IF;

    -- 7. Mark previous accepted highest bid as OUTBID
    IF v_prev_bid_id IS NOT NULL THEN
        UPDATE bids 
        SET status = 'OUTBID' 
        WHERE bid_id = v_prev_bid_id;

        -- Create OUTBID notification for the previous highest bidder
        INSERT INTO notifications (user_id, auction_id, title, message, notification_type)
        VALUES (
            v_prev_highest_bidder,
            p_auction_id,
            'You have been outbid!',
            CONCAT('A higher bid of ₹', p_bid_amount, ' was placed on auction #', p_auction_id),
            'OUTBID'
        );
    END IF;

    -- 8. Insert New Accepted Bid
    INSERT INTO bids (auction_id, bidder_id, bid_amount, bid_time, status)
    VALUES (p_auction_id, p_bidder_id, p_bid_amount, NOW(), 'ACCEPTED');

    SET p_bid_id = LAST_INSERT_ID();

    -- 9. Update Auction Current Price
    UPDATE auctions
    SET current_price = p_bid_amount,
        updated_at = NOW()
    WHERE auction_id = p_auction_id;

    -- 10. Create Bid Confirmation Notification for Bidder
    INSERT INTO notifications (user_id, auction_id, title, message, notification_type)
    VALUES (
        p_bidder_id,
        p_auction_id,
        'Bid Placed Successfully',
        CONCAT('Your bid of ₹', p_bid_amount, ' on auction #', p_auction_id, ' was accepted.'),
        'BID_PLACED'
    );

    -- 11. Write Audit Log
    INSERT INTO audit_logs (table_name, operation, record_id, changed_by, old_values, new_values)
    VALUES (
        'bids',
        'INSERT',
        p_bid_id,
        CONCAT('user:', p_bidder_id),
        JSON_OBJECT('previous_price', v_current_price),
        JSON_OBJECT('new_bid_amount', p_bid_amount, 'auction_id', p_auction_id)
    );

    -- 12. Commit Transaction
    COMMIT;
    SET p_status_code = 200;
    SET p_status_message = 'Bid placed and accepted successfully.';
END proc_label$$


-- -----------------------------------------------------------------------------
-- Stored Procedure: CloseAuction
-- Determines winner, settles auction state, idempotent & transactional
-- -----------------------------------------------------------------------------
CREATE PROCEDURE CloseAuction(
    IN p_auction_id BIGINT,
    OUT p_status_code INT,
    OUT p_status_message VARCHAR(255),
    OUT p_result_id BIGINT
)
proc_label: BEGIN
    DECLARE v_existing_result_id BIGINT;
    DECLARE v_seller_id BIGINT;
    DECLARE v_title VARCHAR(150);
    DECLARE v_status VARCHAR(20);
    DECLARE v_end_time DATETIME;
    DECLARE v_winning_bid_id BIGINT DEFAULT NULL;
    DECLARE v_winner_id BIGINT DEFAULT NULL;
    DECLARE v_final_price DECIMAL(12, 2) DEFAULT 0.00;

    -- Error handler
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_status_code = 500;
        SET p_status_message = 'Internal database error during auction closure. Transaction rolled back.';
        SET p_result_id = NULL;
    END;

    START TRANSACTION;

    -- 1. Idempotency Check: Check if auction result already exists
    SELECT result_id INTO v_existing_result_id
    FROM auction_results
    WHERE auction_id = p_auction_id;

    IF v_existing_result_id IS NOT NULL THEN
        COMMIT;
        SET p_status_code = 200;
        SET p_status_message = 'Auction was already closed. Existing result retained.';
        SET p_result_id = v_existing_result_id;
        LEAVE proc_label;
    END IF;

    -- 2. Lock Auction Row
    SELECT seller_id, title, status, end_time
    INTO v_seller_id, v_title, v_status, v_end_time
    FROM auctions
    WHERE auction_id = p_auction_id
    FOR UPDATE;

    IF v_seller_id IS NULL THEN
        ROLLBACK;
        SET p_status_code = 404;
        SET p_status_message = 'Auction not found.';
        SET p_result_id = NULL;
        LEAVE proc_label;
    END IF;

    -- 3. Determine Highest Bid (Tie-breaking rule: highest amount, earliest bid_time, lowest bid_id)
    SELECT bid_id, bidder_id, bid_amount
    INTO v_winning_bid_id, v_winner_id, v_final_price
    FROM bids
    WHERE auction_id = p_auction_id AND status IN ('ACCEPTED', 'OUTBID')
    ORDER BY bid_amount DESC, bid_time ASC, bid_id ASC
    LIMIT 1;

    -- 4. Record Result and Update Auction
    IF v_winning_bid_id IS NOT NULL AND v_final_price > 0 THEN
        -- Case A: Auction Sold with Valid Winner
        INSERT INTO auction_results (auction_id, winner_id, winning_bid_id, final_price, closed_at, result_status)
        VALUES (p_auction_id, v_winner_id, v_winning_bid_id, v_final_price, NOW(), 'WON');

        SET p_result_id = LAST_INSERT_ID();

        UPDATE auctions
        SET status = 'CLOSED',
            current_price = v_final_price,
            updated_at = NOW()
        WHERE auction_id = p_auction_id;

        -- Notification to Winner
        INSERT INTO notifications (user_id, auction_id, title, message, notification_type)
        VALUES (
            v_winner_id,
            p_auction_id,
            'Congratulations! You won the auction',
            CONCAT('You won "', v_title, '" for ₹', v_final_price, '. Please proceed to simulated payment.'),
            'AUCTION_WON'
        );

        -- Notification to Seller
        INSERT INTO notifications (user_id, auction_id, title, message, notification_type)
        VALUES (
            v_seller_id,
            p_auction_id,
            'Your Auction has Closed',
            CONCAT('Your listing "', v_title, '" sold for ₹', v_final_price, '.'),
            'AUCTION_CLOSED'
        );

        -- Audit log
        INSERT INTO audit_logs (table_name, operation, record_id, changed_by, old_values, new_values)
        VALUES (
            'auction_results',
            'INSERT',
            p_result_id,
            'system_closure',
            JSON_OBJECT('auction_id', p_auction_id, 'status', v_status),
            JSON_OBJECT('result_status', 'WON', 'winner_id', v_winner_id, 'final_price', v_final_price)
        );

        SET p_status_message = CONCAT('Auction #', p_auction_id, ' successfully closed. Winner: User #', v_winner_id, ' at ₹', v_final_price);
    ELSE
        -- Case B: Auction Unsold (No Valid Bids)
        INSERT INTO auction_results (auction_id, winner_id, winning_bid_id, final_price, closed_at, result_status)
        VALUES (p_auction_id, NULL, NULL, 0.00, NOW(), 'UNSOLD');

        SET p_result_id = LAST_INSERT_ID();

        UPDATE auctions
        SET status = 'UNSOLD',
            updated_at = NOW()
        WHERE auction_id = p_auction_id;

        -- Notification to Seller
        INSERT INTO notifications (user_id, auction_id, title, message, notification_type)
        VALUES (
            v_seller_id,
            p_auction_id,
            'Auction Closed Unsold',
            CONCAT('Your listing "', v_title, '" ended with no qualifying bids.'),
            'AUCTION_UNSOLD'
        );

        -- Audit log
        INSERT INTO audit_logs (table_name, operation, record_id, changed_by, old_values, new_values)
        VALUES (
            'auction_results',
            'INSERT',
            p_result_id,
            'system_closure',
            JSON_OBJECT('auction_id', p_auction_id, 'status', v_status),
            JSON_OBJECT('result_status', 'UNSOLD', 'final_price', 0.00)
        );

        SET p_status_message = CONCAT('Auction #', p_auction_id, ' closed as UNSOLD (zero valid bids).');
    END IF;

    COMMIT;
    SET p_status_code = 200;
END proc_label$$

DELIMITER ;
