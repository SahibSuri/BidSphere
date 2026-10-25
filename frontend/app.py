import os
import sys

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath("."))

import streamlit as st

# Configure Streamlit page settings
st.set_page_config(
    page_title="BidSphere | Online Auction Management System",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

from frontend.components.styles import apply_custom_styles
from frontend.components.navbar import render_sidebar
from frontend.api_client import api_client

# Import Page Views
from frontend.views.marketplace import render_marketplace_page
from frontend.views.auth_page import render_auth_page
from frontend.views.auction_detail import render_auction_detail_page
from frontend.views.my_bids import render_my_bids_page
from frontend.views.watchlist_page import render_watchlist_page
from frontend.views.seller_dashboard import render_seller_dashboard_page
from frontend.views.auction_results import render_auction_results_page
from frontend.views.notifications_page import render_notifications_page
from frontend.views.payments_page import render_payments_page
from frontend.views.admin_dashboard import render_admin_dashboard_page
from frontend.views.system_status import render_system_status_page


def main():
    apply_custom_styles()
    render_sidebar()

    active_page = st.session_state.get("active_page", "Marketplace")

    # Dispatch to active page
    if active_page == "Marketplace":
        render_marketplace_page()
    elif active_page == "Login / Register":
        render_auth_page()
    elif active_page == "Auction Details":
        render_auction_detail_page()
    elif active_page == "My Bids":
        render_my_bids_page()
    elif active_page == "My Watchlist":
        render_watchlist_page()
    elif active_page == "Seller Dashboard":
        render_seller_dashboard_page()
    elif active_page == "Auction Results":
        render_auction_results_page()
    elif active_page == "Notifications":
        render_notifications_page()
    elif active_page == "Simulated Payments":
        render_payments_page()
    elif active_page == "Admin Dashboard":
        render_admin_dashboard_page()
    elif active_page == "Database/API Status":
        render_system_status_page()
    else:
        render_marketplace_page()


if __name__ == "__main__":
    main()
