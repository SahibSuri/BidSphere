# 🏛️ BidSphere — Online Auction Management System
### A Full-Stack, Enterprise DBMS Academic Project (B.Tech Computer Science)

BidSphere is a complete, database-driven online auction management system engineered using **MySQL 8.0+**, **FastAPI**, and **Streamlit**. It demonstrates real-world relational database design, ACID compliance, pessimistic concurrency control (`SELECT ... FOR UPDATE`), triggers, stored procedures, analytical views, and an interactive frontend.

---

## 📋 Technology Stack

- **Database:** MySQL 8.0+ (InnoDB Engine)
- **Database GUI:** MySQL Workbench
- **Language:** Python 3.11 or 3.12
- **Backend API:** FastAPI & Uvicorn (ASGI)
- **Database Driver & ORM:** SQLAlchemy 2.0 & PyMySQL
- **Frontend UI:** Streamlit (Communicates strictly over HTTP REST)
- **Data & Visualizations:** Pandas & Plotly
- **Security & Password Hashing:** Argon2 (`argon2-cffi` & `passlib`) & PyJWT
- **Testing:** pytest & FastAPI TestClient

---

## 📁 Project Directory Structure

```
bidsphere/
├── README.md                      # Complete system setup and documentation
├── requirements.txt               # Pinned Python package dependencies
├── .env.example                   # Environment configuration template
├── .env                           # Local environment file (ignored by Git)
├── .gitignore                     # Git ignore rules for secrets and environments
├── database/                      # Reproducible MySQL 8.0+ database scripts
│   ├── schema.sql                 # Database definition and 9 core tables with constraints
│   ├── indexes.sql                # Performance indexes on foreign keys and filters
│   ├── views.sql                  # Analytical SQL views (vw_active_auctions, etc.)
│   ├── procedures.sql             # Stored procedures (PlaceBid, CloseAuction with FOR UPDATE)
│   ├── triggers.sql               # Automated audit logging and notification triggers
│   ├── seed.sql                   # Realistic demo dataset across all 9 tables
│   └── er_diagram.mmd             # Mermaid ER diagram source
├── backend/                       # FastAPI application tier
│   ├── main.py                    # Application entrypoint, CORS, routers & health check
│   ├── database.py                # SQLAlchemy engine, connection pooling & health checks
│   ├── models.py                  # SQLAlchemy ORM models matching database schema
│   ├── schemas.py                 # Pydantic v2 schemas for request/response validation
│   ├── dependencies.py            # JWT authentication, Argon2 hashing & RBAC dependencies
│   ├── routers/                   # Modular REST API endpoints
│   │   ├── auth.py                # Login, registration, profile & me endpoints
│   │   ├── auctions.py            # Auction listing, creation, editing, closing
│   │   ├── bids.py                # PlaceBid procedure invocation & bid history
│   │   ├── watchlist.py           # Add/remove/list user bookmarks
│   │   ├── payments.py            # Simulated payment settlement & receipt generation
│   │   ├── notifications.py       # User alerts & read state management
│   │   ├── dashboard.py           # Seller, buyer, and results analytics endpoints
│   │   └── admin.py               # Administrative metrics, user management & audit logs
│   ├── services/                  # Business logic services
│   │   ├── auth_service.py        # Admin bootstrap & credential validation
│   │   ├── auction_service.py     # Auction lifecycle & auto-closure
│   │   └── bid_service.py         # Transactional stored procedure execution
│   └── tests/                     # 26 automated integration tests
│       ├── conftest.py            # Test fixtures and authenticated tokens
│       ├── test_auth.py           # Registration, login, duplicate rejection & RBAC
│       ├── test_auctions.py       # Creation permissions, dates, search, edit lock
│       ├── test_bids.py           # Valid bids, below-minimum & self-bidding rejection
│       ├── test_concurrency.py    # Simultaneous bids & transaction rollback safety
│       ├── test_closure.py        # Winner determination, unsold lots & idempotency
│       ├── test_payments.py       # Duplicate payment prevention & authorization
│       └── test_constraints.py    # Foreign-key & MySQL CHECK constraint enforcement
├── frontend/                      # Streamlit presentation tier
│   ├── app.py                     # Main Streamlit application entrypoint
│   ├── api_client.py              # Centralized HTTP client communicating with FastAPI
│   ├── components/                # Reusable UI components
│   │   ├── styles.py              # Custom CSS design system & typography
│   │   ├── navbar.py              # Role-aware sidebar navigation & user status
│   │   └── cards.py               # Status badges, INR formatters & KPI cards
│   └── views/                     # 11 distinct Streamlit pages
│       ├── marketplace.py         # Live auction cards, filters & search
│       ├── auth_page.py           # Sign in, registration & quick demo logins
│       ├── auction_detail.py      # Live bidding console & bid history table
│       ├── my_bids.py             # Active positions & submission history
│       ├── watchlist_page.py      # Bookmarked auctions
│       ├── seller_dashboard.py    # Listing creation & seller analytics
│       ├── auction_results.py     # Final settlement records & winner registry
│       ├── notifications_page.py  # User notifications with read toggle
│       ├── payments_page.py       # Simulated payments & receipt vouchers
│       ├── admin_dashboard.py     # Admin KPIs, Plotly charts & user moderation
│       └── system_status.py       # Infrastructure & connectivity diagnostics
└── docs/                          # Project documentation and reports
    ├── architecture.mmd           # 3-tier system architecture diagram
    ├── sql_queries.sql            # 16 demonstration queries covering DBMS concepts
    ├── test_plan.md               # Detailed test matrix and verified results
    └── project_report.md          # Comprehensive academic DBMS project report
```

---

## 🚀 Complete Setup & Execution Instructions

Run all commands from the repository root: `/Users/apple/Desktop/dbms_project` (or your project directory).

### Step 1: Clone and Configure Environment

```bash
# Copy example configuration to .env
cp .env.example .env
```

Review `.env` to verify your MySQL credentials and ports:
```ini
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=bidsphere_user
DB_PASSWORD=bidsphere_pass
DB_NAME=bidsphere_db
SECRET_KEY=bidsphere_super_secret_jwt_key_change_in_production_min_32_chars
API_BASE_URL=http://localhost:8000/api/v1
```

### Step 2: Python Virtual Environment & Dependencies

#### macOS / Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

#### Windows (Command Prompt / PowerShell):
```cmd
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Step 3: MySQL 8.0+ Database Setup

Ensure MySQL Server 8.0+ is running.

#### Create Database & User (Run in MySQL CLI or MySQL Workbench as root):
```sql
CREATE DATABASE IF NOT EXISTS bidsphere_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'bidsphere_user'@'localhost' IDENTIFIED BY 'bidsphere_pass';
CREATE USER IF NOT EXISTS 'bidsphere_user'@'127.0.0.1' IDENTIFIED BY 'bidsphere_pass';
GRANT ALL PRIVILEGES ON bidsphere_db.* TO 'bidsphere_user'@'localhost';
GRANT ALL PRIVILEGES ON bidsphere_db.* TO 'bidsphere_user'@'127.0.0.1';
FLUSH PRIVILEGES;
```

#### Execute SQL Scripts in Exact Order:
```bash
# macOS / Linux:
mysql -u root bidsphere_db < database/schema.sql
mysql -u root bidsphere_db < database/indexes.sql
mysql -u root bidsphere_db < database/views.sql
mysql -u root bidsphere_db < database/triggers.sql
mysql -u root bidsphere_db < database/procedures.sql
mysql -u root bidsphere_db < database/seed.sql

# Windows (Command Prompt):
mysql -u root -p bidsphere_db < database\schema.sql
mysql -u root -p bidsphere_db < database\indexes.sql
mysql -u root -p bidsphere_db < database\views.sql
mysql -u root -p bidsphere_db < database\triggers.sql
mysql -u root -p bidsphere_db < database\procedures.sql
mysql -u root -p bidsphere_db < database\seed.sql
```

*(Alternatively, open each script in MySQL Workbench and execute via the Lightning bolt icon).*

### Step 4: Run Automated Tests

Execute the 26 automated pytest integration tests:
```bash
pytest -v backend/tests
```

All 26 tests will run against live MySQL and output:
```
======================== 26 passed, 4 warnings in 0.75s ========================
```

### Step 5: Start the FastAPI Backend

```bash
# Terminal 1:
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
- Interactive Swagger UI: `http://127.0.0.1:8000/docs`
- Health Diagnostic: `http://127.0.0.1:8000/api/v1/health`

### Step 6: Start the Streamlit Frontend

```bash
# Terminal 2 (with virtual environment activated):
PYTHONPATH=. streamlit run frontend/app.py --server.port 8501
```
- Open your browser to: `http://localhost:8501`

---

## 👥 Documented Demonstration Accounts

All demo user accounts are pre-loaded via `database/seed.sql`:

| Role | Username | Email | Password | Description |
|---|---|---|---|---|
| **ADMIN** | `admin` | `admin@bidsphere.com` | `Admin@BidSphere2026!` | System Administrator with full oversight |
| **SELLER** | `aravind_tech` | `aravind.sharma@example.com` | `Pass@1234` | Seller: Consumer Electronics listings |
| **SELLER** | `priya_artistry`| `priya.nair@example.com` | `Pass@1234` | Seller: Traditional Indian Art & Paintings |
| **SELLER** | `deepa_jewels` | `deepa.patel@example.com` | `Pass@1234` | Seller: Luxury Watches & Jewelry |
| **BUYER** | `vikram_b` | `vikram.joshi@example.com` | `Pass@1234` | Active bidder (Bangalore) |
| **BUYER** | `sneha_rao` | `sneha.rao@example.com` | `Pass@1234` | Active bidder (Hyderabad) |
| **BUYER** | `ananya_sen` | `ananya.sen@example.com` | `Pass@1234` | Active bidder (Kolkata) |
| **INACTIVE**| `inactive_user`| `inactive@example.com` | `Pass@1234` | Deactivated test account |

*(Tip: On the Sign In page, use the **Quick Login** buttons for instant one-click authentication).*

---

## 🔧 Troubleshooting Guide

1. **Error: Can't connect to MySQL server on '127.0.0.1' (Connection Refused)**
   - Check if MySQL service is running:
     - macOS: `brew services list` or `brew services start mysql@8.4`
     - Linux: `sudo systemctl status mysql`
     - Windows: Open Services (`services.msc`) -> start "MySQL80"
2. **Error: Access Denied for user 'bidsphere_user'**
   - Re-run the `GRANT ALL PRIVILEGES ON bidsphere_db.* TO 'bidsphere_user'@'localhost';` command in MySQL as root.
3. **Streamlit ModuleNotFoundError: No module named 'frontend'**
   - Run Streamlit with `PYTHONPATH=.` prepended: `PYTHONPATH=. streamlit run frontend/app.py`
4. **Port 8000 or 8501 already in use**
   - Find and terminate the process:
     - macOS/Linux: `lsof -i :8000` -> `kill -9 <PID>`
     - Windows: `netstat -ano | findstr :8000` -> `taskkill /PID <PID> /F`

---

## 📜 Academic Project Submission Details

- **Academic Project Report:** Full documentation is located in [`docs/project_report.md`](docs/project_report.md).
- **Physical EER Diagram:** Reverse-engineer `database/schema.sql` in MySQL Workbench following instructions in [Appendix of Project Report](docs/project_report.md#appendix-reverse-engineering-physical-eer-diagram-in-mysql-workbench).
- **16 Demonstration SQL Queries:** Located in [`docs/sql_queries.sql`](docs/sql_queries.sql).
