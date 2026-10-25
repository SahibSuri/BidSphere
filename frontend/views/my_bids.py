import streamlit as st
import pandas as pd
from frontend.api_client import api_client
from frontend.components.cards import format_inr, render_kpi_card


def render_my_bids_page():
    st.markdown("## 🏷️ My Bidding Activity")
    st.caption("Track all the bids you have placed across auctions, your active positions, and won auctions.")

    if not st.session_state.get("access_token"):
        st.warning("Please sign in to view your bids.")
        if st.button("Sign In →"):
            st.session_state["active_page"] = "Login / Register"
            st.rerun()
        return

    try:
        buyer_data = api_client.get_buyer_dashboard()
        bids = api_client.get_my_bids()
    except Exception as e:
        st.error(f"Failed to fetch your bids from server: {str(e)}")
        return

    # KPI summary metrics
    kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
    with kpi_col1:
        render_kpi_card("Total Bids Placed", str(buyer_data.get("total_bids_placed", 0)), "Lifetime bid events", "#38bdf8")
    with kpi_col2:
        render_kpi_card("Active Positions", str(buyer_data.get("active_auctions_count", 0)), "Currently open auctions", "#10b981")
    with kpi_col3:
        render_kpi_card("Auctions Won", str(buyer_data.get("won_auctions_count", 0)), "Successful acquisitions", "#f59e0b")

    st.divider()

    # Active Bidding Positions
    st.markdown("#### 🎯 Currently Active Bidding Positions")
    active_parts = buyer_data.get("active_participations", [])
    if not active_parts:
        st.info("You do not currently have any active bids on open auctions.")
    else:
        for p in active_parts:
            with st.container(border=True):
                c1, c2, c3, c4 = st.columns([3, 2, 2, 2])
                with c1:
                    st.markdown(f"**{p['title']}**")
                    st.caption(f"Auction #{p['auction_id']}")
                with c2:
                    st.write(f"**Current Price:** {format_inr(p['current_price'])}")
                with c3:
                    st.write(f"**My Highest Bid:** {format_inr(p['my_highest_bid'])}")
                    pos_text = "🟢 Leading" if p["is_winning"] else "🔴 Outbid"
                    st.markdown(f"**Status:** {pos_text}")
                with c4:
                    if st.button("View Auction →", key=f"btn_mybid_{p['auction_id']}", use_container_width=True):
                        st.session_state["selected_auction_id"] = p["auction_id"]
                        st.session_state["active_page"] = "Auction Details"
                        st.rerun()

    # Complete Bid Log
    st.divider()
    st.markdown("#### 📜 Complete Bid Submission History")
    if not bids:
        st.info("No bid history found.")
    else:
        df = pd.DataFrame([
            {
                "Bid ID": b["bid_id"],
                "Auction ID": b["auction_id"],
                "Bid Amount": format_inr(b["bid_amount"]),
                "Status": b["status"],
                "Timestamp": b["bid_time"][:19].replace("T", " "),
            }
            for b in bids
        ])
        st.dataframe(df, use_container_width=True)
