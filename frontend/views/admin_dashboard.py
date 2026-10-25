import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from frontend.api_client import api_client
from frontend.components.cards import format_inr, render_kpi_card, render_role_badge


def render_admin_dashboard_page():
    st.markdown("## 🛡️ Administrator Analytics & Governance")
    st.caption("Real-time DBMS metrics, category distribution, seller performance, and audit trails.")

    user = st.session_state.get("current_user")
    if not user or user.get("role") != "ADMIN":
        st.error("Access Restricted. Administrator credentials are required to view this dashboard.")
        return

    # Fetch live admin data from backend API
    try:
        data = api_client.get_admin_dashboard()
        kpis = data["kpis"]
    except Exception as e:
        st.error(f"Failed to fetch administrative metrics from API: {str(e)}")
        return

    # 1. KPI Metric Cards Row 1
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        render_kpi_card("Total Registered Users", str(kpis["total_users"]), f"{kpis['total_buyers']} Buyers | {kpis['total_sellers']} Sellers", "#6366f1")
    with k2:
        render_kpi_card("Active Auctions", str(kpis["active_auctions"]), f"Total Created: {kpis['total_auctions']}", "#10b981")
    with k3:
        render_kpi_card("Closed Auctions", str(kpis["closed_auctions"]), f"Unsold: {kpis['unsold_auctions']}", "#94a3b8")
    with k4:
        render_kpi_card("Total Accepted Bids", str(kpis["total_bids"]), "Row-locked transactions", "#f59e0b")

    # KPI Metric Cards Row 2 (Financials)
    f1, f2 = st.columns(2)
    with f1:
        render_kpi_card("Gross Sales Volume (Closed Auctions)", format_inr(kpis["total_sales_volume"]), "Cumulative final price of won lots", "#38bdf8")
    with f2:
        render_kpi_card("Settled Payments Collected", format_inr(kpis["successful_payments_amount"]), "Verified simulated settlements", "#a855f7")

    st.divider()

    # 2. Plotly Charts Row: Category Distribution & Payment Statuses
    c_col1, c_col2 = st.columns(2)

    with c_col1:
        st.markdown("##### 📊 Auction Category Distribution")
        cat_dist = data.get("category_distribution", [])
        if cat_dist:
            df_cat = pd.DataFrame(cat_dist)
            fig_cat = px.pie(
                df_cat,
                names="category_name",
                values="auction_count",
                hole=0.45,
                color_discrete_sequence=px.colors.qualitative.Prism,
            )
            fig_cat.update_layout(
                margin=dict(t=20, b=20, l=20, r=20),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                legend=dict(orientation="h", yanchor="bottom", y=-0.2),
            )
            st.plotly_chart(fig_cat, use_container_width=True)
        else:
            st.info("No category data available.")

    with c_col2:
        st.markdown("##### 💳 Settlement Payment Breakdown")
        pay_summary = data.get("payment_summary", [])
        if pay_summary:
            df_pay = pd.DataFrame(pay_summary)
            fig_pay = px.bar(
                df_pay,
                x="status",
                y="total_amount",
                color="status",
                text="count",
                labels={"total_amount": "Total Amount (₹)", "status": "Status"},
                color_discrete_map={"SUCCESS": "#10b981", "PENDING": "#f59e0b", "FAILED": "#ef4444"},
            )
            fig_pay.update_layout(
                margin=dict(t=20, b=20, l=20, r=20),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig_pay, use_container_width=True)
        else:
            st.info("No payment status records available.")

    st.divider()

    # 3. Seller Performance Table & Chart
    st.markdown("##### 🏅 Seller Performance & Volume Analysis")
    seller_perf = data.get("seller_performance", [])
    if seller_perf:
        df_seller = pd.DataFrame(seller_perf)
        df_seller_display = df_seller.copy()
        df_seller_display["Total Volume"] = df_seller_display["total_volume"].apply(format_inr)
        df_seller_display.rename(
            columns={
                "seller_id": "Seller ID",
                "seller_username": "Username",
                "total_listings": "Total Listings",
                "closed_listings": "Closed Listings",
            },
            inplace=True,
        )
        st.dataframe(df_seller_display[["Seller ID", "Username", "Total Listings", "Closed Listings", "Total Volume"]], use_container_width=True)
    else:
        st.info("No seller performance metrics available.")

    st.divider()

    # 4. User Account Management & Moderation
    st.markdown("##### 👥 User Management & Role Moderation")
    try:
        users = api_client.get_all_users()
        user_rows = []
        for u in users:
            user_rows.append({
                "User ID": u["user_id"],
                "Username": u["username"],
                "Email": u["email"],
                "Full Name": u["full_name"],
                "Role": u["role"],
                "Active": "🟢 Yes" if u["is_active"] else "🔴 No",
                "Created At": u["created_at"][:10],
            })
        st.dataframe(pd.DataFrame(user_rows), use_container_width=True)

        # Toggle Active User control
        u_col1, u_col2 = st.columns([3, 1])
        with u_col1:
            u_options = {f"{u['username']} ({u['email']}) - Role: {u['role']}": u["user_id"] for u in users}
            target_user_str = st.selectbox("Select user to toggle activation status", list(u_options.keys()))
            target_uid = u_options[target_user_str]
        with u_col2:
            st.write("")
            st.write("")
            if st.button("Toggle Active / Deactivate", type="secondary", use_container_width=True):
                try:
                    res_user = api_client.toggle_user_active(target_uid)
                    st.toast(f"User {res_user['username']} active status updated to: {res_user['is_active']}")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))
    except Exception as e:
        st.error(f"Error fetching users: {str(e)}")

    st.divider()

    # 5. System Audit Trail (Trigger & Stored Procedure Events)
    st.markdown("##### 🛡️ Database Audit Log Trail")
    audit_logs = data.get("recent_audit_logs", [])
    if audit_logs:
        df_audit = pd.DataFrame([
            {
                "Log ID": l["log_id"],
                "Table": l["table_name"],
                "Operation": l["operation"],
                "Record ID": l["record_id"],
                "Changed By": l["changed_by"],
                "Timestamp": l["action_timestamp"][:19].replace("T", " "),
            }
            for l in audit_logs
        ])
        st.dataframe(df_audit, use_container_width=True)
    else:
        st.info("No audit logs available.")
