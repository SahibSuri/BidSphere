import streamlit as st
from frontend.api_client import api_client, API_BASE_URL
from frontend.components.cards import render_kpi_card


def render_system_status_page():
    st.markdown("## 🖥️ Database & API Infrastructure Status")
    st.caption("Live health monitoring, architecture verification, and service connectivity diagnostics.")

    # Execute health check over HTTP
    health_data = api_client.check_health()
    db_info = health_data.get("database", {})

    api_healthy = health_data.get("status") == "healthy"
    db_healthy = db_info.get("connected", False)

    col1, col2, col3 = st.columns(3)
    with col1:
        status_text = "🟢 ONLINE" if api_healthy else "🔴 OFFLINE"
        render_kpi_card("FastAPI Backend", status_text, f"Base URL: {API_BASE_URL}", "#10b981" if api_healthy else "#ef4444")
    with col2:
        db_status_text = "🟢 CONNECTED" if db_healthy else "🔴 DISCONNECTED"
        render_kpi_card("MySQL 8.0+ Database", db_status_text, f"Version: {db_info.get('version', 'N/A')}", "#10b981" if db_healthy else "#ef4444")
    with col3:
        render_kpi_card("Target Database", db_info.get("database", "bidsphere_db"), f"Host: {db_info.get('host', '127.0.0.1')}:{db_info.get('port', 3306)}", "#6366f1")

    st.divider()

    st.markdown("#### 📐 Architecture & Connectivity Specifications")
    with st.container(border=True):
        st.markdown(
            f"""
            - **Tier 1 (Presentation):** Streamlit Web Interface (Communicates strictly via HTTP REST to FastAPI)
            - **Tier 2 (Application/Logic):** FastAPI + Uvicorn ASGI Server (JWT auth, Pydantic validation, role permissions)
            - **Tier 3 (Database):** MySQL 8.0+ Community Server (InnoDB engine, row-level locking `FOR UPDATE`, stored procedures & triggers)
            - **ORM / Driver:** SQLAlchemy 2.0 with PyMySQL
            - **API Documentation:** [Open Swagger Interactive Docs (http://127.0.0.1:8000/docs)](http://127.0.0.1:8000/docs)
            """
        )

    st.markdown("#### 🔍 Raw Health Check Payload")
    st.json(health_data)

    if st.button("🔄 Re-Check System Health"):
        st.rerun()
