-- =============================================================================
-- BidSphere Online Auction Management System
-- Database Triggers Definition (Auditing & Automated Event Processing)
-- =============================================================================

USE bidsphere_db;

DROP TRIGGER IF EXISTS trg_after_user_update_audit;
DROP TRIGGER IF EXISTS trg_after_auction_update_audit;
DROP TRIGGER IF EXISTS trg_after_payment_insert_audit;
DROP TRIGGER IF EXISTS trg_after_payment_status_update;

DELIMITER $$

-- -----------------------------------------------------------------------------
-- 1. Trigger: Audit User Updates (Role / Status Changes)
-- -----------------------------------------------------------------------------
CREATE TRIGGER trg_after_user_update_audit
AFTER UPDATE ON users
FOR EACH ROW
BEGIN
    IF (OLD.role != NEW.role) OR (OLD.is_active != NEW.is_active) THEN
        INSERT INTO audit_logs (table_name, operation, record_id, changed_by, old_values, new_values)
        VALUES (
            'users',
            'UPDATE',
            NEW.user_id,
            CURRENT_USER(),
            JSON_OBJECT(
                'role', OLD.role,
                'is_active', OLD.is_active,
                'email', OLD.email
            ),
            JSON_OBJECT(
                'role', NEW.role,
                'is_active', NEW.is_active,
                'email', NEW.email
            )
        );
    END IF;
END$$

-- -----------------------------------------------------------------------------
-- 2. Trigger: Audit Auction State Transitions
-- -----------------------------------------------------------------------------
CREATE TRIGGER trg_after_auction_update_audit
AFTER UPDATE ON auctions
FOR EACH ROW
BEGIN
    IF (OLD.status != NEW.status) OR (OLD.current_price != NEW.current_price) THEN
        INSERT INTO audit_logs (table_name, operation, record_id, changed_by, old_values, new_values)
        VALUES (
            'auctions',
            'UPDATE',
            NEW.auction_id,
            CURRENT_USER(),
            JSON_OBJECT(
                'status', OLD.status,
                'current_price', OLD.current_price
            ),
            JSON_OBJECT(
                'status', NEW.status,
                'current_price', NEW.current_price
            )
        );
    END IF;
END$$

-- -----------------------------------------------------------------------------
-- 3. Trigger: Audit Payment Creation
-- -----------------------------------------------------------------------------
CREATE TRIGGER trg_after_payment_insert_audit
AFTER INSERT ON payments
FOR EACH ROW
BEGIN
    INSERT INTO audit_logs (table_name, operation, record_id, changed_by, old_values, new_values)
    VALUES (
        'payments',
        'INSERT',
        NEW.payment_id,
        CONCAT('buyer:', NEW.buyer_id),
        NULL,
        JSON_OBJECT(
            'result_id', NEW.result_id,
            'buyer_id', NEW.buyer_id,
            'amount', NEW.amount,
            'status', NEW.status,
            'tx_ref', NEW.transaction_reference
        )
    );
END$$

-- -----------------------------------------------------------------------------
-- 4. Trigger: Automated Notification on Successful Payment
-- -----------------------------------------------------------------------------
CREATE TRIGGER trg_after_payment_status_update
AFTER UPDATE ON payments
FOR EACH ROW
BEGIN
    DECLARE v_seller_id BIGINT;
    DECLARE v_auction_id BIGINT;
    DECLARE v_title VARCHAR(150);

    IF (OLD.status != NEW.status AND NEW.status = 'SUCCESS') THEN
        -- Find seller and auction details
        SELECT a.seller_id, a.auction_id, a.title 
        INTO v_seller_id, v_auction_id, v_title
        FROM auction_results r
        JOIN auctions a ON r.auction_id = a.auction_id
        WHERE r.result_id = NEW.result_id;

        IF v_seller_id IS NOT NULL THEN
            -- Notify Seller
            INSERT INTO notifications (user_id, auction_id, title, message, notification_type)
            VALUES (
                v_seller_id,
                v_auction_id,
                'Payment Received!',
                CONCAT('Payment of ₹', NEW.amount, ' for "', v_title, '" has been verified (Ref: ', NEW.transaction_reference, ').'),
                'PAYMENT_RECEIVED'
            );

            -- Notify Buyer
            INSERT INTO notifications (user_id, auction_id, title, message, notification_type)
            VALUES (
                NEW.buyer_id,
                v_auction_id,
                'Payment Confirmation',
                CONCAT('Your payment of ₹', NEW.amount, ' for "', v_title, '" was successful (Ref: ', NEW.transaction_reference, ').'),
                'PAYMENT_RECEIVED'
            );
        END IF;
    END IF;
END$$

DELIMITER ;
