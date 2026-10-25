import streamlit as st
from frontend.api_client import api_client
from frontend.components.cards import render_role_badge


def render_auth_page():
    st.markdown("## 🔐 Account Authentication")
    st.caption("Sign in to your BidSphere account or register as a new Buyer or Seller.")

    # If already logged in, show profile card and logout
    if st.session_state.get("access_token") and st.session_state.get("current_user"):
        user = st.session_state["current_user"]
        with st.container(border=True):
            st.success(f"You are currently logged in as **{user.get('username')}**")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Full Name:** {user.get('full_name')}")
                st.write(f"**Email:** {user.get('email')}")
            with col2:
                role_html = render_role_badge(user.get("role"))
                st.markdown(f"**Role:** {role_html}", unsafe_allow_html=True)
                st.write(f"**Phone:** {user.get('phone') or 'Not provided'}")

            if st.button("🚪 Logout of Account", type="primary"):
                st.session_state.pop("access_token", None)
                st.session_state.pop("current_user", None)
                st.toast("Logged out successfully.")
                st.rerun()
        return

    # Demo Quick-Login Banner
    st.info(
        "💡 **Academic Demo Accounts Ready:** Click any demo button below for instant testing!"
    )
    demo_cols = st.columns(3)
    with demo_cols[0]:
        if st.button("👑 Quick Login as Admin", use_container_width=True):
            _execute_login("admin", "Admin@BidSphere2026!")
    with demo_cols[1]:
        if st.button("💼 Quick Login as Seller (aravind)", use_container_width=True):
            _execute_login("aravind_tech", "Pass@1234")
    with demo_cols[2]:
        if st.button("🛒 Quick Login as Buyer (vikram)", use_container_width=True):
            _execute_login("vikram_b", "Pass@1234")

    st.divider()

    tab_login, tab_register = st.tabs(["🔑 Sign In", "📝 Create New Account"])

    # Login Tab
    with tab_login:
        with st.form("login_form"):
            username_or_email = st.text_input("Username or Email Address")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Sign In →", type="primary", use_container_width=True)

            if submitted:
                if not username_or_email or not password:
                    st.error("Please enter both username/email and password.")
                else:
                    _execute_login(username_or_email, password)

    # Register Tab
    with tab_register:
        with st.form("register_form"):
            r_col1, r_col2 = st.columns(2)
            with r_col1:
                new_username = st.text_input("Username (letters, numbers, underscore)")
                new_email = st.text_input("Email Address")
                new_fullname = st.text_input("Full Legal Name")
            with r_col2:
                new_password = st.text_input("Password (min 6 characters)", type="password")
                new_role = st.selectbox("I want to register as a:", ["BUYER", "SELLER"])
                new_phone = st.text_input("Phone Number (+91-...)")

            new_address = st.text_area("Billing/Delivery Address")
            reg_submitted = st.form_submit_button("Register Account →", type="primary", use_container_width=True)

            if reg_submitted:
                if not new_username or not new_email or not new_password or not new_fullname:
                    st.error("Please fill in all mandatory fields (Username, Email, Full Name, Password).")
                else:
                    try:
                        api_client.register({
                            "username": new_username,
                            "email": new_email,
                            "password": new_password,
                            "full_name": new_fullname,
                            "role": new_role,
                            "phone": new_phone or None,
                            "address": new_address or None,
                        })
                        st.success("Account created successfully! Logging you in...")
                        _execute_login(new_username, new_password)
                    except Exception as e:
                        st.error(f"Registration failed: {str(e)}")


def _execute_login(username_or_email, password):
    try:
        data = api_client.login(username_or_email, password)
        st.session_state["access_token"] = data["access_token"]
        st.session_state["current_user"] = {
            "user_id": data["user_id"],
            "username": data["username"],
            "email": data["email"],
            "full_name": data["full_name"],
            "role": data["role"],
        }
        st.toast(f"Welcome back, {data['username']}! Signed in as {data['role']}.")
        st.session_state["active_page"] = "Marketplace"
        st.rerun()
    except Exception as e:
        st.error(f"Login failed: {str(e)}")
