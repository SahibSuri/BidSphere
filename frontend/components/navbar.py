import streamlit as st
from frontend.api_client import api_client
from frontend.components.cards import render_role_badge


def render_sidebar():
    """Renders the BidSphere application sidebar navigation with active highlights."""
    with st.sidebar:
        # Brand Header
        st.markdown(
            """
            <div style="margin-bottom: 20px;">
                <div style="font-size: 1.8rem; font-weight: 800; color: #f8fafc; font-family: 'Outfit', sans-serif;">
                    🏛️ Bid<span style="color: #6366f1;">Sphere</span>
                </div>
                <div style="font-size: 0.75rem; color: #94a3b8; font-weight: 500;">
                    Online Auction Management System
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        current_user = st.session_state.get("current_user")
        unread_count = 0

        # User Profile Status Widget
        if current_user:
            role_html = render_role_badge(current_user.get("role"))
            unread_count = api_client.get_unread_count()
            st.markdown(
                f"""
                <div style="background: rgba(30, 41, 59, 0.6); padding: 12px; border-radius: 10px; margin-bottom: 16px; border: 1px solid rgba(255,255,255,0.08);">
                    <div style="font-weight: 700; color: #f8fafc; font-size: 0.95rem;">👤 {current_user.get('full_name')}</div>
                    <div style="font-size: 0.8rem; color: #94a3b8;">@{current_user.get('username')} • {role_html}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                """
                <div style="background: rgba(30, 41, 59, 0.4); padding: 10px; border-radius: 8px; margin-bottom: 16px; font-size: 0.82rem; color: #94a3b8;">
                    Guest Mode • Sign in to place bids or create listings
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Initialize active_page in session state
        if "active_page" not in st.session_state:
            st.session_state["active_page"] = "Marketplace"

        current_page = st.session_state["active_page"]

        # Navigation Items Definition
        notif_label = f"🔔 Notifications ({unread_count})" if unread_count > 0 else "🔔 Notifications"

        nav_items = [
            ("🏛️ Marketplace", "Marketplace"),
            ("🔍 Auction Details", "Auction Details"),
            ("⭐ My Watchlist", "My Watchlist"),
            ("🏷️ My Bids", "My Bids"),
            ("💼 Seller Dashboard", "Seller Dashboard"),
            ("🏆 Auction Results", "Auction Results"),
            (notif_label, "Notifications"),
            ("💳 Simulated Payments", "Simulated Payments"),
        ]

        if current_user and current_user.get("role") == "ADMIN":
            nav_items.append(("🛡️ Admin Dashboard", "Admin Dashboard"))

        nav_items.append(("🖥️ Database/API Status", "Database/API Status"))

        if not current_user:
            nav_items.append(("🔑 Sign In / Register", "Login / Register"))
        else:
            nav_items.append(("👤 My Profile", "Login / Register"))

        st.markdown("<p style='font-size: 0.75rem; text-transform: uppercase; color: #64748b; font-weight: 700; margin-bottom: 8px;'>Navigation</p>", unsafe_allow_html=True)

        # Render styled navigation buttons
        for label, page_key in nav_items:
            is_active = (current_page == page_key)
            button_type = "primary" if is_active else "secondary"
            if st.button(label, key=f"nav_btn_{page_key}_{label}", type=button_type, use_container_width=True):
                st.session_state["active_page"] = page_key
                st.rerun()

        st.divider()

        # Logout Button for Authenticated Users
        if current_user:
            if st.button("🚪 Logout of Account", use_container_width=True):
                st.session_state.pop("access_token", None)
                st.session_state.pop("current_user", None)
                st.session_state["active_page"] = "Marketplace"
                st.toast("Signed out successfully.")
                st.rerun()

        st.caption("B.Tech CSE DBMS Project • MySQL 8.0+")
