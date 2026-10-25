import streamlit as st
from frontend.api_client import api_client


def render_notifications_page():
    st.markdown("## 🔔 User Alerts & Notifications")
    st.caption("Live notifications about your bids, outbid events, closures, and payment receipts.")

    if not st.session_state.get("access_token"):
        st.warning("Please sign in to view your notifications.")
        if st.button("Sign In →"):
            st.session_state["active_page"] = "Login / Register"
            st.rerun()
        return

    top_col1, top_col2 = st.columns([4, 2])
    with top_col2:
        if st.button("✓ Mark All as Read", use_container_width=True):
            try:
                api_client.mark_all_notifications_read()
                st.toast("All notifications marked as read.")
                st.rerun()
            except Exception as e:
                st.error(str(e))

    try:
        notifications = api_client.get_notifications()
    except Exception as e:
        st.error(f"Error fetching notifications: {str(e)}")
        return

    if not notifications:
        st.info("You have no notifications yet.")
        return

    type_icons = {
        "BID_PLACED": ("🔨", "#3b82f6"),
        "OUTBID": ("⚠️", "#ef4444"),
        "AUCTION_WON": ("🏆", "#10b981"),
        "AUCTION_CLOSED": ("🏁", "#6b7280"),
        "AUCTION_UNSOLD": ("🟠", "#f59e0b"),
        "PAYMENT_RECEIVED": ("💰", "#8b5cf6"),
    }

    for n in notifications:
        icon, color = type_icons.get(n["notification_type"], ("ℹ️", "#3b82f6"))
        unread_bg = "rgba(99, 102, 241, 0.08)" if not n["is_read"] else "transparent"
        border_col = color if not n["is_read"] else "rgba(255, 255, 255, 0.1)"

        with st.container(border=True):
            col_icon, col_text, col_action = st.columns([0.8, 5.2, 1.5])
            with col_icon:
                st.markdown(f'<div style="font-size: 1.8rem; text-align: center;">{icon}</div>', unsafe_allow_html=True)
            with col_text:
                st.markdown(f"**{n['title']}**")
                st.write(n["message"])
                st.caption(f"{n['notification_type']} • {n['created_at'][:19].replace('T', ' ')}")
            with col_action:
                if not n["is_read"]:
                    if st.button("Mark Read", key=f"read_{n['notification_id']}", use_container_width=True):
                        try:
                            api_client.mark_notification_read(n["notification_id"])
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))
                else:
                    st.caption("✓ Read")
