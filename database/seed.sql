-- =============================================================================
-- BidSphere Online Auction Management System
-- Comprehensive Seed Data
-- =============================================================================

USE bidsphere_db;

-- Clear existing data in reverse dependency order
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE audit_logs;
TRUNCATE TABLE notifications;
TRUNCATE TABLE payments;
TRUNCATE TABLE auction_results;
TRUNCATE TABLE watchlist;
TRUNCATE TABLE bids;
TRUNCATE TABLE auctions;
TRUNCATE TABLE categories;
TRUNCATE TABLE users;
SET FOREIGN_KEY_CHECKS = 1;

-- -----------------------------------------------------------------------------
-- 1. USERS (12 Users: 1 Admin, 4 Sellers, 7 Buyers)
-- Passwords:
-- admin: Admin@BidSphere2026!
-- all others: Pass@1234
-- -----------------------------------------------------------------------------
INSERT INTO users (user_id, username, email, password_hash, full_name, role, phone, address, is_active)
VALUES
(1, 'admin', 'admin@bidsphere.com', '$argon2id$v=19$m=65536,t=3,p=4$m3NOKaW0tpbSGkPIGUPIOQ$v0xJG71SKRweOP7IYV6ACHQlM14ZeHy+O2VpMUtMTIQ', 'System Administrator', 'ADMIN', '+91-9876543210', 'Tech Park, Whitefield, Bangalore, Karnataka', TRUE),
(2, 'aravind_tech', 'aravind.sharma@example.com', '$argon2id$v=19$m=65536,t=3,p=4$dw4hBGBszXkvxVir1TpHyA$rmBj6AQGLYl469u3E+D5RzvI3v2jSatsR2QEFyXZEsU', 'Aravind Sharma', 'SELLER', '+91-9811223344', 'Connaught Place, New Delhi, Delhi', TRUE),
(3, 'priya_artistry', 'priya.nair@example.com', '$argon2id$v=19$m=65536,t=3,p=4$dw4hBGBszXkvxVir1TpHyA$rmBj6AQGLYl469u3E+D5RzvI3v2jSatsR2QEFyXZEsU', 'Priya Nair', 'SELLER', '+91-9822334455', 'Bandra West, Mumbai, Maharashtra', TRUE),
(4, 'rajesh_antiques', 'rajesh.verma@example.com', '$argon2id$v=19$m=65536,t=3,p=4$dw4hBGBszXkvxVir1TpHyA$rmBj6AQGLYl469u3E+D5RzvI3v2jSatsR2QEFyXZEsU', 'Rajesh Verma', 'SELLER', '+91-9833445566', 'Civil Lines, Jaipur, Rajasthan', TRUE),
(5, 'deepa_jewels', 'deepa.patel@example.com', '$argon2id$v=19$m=65536,t=3,p=4$dw4hBGBszXkvxVir1TpHyA$rmBj6AQGLYl469u3E+D5RzvI3v2jSatsR2QEFyXZEsU', 'Deepa Patel', 'SELLER', '+91-9844556677', 'Navrangpura, Ahmedabad, Gujarat', TRUE),
(6, 'vikram_b', 'vikram.joshi@example.com', '$argon2id$v=19$m=65536,t=3,p=4$dw4hBGBszXkvxVir1TpHyA$rmBj6AQGLYl469u3E+D5RzvI3v2jSatsR2QEFyXZEsU', 'Vikram Joshi', 'BUYER', '+91-9855667788', 'Indiranagar, Bangalore, Karnataka', TRUE),
(7, 'sneha_rao', 'sneha.rao@example.com', '$argon2id$v=19$m=65536,t=3,p=4$dw4hBGBszXkvxVir1TpHyA$rmBj6AQGLYl469u3E+D5RzvI3v2jSatsR2QEFyXZEsU', 'Sneha Rao', 'BUYER', '+91-9866778899', 'Jubilee Hills, Hyderabad, Telangana', TRUE),
(8, 'amit_kumar', 'amit.kumar@example.com', '$argon2id$v=19$m=65536,t=3,p=4$dw4hBGBszXkvxVir1TpHyA$rmBj6AQGLYl469u3E+D5RzvI3v2jSatsR2QEFyXZEsU', 'Amit Kumar', 'BUYER', '+91-9877889900', 'Salt Lake Sector V, Kolkata, West Bengal', TRUE),
(9, 'ananya_sen', 'ananya.sen@example.com', '$argon2id$v=19$m=65536,t=3,p=4$dw4hBGBszXkvxVir1TpHyA$rmBj6AQGLYl469u3E+D5RzvI3v2jSatsR2QEFyXZEsU', 'Ananya Sen', 'BUYER', '+91-9888990011', 'Alipore, Kolkata, West Bengal', TRUE),
(10, 'karthik_m', 'karthik.menon@example.com', '$argon2id$v=19$m=65536,t=3,p=4$dw4hBGBszXkvxVir1TpHyA$rmBj6AQGLYl469u3E+D5RzvI3v2jSatsR2QEFyXZEsU', 'Karthik Menon', 'BUYER', '+91-9899001122', 'Panampilly Nagar, Kochi, Kerala', TRUE),
(11, 'rohit_sharma', 'rohit.bidder@example.com', '$argon2id$v=19$m=65536,t=3,p=4$dw4hBGBszXkvxVir1TpHyA$rmBj6AQGLYl469u3E+D5RzvI3v2jSatsR2QEFyXZEsU', 'Rohit Sharma', 'BUYER', '+91-9900112233', 'Koregaon Park, Pune, Maharashtra', TRUE),
(12, 'inactive_user', 'inactive@example.com', '$argon2id$v=19$m=65536,t=3,p=4$dw4hBGBszXkvxVir1TpHyA$rmBj6AQGLYl469u3E+D5RzvI3v2jSatsR2QEFyXZEsU', 'Inactive Account', 'BUYER', '+91-9911223344', 'Sector 18, Noida, Uttar Pradesh', FALSE);

-- -----------------------------------------------------------------------------
-- 2. CATEGORIES (6 Diverse Categories)
-- -----------------------------------------------------------------------------
INSERT INTO categories (category_id, name, description, icon)
VALUES
(1, 'Consumer Electronics', 'Smartphones, laptops, audio gear, smartwatches and gaming hardware', 'cpu'),
(2, 'Fine Art & Paintings', 'Original canvas art, oil paintings, sketches and contemporary folk art', 'palette'),
(3, 'Vintage & Collectibles', 'Rare stamps, historical coins, retro vinyl records and vintage cameras', 'watch'),
(4, 'Luxury Watches & Jewelry', 'Swiss chronographs, gold jewelry, gemstone rings and heirloom ornaments', 'gem'),
(5, 'Rare Books & Manuscripts', 'First edition novels, autographed literary works and rare maps', 'book'),
(6, 'Automotive & Memorabilia', 'Classic bike accessories, diecast models and racing memorabilia', 'truck');

-- -----------------------------------------------------------------------------
-- 3. AUCTIONS (16 Auctions spanning SCHEDULED, ACTIVE, CLOSED, UNSOLD, CANCELLED)
-- -----------------------------------------------------------------------------
INSERT INTO auctions (auction_id, seller_id, category_id, title, description, starting_price, current_price, bid_increment, status, start_time, end_time, image_url)
VALUES
-- ACTIVE AUCTIONS (Open for bidding right now)
(1, 2, 1, 'Apple MacBook Pro M3 Max 16-inch (1TB, 36GB RAM)', 'Space Black Apple MacBook Pro M3 Max in pristine condition with 10 months warranty remaining. Includes MagSafe charger and original box.', 180000.00, 215000.00, 5000.00, 'ACTIVE', DATE_SUB(NOW(), INTERVAL 2 DAY), DATE_ADD(NOW(), INTERVAL 3 DAY), 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=800&q=80'),
(2, 2, 1, 'Sony PlayStation 5 Disc Edition + 2 DualSense Controllers', 'Lightly used Sony PS5 disc edition with Spider-Man 2 and God of War Ragnarok discs. Mint condition with original packaging.', 35000.00, 42000.00, 1000.00, 'ACTIVE', DATE_SUB(NOW(), INTERVAL 1 DAY), DATE_ADD(NOW(), INTERVAL 2 DAY), 'https://images.unsplash.com/photo-1606813907291-d86efa9b94db?auto=format&fit=crop&w=800&q=80'),
(3, 3, 2, 'Authentic Tanjore Painting - Lord Krishna in Pure 22K Gold Foil', 'Handmade 24x30 inch traditional Thanjavur painting embellished with certified 22 karat gold leaf and Jaipur semi-precious stones. Teakwood framed.', 45000.00, 55000.00, 2000.00, 'ACTIVE', DATE_SUB(NOW(), INTERVAL 3 DAY), DATE_ADD(NOW(), INTERVAL 4 DAY), 'https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?auto=format&fit=crop&w=800&q=80'),
(4, 4, 3, '1947 Republic of India Inaugural Stamp Collection & First Day Cover', 'Complete framed set of 3 first stamps of independent India (Ashoka Lion, National Flag, Douglas DC-4 Aircraft) in VF-NH condition.', 25000.00, 31000.00, 1000.00, 'ACTIVE', DATE_SUB(NOW(), INTERVAL 1 DAY), DATE_ADD(NOW(), INTERVAL 5 DAY), 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?auto=format&fit=crop&w=800&q=80'),
(5, 5, 4, 'Omega Seamaster Diver 300M Co-Axial Master Chronometer (Blue Dial)', 'Original Omega Seamaster automatic timepiece with steel bracelet, laser-engraved blue ceramic dial. Box and chronometer certification card included.', 280000.00, 310000.00, 10000.00, 'ACTIVE', DATE_SUB(NOW(), INTERVAL 2 DAY), DATE_ADD(NOW(), INTERVAL 1 DAY), 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=800&q=80'),
(6, 2, 1, 'Sony Alpha A7 IV Full-Frame Mirrorless Camera + 24-70mm GM Lens', '33MP full-frame hybrid camera with low shutter count (< 4,000 actuations). Perfect for studio photography and 4K60p cinematography.', 160000.00, 160000.00, 5000.00, 'ACTIVE', DATE_SUB(NOW(), INTERVAL 12 HOUR), DATE_ADD(NOW(), INTERVAL 4 DAY), 'https://images.unsplash.com/photo-1516035069371-29a1b244cc32?auto=format&fit=crop&w=800&q=80'),
(7, 3, 2, 'Contemporary Abstract Canvas "Monsoon Raga" by K. G. Subramanyan School', 'Acrylic on Belgian linen, 36x48 inches. Gallery-stretched, vibrant blues and ochre tones with artist provenance certificate.', 60000.00, 72000.00, 2000.00, 'ACTIVE', DATE_SUB(NOW(), INTERVAL 2 DAY), DATE_ADD(NOW(), INTERVAL 3 DAY), 'https://images.unsplash.com/photo-1579783902614-a3fb3927b675?auto=format&fit=crop&w=800&q=80'),
(8, 4, 3, 'Vintage Leica M3 Rangefinder (1956 Double Stroke) + 50mm Summicron', 'Iconic mechanical 35mm rangefinder camera in fully operational condition. Shutter speeds calibrated, clear viewfinder, vulcanite intact.', 120000.00, 135000.00, 5000.00, 'ACTIVE', DATE_SUB(NOW(), INTERVAL 1 DAY), DATE_ADD(NOW(), INTERVAL 2 DAY), 'https://images.unsplash.com/photo-1512790182412-b19e6d62bc39?auto=format&fit=crop&w=800&q=80'),

-- SCHEDULED AUCTIONS (Upcoming)
(9, 5, 4, '18K White Gold Solitaire Diamond Ring (1.50 Carat, VVS1, GIA Certified)', 'Magnificent round brilliant solitaire diamond set in an 18-karat white gold cathedral mount. Laser-inscribed with GIA dossier.', 350000.00, 350000.00, 10000.00, 'SCHEDULED', DATE_ADD(NOW(), INTERVAL 2 DAY), DATE_ADD(NOW(), INTERVAL 7 DAY), 'https://images.unsplash.com/photo-1605100804763-247f67b3557e?auto=format&fit=crop&w=800&q=80'),
(10, 4, 5, 'Rabindranath Tagore Gitanjali 1912 First English Edition (Macmillan)', 'Rare collector copy of Gitanjali (Song Offerings) with introduction by W.B. Yeats. Original dark green cloth with gilt lettering.', 75000.00, 75000.00, 2500.00, 'SCHEDULED', DATE_ADD(NOW(), INTERVAL 3 DAY), DATE_ADD(NOW(), INTERVAL 8 DAY), 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?auto=format&fit=crop&w=800&q=80'),

-- CLOSED AUCTIONS (Won by bidders with settlement)
(11, 2, 1, 'Apple iPhone 15 Pro Max 256GB Natural Titanium (Unlocked)', 'Flagship Apple smartphone, battery health 99%, flawless physical state with AppleCare+ cover.', 90000.00, 108000.00, 2000.00, 'CLOSED', DATE_SUB(NOW(), INTERVAL 10 DAY), DATE_SUB(NOW(), INTERVAL 5 DAY), 'https://images.unsplash.com/photo-1695048133142-1a20484d2569?auto=format&fit=crop&w=800&q=80'),
(12, 3, 2, 'Heritage Madhubani Handpainted Folk Triptych (Natural Dyes)', 'Three-panel Mithila artwork created with bamboo twigs, powdered rice and organic vegetable pigments on handmade paper.', 18000.00, 24000.00, 1000.00, 'CLOSED', DATE_SUB(NOW(), INTERVAL 8 DAY), DATE_SUB(NOW(), INTERVAL 3 DAY), 'https://images.unsplash.com/photo-1582561121890-096738980860?auto=format&fit=crop&w=800&q=80'),
(13, 5, 4, 'Rolex Datejust 36 Stainless Steel & 18K Yellow Gold (Fluted Bezel)', 'Classic two-tone Jubilee bracelet luxury timepiece with champagne dial and Roman numerals. Serviced 2024.', 450000.00, 520000.00, 15000.00, 'CLOSED', DATE_SUB(NOW(), INTERVAL 14 DAY), DATE_SUB(NOW(), INTERVAL 7 DAY), 'https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?auto=format&fit=crop&w=800&q=80'),

-- UNSOLD AUCTIONS (Ended without any qualifying bids)
(14, 4, 6, 'Royal Enfield 1968 Cast Iron Bullet 350 Restoration Project', 'Partially restored vintage Chennai-built Bullet with original heavy crank and Lucas magneto ignition. Needs assembly.', 80000.00, 80000.00, 2000.00, 'UNSOLD', DATE_SUB(NOW(), INTERVAL 12 DAY), DATE_SUB(NOW(), INTERVAL 6 DAY), 'https://images.unsplash.com/photo-1558981806-ec527fa84c39?auto=format&fit=crop&w=800&q=80'),
(15, 3, 5, 'Ancient Sanskrit Palm Leaf Manuscript Fragment (18th Century CE)', 'Folio of astronomical calculation verses inscribed in Grantha script on dried palmyra leaf. Museum preserved.', 110000.00, 110000.00, 5000.00, 'UNSOLD', DATE_SUB(NOW(), INTERVAL 9 DAY), DATE_SUB(NOW(), INTERVAL 4 DAY), 'https://images.unsplash.com/photo-1457369804613-52c61a468e7d?auto=format&fit=crop&w=800&q=80'),

-- CANCELLED AUCTION (Cancelled by seller before bidding)
(16, 2, 1, 'Custom Liquid-Cooled Gaming PC (RTX 4090, Intel i9-14900K)', 'High-end custom rig with EKWB custom loop, Lian Li O11 Dynamic EVO XL case. Withdrawn by seller due to hardware repair.', 260000.00, 260000.00, 5000.00, 'CANCELLED', DATE_SUB(NOW(), INTERVAL 4 DAY), DATE_ADD(NOW(), INTERVAL 2 DAY), 'https://images.unsplash.com/photo-1587202372775-e229f172b9d7?auto=format&fit=crop&w=800&q=80');

-- -----------------------------------------------------------------------------
-- 4. BIDS (30 realistic bids across active and closed auctions)
-- -----------------------------------------------------------------------------
INSERT INTO bids (bid_id, auction_id, bidder_id, bid_amount, bid_time, status)
VALUES
-- Auction 1 (MacBook Pro)
(1, 1, 6, 185000.00, DATE_SUB(NOW(), INTERVAL 40 HOUR), 'OUTBID'),
(2, 1, 7, 195000.00, DATE_SUB(NOW(), INTERVAL 35 HOUR), 'OUTBID'),
(3, 1, 8, 200000.00, DATE_SUB(NOW(), INTERVAL 28 HOUR), 'OUTBID'),
(4, 1, 6, 210000.00, DATE_SUB(NOW(), INTERVAL 18 HOUR), 'OUTBID'),
(5, 1, 10, 215000.00, DATE_SUB(NOW(), INTERVAL 6 HOUR), 'ACCEPTED'),

-- Auction 2 (PS5 Disc)
(6, 2, 9, 36000.00, DATE_SUB(NOW(), INTERVAL 20 HOUR), 'OUTBID'),
(7, 2, 11, 38000.00, DATE_SUB(NOW(), INTERVAL 16 HOUR), 'OUTBID'),
(8, 2, 7, 40000.00, DATE_SUB(NOW(), INTERVAL 10 HOUR), 'OUTBID'),
(9, 2, 9, 42000.00, DATE_SUB(NOW(), INTERVAL 4 HOUR), 'ACCEPTED'),

-- Auction 3 (Tanjore Painting)
(10, 3, 8, 47000.00, DATE_SUB(NOW(), INTERVAL 60 HOUR), 'OUTBID'),
(11, 3, 9, 51000.00, DATE_SUB(NOW(), INTERVAL 44 HOUR), 'OUTBID'),
(12, 3, 8, 55000.00, DATE_SUB(NOW(), INTERVAL 20 HOUR), 'ACCEPTED'),

-- Auction 4 (Stamp Collection)
(13, 4, 10, 26000.00, DATE_SUB(NOW(), INTERVAL 22 HOUR), 'OUTBID'),
(14, 4, 11, 28000.00, DATE_SUB(NOW(), INTERVAL 18 HOUR), 'OUTBID'),
(15, 4, 6, 31000.00, DATE_SUB(NOW(), INTERVAL 8 HOUR), 'ACCEPTED'),

-- Auction 5 (Omega Seamaster)
(16, 5, 7, 290000.00, DATE_SUB(NOW(), INTERVAL 42 HOUR), 'OUTBID'),
(17, 5, 8, 300000.00, DATE_SUB(NOW(), INTERVAL 30 HOUR), 'OUTBID'),
(18, 5, 11, 310000.00, DATE_SUB(NOW(), INTERVAL 12 HOUR), 'ACCEPTED'),

-- Auction 7 (Abstract Canvas)
(19, 7, 9, 64000.00, DATE_SUB(NOW(), INTERVAL 36 HOUR), 'OUTBID'),
(20, 7, 10, 68000.00, DATE_SUB(NOW(), INTERVAL 24 HOUR), 'OUTBID'),
(21, 7, 9, 72000.00, DATE_SUB(NOW(), INTERVAL 10 HOUR), 'ACCEPTED'),

-- Auction 8 (Leica M3)
(22, 8, 6, 125000.00, DATE_SUB(NOW(), INTERVAL 20 HOUR), 'OUTBID'),
(23, 8, 8, 135000.00, DATE_SUB(NOW(), INTERVAL 6 HOUR), 'ACCEPTED'),

-- Auction 11 (Closed iPhone 15 Pro Max)
(24, 11, 6, 92000.00, DATE_SUB(NOW(), INTERVAL 9 DAY), 'OUTBID'),
(25, 11, 7, 98000.00, DATE_SUB(NOW(), INTERVAL 8 DAY), 'OUTBID'),
(26, 11, 10, 104000.00, DATE_SUB(NOW(), INTERVAL 7 DAY), 'OUTBID'),
(27, 11, 6, 108000.00, DATE_SUB(NOW(), INTERVAL 6 DAY), 'ACCEPTED'),

-- Auction 12 (Closed Madhubani Folk Art)
(28, 12, 8, 200000.00, DATE_SUB(NOW(), INTERVAL 7 DAY), 'OUTBID'),
(29, 12, 9, 24000.00, DATE_SUB(NOW(), INTERVAL 5 DAY), 'ACCEPTED'),

-- Auction 13 (Closed Rolex Datejust)
(30, 13, 7, 480000.00, DATE_SUB(NOW(), INTERVAL 12 DAY), 'OUTBID'),
(31, 13, 11, 520000.00, DATE_SUB(NOW(), INTERVAL 8 DAY), 'ACCEPTED');

-- -----------------------------------------------------------------------------
-- 5. WATCHLIST (Buyer Bookmarks)
-- -----------------------------------------------------------------------------
INSERT INTO watchlist (watchlist_id, user_id, auction_id)
VALUES
(1, 6, 1),
(2, 6, 5),
(3, 7, 1),
(4, 7, 2),
(5, 7, 5),
(6, 8, 3),
(7, 8, 4),
(8, 9, 3),
(9, 9, 7),
(10, 10, 1),
(11, 10, 8),
(12, 11, 5);

-- -----------------------------------------------------------------------------
-- 6. AUCTION_RESULTS (Final settlement records for closed and unsold auctions)
-- Exactly 1 result record per finished auction
-- -----------------------------------------------------------------------------
INSERT INTO auction_results (result_id, auction_id, winner_id, winning_bid_id, final_price, closed_at, result_status)
VALUES
(1, 11, 6, 27, 108000.00, DATE_SUB(NOW(), INTERVAL 5 DAY), 'WON'),
(2, 12, 9, 29, 24000.00, DATE_SUB(NOW(), INTERVAL 3 DAY), 'WON'),
(3, 13, 11, 31, 520000.00, DATE_SUB(NOW(), INTERVAL 7 DAY), 'WON'),
(4, 14, NULL, NULL, 0.00, DATE_SUB(NOW(), INTERVAL 6 DAY), 'UNSOLD'),
(5, 15, NULL, NULL, 0.00, DATE_SUB(NOW(), INTERVAL 4 DAY), 'UNSOLD');

-- -----------------------------------------------------------------------------
-- 7. PAYMENTS (Simulated Payments for Won Auctions)
-- -----------------------------------------------------------------------------
INSERT INTO payments (payment_id, result_id, buyer_id, amount, payment_method, status, transaction_reference, paid_at)
VALUES
(1, 1, 6, 108000.00, 'SIMULATED_UPI', 'SUCCESS', 'UPI/20261019/BSPHR8849201', DATE_SUB(NOW(), INTERVAL 4 DAY)),
(2, 2, 9, 24000.00, 'SIMULATED_NETBANKING', 'SUCCESS', 'NB/20261022/BSPHR7730114', DATE_SUB(NOW(), INTERVAL 2 DAY)),
(3, 3, 11, 520000.00, 'SIMULATED_CARD', 'PENDING', 'CARD/20261024/BSPHR9910023', NULL);

-- -----------------------------------------------------------------------------
-- 8. NOTIFICATIONS (Outbid, closure, win notifications)
-- -----------------------------------------------------------------------------
INSERT INTO notifications (notification_id, user_id, auction_id, title, message, is_read, notification_type)
VALUES
(1, 6, 11, 'Congratulations! You won the auction', 'You won "Apple iPhone 15 Pro Max 256GB" for ₹108000.00.', TRUE, 'AUCTION_WON'),
(2, 2, 11, 'Your Auction has Closed', 'Your listing "Apple iPhone 15 Pro Max 256GB" sold for ₹108000.00.', TRUE, 'AUCTION_CLOSED'),
(3, 9, 12, 'Congratulations! You won the auction', 'You won "Heritage Madhubani Handpainted Folk Triptych" for ₹24000.00.', TRUE, 'AUCTION_WON'),
(4, 11, 13, 'Congratulations! You won the auction', 'You won "Rolex Datejust 36 Stainless Steel" for ₹520000.00. Payment is currently pending.', FALSE, 'AUCTION_WON'),
(5, 4, 14, 'Auction Closed Unsold', 'Your listing "Royal Enfield 1968 Cast Iron Bullet 350" ended without qualifying bids.', TRUE, 'AUCTION_UNSOLD'),
(6, 6, 1, 'You have been outbid!', 'A higher bid of ₹215000.00 was placed on auction #1 (Apple MacBook Pro M3 Max).', FALSE, 'OUTBID'),
(7, 7, 2, 'You have been outbid!', 'A higher bid of ₹42000.00 was placed on auction #2 (Sony PlayStation 5).', FALSE, 'OUTBID');

-- -----------------------------------------------------------------------------
-- 9. AUDIT_LOGS (Demonstration Audit Records)
-- -----------------------------------------------------------------------------
INSERT INTO audit_logs (table_name, operation, record_id, changed_by, old_values, new_values, action_timestamp)
VALUES
('auctions', 'INSERT', 1, 'aravind_tech', NULL, JSON_OBJECT('title', 'Apple MacBook Pro M3 Max', 'starting_price', 180000.00), DATE_SUB(NOW(), INTERVAL 2 DAY)),
('bids', 'INSERT', 5, 'karthik_m', JSON_OBJECT('current_price', 210000.00), JSON_OBJECT('bid_amount', 215000.00, 'auction_id', 1), DATE_SUB(NOW(), INTERVAL 6 HOUR)),
('auction_results', 'INSERT', 1, 'system_closure', JSON_OBJECT('auction_id', 11, 'status', 'ACTIVE'), JSON_OBJECT('result_status', 'WON', 'winner_id', 6, 'final_price', 108000.00), DATE_SUB(NOW(), INTERVAL 5 DAY)),
('payments', 'INSERT', 1, 'buyer:6', NULL, JSON_OBJECT('result_id', 1, 'amount', 108000.00, 'status', 'SUCCESS'), DATE_SUB(NOW(), INTERVAL 4 DAY));
