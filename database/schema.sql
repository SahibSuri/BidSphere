-- =============================================================================
-- BidSphere Online Auction Management System
-- Database Schema Definition (MySQL 8.0+)
-- Database: bidsphere_db
-- Engine: InnoDB for ACID compliance, referential integrity & row-level locking
-- =============================================================================

CREATE DATABASE IF NOT EXISTS bidsphere_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE bidsphere_db;

-- -----------------------------------------------------------------------------
-- 1. USERS TABLE
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    role ENUM('BUYER', 'SELLER', 'ADMIN') NOT NULL DEFAULT 'BUYER',
    phone VARCHAR(20) NULL,
    address TEXT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uk_users_username UNIQUE (username),
    CONSTRAINT uk_users_email UNIQUE (email),
    CONSTRAINT chk_users_email_format CHECK (email LIKE '%_@__%.__%')
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- 2. CATEGORIES TABLE
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    description VARCHAR(255) NULL,
    icon VARCHAR(50) NOT NULL DEFAULT 'tag',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uk_categories_name UNIQUE (name)
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- 3. AUCTIONS TABLE
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS auctions (
    auction_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    seller_id BIGINT NOT NULL,
    category_id INT NOT NULL,
    title VARCHAR(150) NOT NULL,
    description TEXT NOT NULL,
    starting_price DECIMAL(12, 2) NOT NULL,
    current_price DECIMAL(12, 2) NOT NULL,
    bid_increment DECIMAL(10, 2) NOT NULL DEFAULT 50.00,
    status ENUM('SCHEDULED', 'ACTIVE', 'CLOSED', 'CANCELLED', 'UNSOLD') NOT NULL DEFAULT 'SCHEDULED',
    start_time DATETIME NOT NULL,
    end_time DATETIME NOT NULL,
    image_url VARCHAR(500) NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_auctions_seller FOREIGN KEY (seller_id)
        REFERENCES users (user_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_auctions_category FOREIGN KEY (category_id)
        REFERENCES categories (category_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT chk_auctions_start_price CHECK (starting_price > 0),
    CONSTRAINT chk_auctions_curr_price CHECK (current_price >= starting_price),
    CONSTRAINT chk_auctions_increment CHECK (bid_increment > 0),
    CONSTRAINT chk_auctions_time_window CHECK (end_time > start_time)
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- 4. BIDS TABLE
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS bids (
    bid_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    auction_id BIGINT NOT NULL,
    bidder_id BIGINT NOT NULL,
    bid_amount DECIMAL(12, 2) NOT NULL,
    bid_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status ENUM('ACCEPTED', 'OUTBID', 'CANCELLED') NOT NULL DEFAULT 'ACCEPTED',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_bids_auction FOREIGN KEY (auction_id)
        REFERENCES auctions (auction_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_bids_bidder FOREIGN KEY (bidder_id)
        REFERENCES users (user_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT chk_bids_amount CHECK (bid_amount > 0)
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- 5. WATCHLIST TABLE
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS watchlist (
    watchlist_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    auction_id BIGINT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_watchlist_user FOREIGN KEY (user_id)
        REFERENCES users (user_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_watchlist_auction FOREIGN KEY (auction_id)
        REFERENCES auctions (auction_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT uk_watchlist_user_auction UNIQUE (user_id, auction_id)
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- 6. AUCTION_RESULTS TABLE
-- Exactly one final result per auction
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS auction_results (
    result_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    auction_id BIGINT NOT NULL,
    winner_id BIGINT NULL,
    winning_bid_id BIGINT NULL,
    final_price DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    closed_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    result_status ENUM('WON', 'UNSOLD', 'CANCELLED') NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_results_auction FOREIGN KEY (auction_id)
        REFERENCES auctions (auction_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_results_winner FOREIGN KEY (winner_id)
        REFERENCES users (user_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_results_bid FOREIGN KEY (winning_bid_id)
        REFERENCES bids (bid_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT uk_results_auction UNIQUE (auction_id),
    CONSTRAINT chk_results_price CHECK (final_price >= 0)
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- 7. PAYMENTS TABLE
-- Simulated payments linked to won auction results
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS payments (
    payment_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    result_id BIGINT NOT NULL,
    buyer_id BIGINT NOT NULL,
    amount DECIMAL(12, 2) NOT NULL,
    payment_method ENUM('SIMULATED_UPI', 'SIMULATED_NETBANKING', 'SIMULATED_CARD') NOT NULL DEFAULT 'SIMULATED_UPI',
    status ENUM('PENDING', 'SUCCESS', 'FAILED') NOT NULL DEFAULT 'PENDING',
    transaction_reference VARCHAR(100) NOT NULL,
    paid_at DATETIME NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_payments_result FOREIGN KEY (result_id)
        REFERENCES auction_results (result_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_payments_buyer FOREIGN KEY (buyer_id)
        REFERENCES users (user_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT uk_payments_tx_ref UNIQUE (transaction_reference),
    CONSTRAINT chk_payments_amount CHECK (amount > 0)
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- 8. NOTIFICATIONS TABLE
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS notifications (
    notification_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    auction_id BIGINT NULL,
    title VARCHAR(150) NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    notification_type ENUM(
        'BID_PLACED',
        'OUTBID',
        'AUCTION_WON',
        'AUCTION_CLOSED',
        'AUCTION_UNSOLD',
        'PAYMENT_RECEIVED'
    ) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_notifications_user FOREIGN KEY (user_id)
        REFERENCES users (user_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_notifications_auction FOREIGN KEY (auction_id)
        REFERENCES auctions (auction_id) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- 9. AUDIT_LOGS TABLE
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS audit_logs (
    log_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    table_name VARCHAR(50) NOT NULL,
    operation ENUM('INSERT', 'UPDATE', 'DELETE') NOT NULL,
    record_id BIGINT NOT NULL,
    changed_by VARCHAR(100) NULL,
    old_values JSON NULL,
    new_values JSON NULL,
    action_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;
