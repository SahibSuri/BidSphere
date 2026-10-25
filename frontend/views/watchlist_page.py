import streamlit as st
from frontend.api_client import api_client
from frontend.components.cards import format_inr, render_status_badge


def render_watchlist_page():
    st.markdown("## ⭐ My Watchlist")
    st.caption("Saved auction listings you are monitoring.")

    if not st.session_state.get("access_token"):
        st.warning("Please sign in to view your saved watchlist.")
        if st.button("Sign In →"):
            st.session_state["active_page"] = "Login / Register"
            st.rerun()
        return

    try:
        watchlist_items = api_client.get_my_watchlist()
    except Exception as e:
        st.error(f"Error fetching watchlist: {str(e)}")
        return

    if not watchlist_items:
        st.info("Your watchlist is currently empty. Star items in the Marketplace to monitor them here!")
        if st.button("Explore Marketplace →"):
            st.session_state["active_page"] = "Marketplace"
            st.rerun()
        return

    st.markdown(f"**{len(watchlist_items)} bookmarked auctions**")

    for item in watchlist_items:
        auc = item.get("auction")
        if not auc:
            continue
        with st.container(border=True):
            col_img, col_info, col_price, col_actions = st.columns([1.5, 3.5, 2, 2])
            with col_img:
                img_url = auc.get("image_url") or "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=400&q=80"
                st.image(img_url, use_column_width=True)
            with col_info:
                st.markdown(f"**{auc['title']}**")
                st.caption(f"Category: {auc.get('category_name')} • Seller: {auc.get('seller_username')}")
                st.markdown(render_status_badge(auc.get("status")), unsafe_allow_html=True)
            with col_price:
                st.markdown(
                    f"""
                    <div style="font-size: 0.75rem; color: #94a3b8;">CURRENT PRICE</div>
                    <div style="font-size: 1.25rem; font-weight: 800; color: #38bdf8;">{format_inr(auc['current_price'])}</div>
                    <div style="font-size: 0.75rem; color: #64748b;">{auc.get('total_bids', 0)} bids placed</div>
                    """,
                    unsafe_allow_html=True,
                )
            with col_actions:
                if st.button("View Auction →", key=f"wl_view_{auc['auction_id']}", use_container_width=True):
                    st.session_state["selected_auction_id"] = auc["auction_id"]
                    st.session_state["active_page"] = "Auction Details"
                    st.rerun()

                if st.button("🗑️ Remove", key=f"wl_del_{auc['auction_id']}", use_container_width=True):
                    try:
                        api_client.remove_from_watchlist(auc["auction_id"])
                        st.toast("Removed from watchlist.")
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))
