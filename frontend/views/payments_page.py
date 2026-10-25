import streamlit as st
import pandas as pd
from frontend.api_client import api_client
from frontend.components.cards import format_inr


def render_payments_page():
    st.markdown("## 💳 Simulated Payments & Receipts")
    st.caption("Securely complete simulated settlement transactions for your won auction listings.")

    if not st.session_state.get("access_token"):
        st.warning("Please sign in to access payments.")
        if st.button("Sign In →"):
            st.session_state["active_page"] = "Login / Register"
            st.rerun()
        return

    # Academic Disclaimer
    st.info(
        "🛡️ **Academic Simulation Notice:** This project implements simulated payment workflows only. "
        "No real financial transactions take place, and no payment card or banking credentials are ever collected."
    )

    tab_pay, tab_history = st.tabs(["💳 Execute Payment", "🧾 Payment Receipts & History"])

    with tab_pay:
        # Check for pre-selected result from results page or query buyer dashboard
        try:
            buyer_data = api_client.get_buyer_dashboard()
            won_auctions = buyer_data.get("won_auctions", [])
            pending_won = [w for w in won_auctions if w.get("payment_status") != "SUCCESS"]
        except Exception as e:
            st.error(f"Error fetching pending payments: {str(e)}")
            pending_won = []

        if not pending_won:
            st.success("🎉 You have no pending payments! All won auctions are settled.")
        else:
            options_map = {
                f"{w['auction_title']} - {format_inr(w['final_price'])} (Result #{w['result_id']})": w
                for w in pending_won
            }

            pre_result_id = st.session_state.get("payment_target_result_id")
            default_idx = 0
            if pre_result_id:
                for idx, (label, item) in enumerate(options_map.items()):
                    if item["result_id"] == pre_result_id:
                        default_idx = idx
                        break

            with st.form("payment_submission_form"):
                selected_label = st.selectbox("Select Won Auction to Settle", list(options_map.keys()), index=default_idx)
                selected_item = options_map[selected_label]

                st.write(f"**Item:** {selected_item['auction_title']}")
                st.write(f"**Settlement Amount:** {format_inr(selected_item['final_price'])}")

                payment_method = st.radio(
                    "Simulated Payment Method",
                    ["SIMULATED_UPI", "SIMULATED_NETBANKING", "SIMULATED_CARD"],
                    format_func=lambda x: {
                        "SIMULATED_UPI": "⚡ Simulated UPI (Google Pay / PhonePe / BHIM)",
                        "SIMULATED_NETBANKING": "🏦 Simulated Net Banking (NEFT / IMPS)",
                        "SIMULATED_CARD": "💳 Simulated Credit / Debit Card",
                    }.get(x, x),
                )

                pay_submit = st.form_submit_button("Confirm Simulated Payment →", type="primary", use_container_width=True)

                if pay_submit:
                    try:
                        res = api_client.submit_payment(
                            result_id=selected_item["result_id"],
                            payment_method=payment_method,
                        )
                        st.balloons()
                        st.success(f"Payment Verified! Transaction Reference: **{res['transaction_reference']}**")
                        st.session_state.pop("payment_target_result_id", None)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Payment failed: {str(e)}")

    with tab_history:
        try:
            my_payments = api_client.get_my_payments()
            if not my_payments:
                st.info("No payment transactions recorded yet.")
            else:
                df = pd.DataFrame([
                    {
                        "Receipt ID": p["payment_id"],
                        "Auction Title": p["auction_title"],
                        "Amount Paid": format_inr(p["amount"]),
                        "Method": p["payment_method"],
                        "Status": p["status"],
                        "Transaction Reference": p["transaction_reference"],
                        "Timestamp": p["paid_at"][:19].replace("T", " ") if p.get("paid_at") else p["created_at"][:19].replace("T", " "),
                    }
                    for p in my_payments
                ])
                st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.error(f"Error loading receipts: {str(e)}")
