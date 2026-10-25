from datetime import datetime, timedelta
import streamlit as st
import pandas as pd
from frontend.api_client import api_client
from frontend.components.cards import format_inr, render_status_badge, render_kpi_card


def render_seller_dashboard_page():
    st.markdown("## 💼 Seller Workspace & Dashboard")
    st.caption("Create, monitor, and manage your auction listings, inventory, and settlements.")

    user = st.session_state.get("current_user")
    if not user:
        st.warning("Please sign in to access the Seller Workspace.")
        if st.button("Sign In →"):
            st.session_state["active_page"] = "Login / Register"
            st.rerun()
        return

    if user.get("role") not in ["SELLER", "ADMIN"]:
        st.error("This workspace is reserved for Sellers and Administrators. Your current role is BUYER.")
        return

    # Fetch seller metrics
    try:
        data = api_client.get_seller_dashboard()
    except Exception as e:
        st.error(f"Error loading seller data: {str(e)}")
        return

    # KPI Summary Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_kpi_card("Total Listings", str(data.get("total_listings", 0)), "All created items", "#6366f1")
    with col2:
        render_kpi_card("Active Auctions", str(data.get("active_listings", 0)), "Open for bids", "#10b981")
    with col3:
        render_kpi_card("Closed Auctions", str(data.get("closed_listings", 0)), "Finished items", "#94a3b8")
    with col4:
        render_kpi_card("Total Sales Volume", format_inr(data.get("total_sales_volume", 0)), "Gross settled value", "#38bdf8")

    st.divider()

    tab_listings, tab_create, tab_bids = st.tabs(["📦 My Listings", "➕ Create New Listing", "🔨 Bids Received"])

    # Tab 1: My Listings
    with tab_listings:
        listings = data.get("listings", [])
        if not listings:
            st.info("You haven't published any listings yet. Use the 'Create New Listing' tab to list your first item!")
        else:
            for auc in listings:
                with st.container(border=True):
                    c1, c2, c3, c4 = st.columns([1.5, 3.5, 2, 2.5])
                    with c1:
                        img = auc.get("image_url") or "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=400&q=80"
                        st.image(img, use_column_width=True)
                    with c2:
                        st.markdown(f"**{auc['title']}**")
                        st.caption(f"Category: {auc.get('category_name')} • Starts: {auc['start_time'][:10]} • Ends: {auc['end_time'][:10]}")
                        st.markdown(render_status_badge(auc.get("status")), unsafe_allow_html=True)
                    with c3:
                        st.markdown(
                            f"""
                            <div style="font-size: 0.75rem; color: #94a3b8;">CURRENT BID</div>
                            <div style="font-size: 1.25rem; font-weight: 800; color: #38bdf8;">{format_inr(auc['current_price'])}</div>
                            <div style="font-size: 0.75rem; color: #64748b;">Start: {format_inr(auc['starting_price'])}</div>
                            """,
                            unsafe_allow_html=True,
                        )
                    with c4:
                        if st.button("View Details →", key=f"sel_view_{auc['auction_id']}", use_container_width=True):
                            st.session_state["selected_auction_id"] = auc["auction_id"]
                            st.session_state["active_page"] = "Auction Details"
                            st.rerun()

                        if auc["status"] in ["ACTIVE", "SCHEDULED"]:
                            if st.button("⏹️ Settle / Close", key=f"sel_close_{auc['auction_id']}", use_container_width=True):
                                try:
                                    res = api_client.close_auction(auc["auction_id"])
                                    st.success(res.get("status_message"))
                                    st.rerun()
                                except Exception as e:
                                    st.error(str(e))

    # Tab 2: Create Listing
    with tab_create:
        st.markdown("##### 📝 Create an Auction Listing")
        try:
            categories = api_client.get_categories()
            cat_map = {c["name"]: c["category_id"] for c in categories}
        except Exception:
            cat_map = {}

        with st.form("create_auction_form"):
            form_col1, form_col2 = st.columns(2)
            with form_col1:
                title = st.text_input("Product Title*", placeholder="E.g., Vintage Rolex Submariner (1982)")
                cat_name = st.selectbox("Category*", list(cat_map.keys()) if cat_map else ["General"])
                starting_price = st.number_input("Starting Price (INR)*", min_value=1.0, value=1000.0, step=100.0)
                bid_increment = st.number_input("Minimum Bid Increment (INR)*", min_value=1.0, value=50.0, step=10.0)
            with form_col2:
                image_url = st.text_input("Product Image URL", placeholder="https://images.unsplash.com/...")
                start_date = st.date_input("Start Date", value=datetime.now().date())
                start_time = st.time_input("Start Time", value=datetime.now().time())
                end_date = st.date_input("End Date", value=(datetime.now() + timedelta(days=5)).date())
                end_time = st.time_input("End Time", value=datetime.now().time())

            description = st.text_area("Detailed Product Description*", placeholder="Provide accurate provenance, condition, specifications, and warranty info...")
            publish_btn = st.form_submit_button("Publish Auction Listing →", type="primary", use_container_width=True)

            if publish_btn:
                if not title or not description:
                    st.error("Please provide both product title and detailed description.")
                else:
                    start_dt = datetime.combine(start_date, start_time)
                    end_dt = datetime.combine(end_date, end_time)
                    if end_dt <= start_dt:
                        st.error("Auction End Time must be strictly after Start Time.")
                    else:
                        payload = {
                            "category_id": cat_map.get(cat_name, 1),
                            "title": title,
                            "description": description,
                            "starting_price": starting_price,
                            "bid_increment": bid_increment,
                            "start_time": start_dt.isoformat(),
                            "end_time": end_dt.isoformat(),
                            "image_url": image_url or None,
                        }
                        try:
                            new_auc = api_client.create_auction(payload)
                            st.balloons()
                            st.success(f"Auction #{new_auc['auction_id']} '{title}' published successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to create auction: {str(e)}")

    # Tab 3: Bids Received
    with tab_bids:
        recent_bids = data.get("recent_bids", [])
        if not recent_bids:
            st.info("No bids recorded yet on your listings.")
        else:
            df_bids = pd.DataFrame([
                {
                    "Auction Title": b["auction_title"],
                    "Bidder": b["bidder_username"],
                    "Bid Amount": format_inr(b["bid_amount"]),
                    "Status": b["status"],
                    "Timestamp": b["bid_time"][:19].replace("T", " "),
                }
                for b in recent_bids
            ])
            st.dataframe(df_bids, use_container_width=True)
