import streamlit as st
import pandas as pd
from frontend.api_client import api_client
from frontend.components.cards import format_inr, render_status_badge


def render_auction_results_page():
    st.markdown("## 🏆 Final Auction Results & Settlements")
    st.caption("Official archive of finalized auctions, winning bids, and settlement records.")

    try:
        results = api_client.get_auction_results()
    except Exception as e:
        st.error(f"Error fetching auction results: {str(e)}")
        return

    if not results:
        st.info("No closed auction results available yet.")
        return

    # Filter by result status
    filter_status = st.selectbox("Filter Result Status", ["ALL", "WON", "UNSOLD", "CANCELLED"], index=0)
    if filter_status != "ALL":
        results = [r for r in results if r["result_status"] == filter_status]

    st.markdown(f"**Found {len(results)} settlement records**")

    current_user = st.session_state.get("current_user")
    current_uid = current_user.get("user_id") if current_user else None

    for r in results:
        with st.container(border=True):
            c1, c2, c3, c4 = st.columns([3.5, 2, 2, 2.5])
            with c1:
                st.markdown(f"**{r.get('auction_title', f'Auction #{r['auction_id']}')}**")
                st.caption(f"Result #{r['result_id']} • Closed: {r['closed_at'][:19].replace('T', ' ')}")
            with c2:
                status_color = "#10b981" if r["result_status"] == "WON" else "#f59e0b"
                st.markdown(
                    f'<span style="background:{status_color}22; color:{status_color}; padding:4px 10px; border-radius:9999px; font-weight:700; font-size:0.8rem;">{r["result_status"]}</span>',
                    unsafe_allow_html=True,
                )
                if r["result_status"] == "WON":
                    st.caption(f"Winner: **{r.get('winner_username')}**")
            with c3:
                st.markdown(
                    f"""
                    <div style="font-size: 0.75rem; color: #94a3b8;">FINAL PRICE</div>
                    <div style="font-size: 1.25rem; font-weight: 800; color: #38bdf8;">{format_inr(r['final_price'])}</div>
                    """,
                    unsafe_allow_html=True,
                )
            with c4:
                pay_status = r.get("payment_status", "NOT_INITIATED")
                pay_color = "#10b981" if pay_status == "SUCCESS" else "#f59e0b"
                st.markdown(
                    f'<div style="font-size: 0.8rem; font-weight: 600; color: {pay_color};">Payment: {pay_status}</div>',
                    unsafe_allow_html=True,
                )

                # If current user is the winner and payment not success, show button to proceed to payment
                if r["result_status"] == "WON" and r.get("winner_id") == current_uid and pay_status != "SUCCESS":
                    if st.button("💳 Pay Now →", key=f"pay_res_{r['result_id']}", type="primary", use_container_width=True):
                        st.session_state["payment_target_result_id"] = r["result_id"]
                        st.session_state["payment_target_price"] = r["final_price"]
                        st.session_state["payment_target_title"] = r.get("auction_title")
                        st.session_state["active_page"] = "Simulated Payments"
                        st.rerun()
                else:
                    if st.button("View Auction →", key=f"res_auc_{r['result_id']}", use_container_width=True):
                        st.session_state["selected_auction_id"] = r["auction_id"]
                        st.session_state["active_page"] = "Auction Details"
                        st.rerun()
