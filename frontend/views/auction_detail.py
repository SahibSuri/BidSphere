from datetime import datetime
import streamlit as st
from frontend.api_client import api_client
from frontend.components.cards import format_inr, render_status_badge, render_role_badge


def render_auction_detail_page():
    auction_id = st.session_state.get("selected_auction_id")
    if not auction_id:
        st.warning("No auction selected. Please choose an auction from the Marketplace.")
        if st.button("← Return to Marketplace"):
            st.session_state["active_page"] = "Marketplace"
            st.rerun()
        return

    # Fetch fresh auction details
    try:
        auction = api_client.get_auction(auction_id)
    except Exception as e:
        st.error(f"Error fetching auction details: {str(e)}")
        if st.button("← Back to Marketplace"):
            st.session_state["active_page"] = "Marketplace"
            st.rerun()
        return

    # Back button & Title header
    top_col1, top_col2 = st.columns([1, 5])
    with top_col1:
        if st.button("← Back"):
            st.session_state["active_page"] = "Marketplace"
            st.rerun()
    with top_col2:
        st.markdown(f"### {auction['title']}")

    # Main content layout
    left_col, right_col = st.columns([1.1, 1.2])

    with left_col:
        # Image
        img_url = auction.get("image_url") or "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=800&q=80"
        st.image(img_url, use_column_width=True)

        # Auction Details Meta
        with st.container(border=True):
            st.markdown("##### 📋 Listing Specification")
            st.write(f"**Category:** {auction.get('category_name')}")
            st.write(f"**Seller:** {auction.get('seller_full_name')} (`{auction.get('seller_username')}`)")
            st.write(f"**Starting Price:** {format_inr(auction['starting_price'])}")
            st.write(f"**Bid Increment:** {format_inr(auction['bid_increment'])}")
            st.write(f"**Start Time:** {auction['start_time'][:19].replace('T', ' ')}")
            st.write(f"**End Time:** {auction['end_time'][:19].replace('T', ' ')}")

        # Watchlist button
        is_watched = auction.get("is_in_watchlist", False)
        watch_btn_label = "⭐ Remove from Watchlist" if is_watched else "☆ Add to Watchlist"
        if st.button(watch_btn_label, use_container_width=True):
            if not st.session_state.get("access_token"):
                st.warning("Please sign in to save items to your watchlist.")
            else:
                try:
                    if is_watched:
                        api_client.remove_from_watchlist(auction_id)
                        st.toast("Removed from Watchlist")
                    else:
                        api_client.add_to_watchlist(auction_id)
                        st.toast("Saved to Watchlist!")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

    with right_col:
        # Status & Bidding summary
        status_html = render_status_badge(auction["status"])
        st.markdown(
            f"""
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <span style="font-size: 0.9rem; color: #94a3b8; font-weight: 600;">AUCTION STATUS</span>
                {status_html}
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Price Display Card
        with st.container(border=True):
            st.markdown(
                f"""
                <div style="font-size: 0.85rem; color: #94a3b8; font-weight: 600;">CURRENT HIGHEST BID</div>
                <div style="font-size: 2.2rem; font-weight: 800; color: #38bdf8; font-family: 'Outfit', sans-serif;">
                    {format_inr(auction['current_price'])}
                </div>
                """,
                unsafe_allow_html=True,
            )

            if auction.get("highest_bidder_username"):
                st.caption(f"🏆 Leading Bidder: **{auction['highest_bidder_username']}**")
            else:
                st.caption("No bids have been accepted yet. First bid will establish current price.")

            min_bid = float(auction.get("min_next_bid", auction["starting_price"]))
            st.markdown(f"**Minimum Next Bid Required:** `{format_inr(min_bid)}`")

            # Active Bidding Form
            if auction["status"] == "ACTIVE":
                st.divider()
                st.markdown("##### 🔨 Place Your Bid")

                # Quick increment buttons
                q_cols = st.columns(4)
                if "custom_bid_amount" not in st.session_state or st.session_state["custom_bid_amount"] < min_bid:
                    st.session_state["custom_bid_amount"] = min_bid

                with q_cols[0]:
                    if st.button(f"+{format_inr(auction['bid_increment'])}", use_container_width=True):
                        st.session_state["custom_bid_amount"] += float(auction['bid_increment'])
                        st.rerun()
                with q_cols[1]:
                    if st.button("+₹1,000", use_container_width=True):
                        st.session_state["custom_bid_amount"] += 1000.0
                        st.rerun()
                with q_cols[2]:
                    if st.button("+₹5,000", use_container_width=True):
                        st.session_state["custom_bid_amount"] += 5000.0
                        st.rerun()
                with q_cols[3]:
                    if st.button("Reset", use_container_width=True):
                        st.session_state["custom_bid_amount"] = min_bid
                        st.rerun()

                bid_val = st.number_input(
                    "Bid Amount (INR)",
                    min_value=min_bid,
                    value=float(st.session_state.get("custom_bid_amount", min_bid)),
                    step=float(auction["bid_increment"]),
                    format="%.2f",
                )

                if st.button("🚀 Confirm & Submit Bid", type="primary", use_container_width=True):
                    if not st.session_state.get("access_token"):
                        st.warning("Please sign in or register to place bids.")
                    else:
                        try:
                            res = api_client.place_bid(auction_id, bid_val)
                            st.balloons()
                            st.success(f"🎉 {res.get('status_message', 'Bid Accepted!')} New current price: {format_inr(res.get('current_price', bid_val))}")
                            st.session_state["custom_bid_amount"] = float(res.get("current_price", bid_val)) + float(auction["bid_increment"])
                            st.rerun()
                        except Exception as e:
                            st.error(f"Bid submission rejected: {str(e)}")
            else:
                st.info(f"Bidding is closed for this auction (Status: {auction['status']}).")

        # Description
        with st.container(border=True):
            st.markdown("##### 📝 Description")
            st.write(auction["description"])

    # Owner / Admin Management Section
    current_user = st.session_state.get("current_user")
    if current_user and (current_user["user_id"] == auction["seller_id"] or current_user["role"] == "ADMIN"):
        st.divider()
        st.markdown("#### ⚙️ Seller & Administrator Operations")
        act_col1, act_col2 = st.columns(2)
        with act_col1:
            if st.button("⏹️ Trigger Auction Closure (Settle Results)", type="secondary", use_container_width=True):
                try:
                    close_res = api_client.close_auction(auction_id)
                    st.success(f"Settlement finished: {close_res.get('status_message')}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Closure failed: {str(e)}")

        with act_col2:
            if auction["status"] in ["ACTIVE", "SCHEDULED"]:
                if st.button("🚫 Cancel Listing", use_container_width=True):
                    try:
                        api_client.cancel_auction(auction_id)
                        st.warning("Auction listing has been cancelled.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Cancellation rejected: {str(e)}")

    # Bid History Section
    st.divider()
    st.markdown("#### 📜 Live Bid History")
    try:
        bids = api_client.get_auction_bids(auction_id)
        if not bids:
            st.info("No bids recorded yet on this auction.")
        else:
            bid_data = []
            for b in bids:
                bid_data.append({
                    "Bidder": b.get("bidder_username", f"User #{b['bidder_id']}"),
                    "Bid Amount": format_inr(b["bid_amount"]),
                    "Status": b["status"],
                    "Timestamp": b["bid_time"][:19].replace("T", " "),
                })
            st.dataframe(bid_data, use_container_width=True)
    except Exception as e:
        st.error(f"Could not load bid history: {str(e)}")
