import streamlit as st
from frontend.api_client import api_client
from frontend.components.cards import format_inr, render_status_badge


def render_marketplace_page():
    st.markdown('<h1 style="margin-bottom: 4px;">🏛️ BidSphere Marketplace</h1>', unsafe_allow_html=True)
    st.caption("Discover, monitor, and bid on authentic verified auctions across categories.")

    # Search & Filter Controls
    with st.container():
        col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
        with col1:
            search_query = st.text_input("🔍 Search Listings", placeholder="E.g., MacBook, Painting, Rolex, Leica...")
        with col2:
            try:
                categories = api_client.get_categories()
                cat_options = {"All Categories": None}
                for c in categories:
                    cat_options[c["name"]] = c["category_id"]
                selected_cat_name = st.selectbox("Category", list(cat_options.keys()))
                selected_cat_id = cat_options[selected_cat_name]
            except Exception:
                selected_cat_id = None
                st.selectbox("Category", ["All Categories"])
        with col3:
            status_filter = st.selectbox(
                "Auction Status",
                ["ACTIVE", "SCHEDULED", "CLOSED", "ALL", "UNSOLD", "CANCELLED"],
                index=0,
            )
        with col4:
            sort_by = st.selectbox(
                "Sort By",
                ["closing_soon", "price_low_high", "price_high_low", "newest"],
                format_func=lambda x: {
                    "closing_soon": "⏳ Closing Soon",
                    "price_low_high": "🔼 Price: Low to High",
                    "price_high_low": "🔽 Price: High to Low",
                    "newest": "✨ Newly Listed",
                }.get(x, x),
            )

    # Fetch auctions via API
    try:
        auctions = api_client.get_auctions(
            status=status_filter if status_filter != "ALL" else None,
            category_id=selected_cat_id,
            search=search_query if search_query else None,
            sort_by=sort_by,
        )
    except Exception as e:
        st.error(f"Failed to load auctions from backend: {str(e)}")
        auctions = []

    st.markdown(f"**Found {len(auctions)} auctions** matching criteria")

    if not auctions:
        st.info("No auctions found matching your criteria. Try adjusting the search or filters.")
        return

    # Render auction cards in 3 responsive columns
    cols = st.columns(3)
    for idx, auc in enumerate(auctions):
        col = cols[idx % 3]
        with col:
            with st.container(border=True):
                # Image
                img_url = auc.get("image_url") or "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=600&q=80"
                st.markdown(
                    f"""
                    <div style="height: 180px; overflow: hidden; border-radius: 8px; margin-bottom: 12px;">
                        <img src="{img_url}" style="width: 100%; height: 100%; object-fit: cover;" onerror="this.src='https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=600&q=80'"/>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # Status and Category
                st.markdown(
                    f"""
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <span style="font-size: 0.8rem; color: #94a3b8; font-weight: 600;">{auc.get('category_name', 'Category')}</span>
                        {render_status_badge(auc.get('status', ''))}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # Title
                st.markdown(f"**{auc['title'][:48]}**{'...' if len(auc['title']) > 48 else ''}")

                # Price and Bids
                st.markdown(
                    f"""
                    <div style="margin-top: 8px; margin-bottom: 12px;">
                        <div style="font-size: 0.75rem; color: #64748b;">CURRENT HIGHEST BID</div>
                        <div style="font-size: 1.35rem; font-weight: 800; color: #38bdf8;">{format_inr(auc['current_price'])}</div>
                        <div style="font-size: 0.75rem; color: #94a3b8; margin-top: 2px;">
                            <span>🏷️ Starting: {format_inr(auc['starting_price'])}</span> • 
                            <span>🔨 {auc.get('total_bids', 0)} bids</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # Actions
                btn_col1, btn_col2 = st.columns([3, 1])
                with btn_col1:
                    if st.button("View & Bid →", key=f"btn_view_{auc['auction_id']}", use_container_width=True):
                        st.session_state["selected_auction_id"] = auc["auction_id"]
                        st.session_state["active_page"] = "Auction Details"
                        st.rerun()

                with btn_col2:
                    is_watched = auc.get("is_in_watchlist", False)
                    watch_icon = "⭐" if is_watched else "☆"
                    if st.button(watch_icon, key=f"btn_watch_{auc['auction_id']}", help="Toggle Watchlist"):
                        if not st.session_state.get("access_token"):
                            st.warning("Please login to save to watchlist.")
                        else:
                            try:
                                if is_watched:
                                    api_client.remove_from_watchlist(auc["auction_id"])
                                    st.toast("Removed from Watchlist")
                                else:
                                    api_client.add_to_watchlist(auc["auction_id"])
                                    st.toast("Added to Watchlist!")
                                st.rerun()
                            except Exception as e:
                                st.error(str(e))
