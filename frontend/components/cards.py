import streamlit as st
from decimal import Decimal


def format_inr(amount) -> str:
    """Formats numeric value to Indian Rupee (₹) convention."""
    if amount is None:
        return "₹0.00"
    try:
        val = float(amount)
        # Handle zero or negative
        is_neg = val < 0
        val = abs(val)
        parts = f"{val:.2f}".split(".")
        integer_part = parts[0]
        decimal_part = parts[1]

        if len(integer_part) > 3:
            last_three = integer_part[-3:]
            remaining = integer_part[:-3]
            # Group in pairs from right to left
            chunks = []
            while len(remaining) > 2:
                chunks.append(remaining[-2:])
                remaining = remaining[:-2]
            if remaining:
                chunks.append(remaining)
            chunks.reverse()
            formatted_int = ",".join(chunks) + "," + last_three
        else:
            formatted_int = integer_part

        formatted = f"₹{formatted_int}.{decimal_part}"
        return f"-{formatted}" if is_neg else formatted
    except Exception:
        return f"₹{amount}"


def render_status_badge(status: str) -> str:
    """Returns HTML for an auction status pill."""
    status_upper = (status or "").upper()
    css_class = {
        "ACTIVE": "badge-active",
        "SCHEDULED": "badge-scheduled",
        "CLOSED": "badge-closed",
        "UNSOLD": "badge-unsold",
        "CANCELLED": "badge-cancelled",
    }.get(status_upper, "badge-closed")

    icon = {
        "ACTIVE": "🟢",
        "SCHEDULED": "🔵",
        "CLOSED": "⚪",
        "UNSOLD": "🟠",
        "CANCELLED": "🔴",
    }.get(status_upper, "⚪")

    return f'<span class="badge {css_class}">{icon} {status_upper}</span>'


def render_role_badge(role: str) -> str:
    """Returns HTML for user role badge."""
    role_upper = (role or "").upper()
    css_class = {
        "ADMIN": "role-admin",
        "SELLER": "role-seller",
        "BUYER": "role-buyer",
    }.get(role_upper, "role-buyer")
    return f'<span class="role-badge {css_class}">{role_upper}</span>'


def render_kpi_card(title: str, value: str, subtext: str = None, color: str = "#6366f1"):
    """Renders a styled KPI metric block."""
    sub_html = f'<div style="font-size: 0.75rem; color: #64748b; margin-top: 4px;">{subtext}</div>' if subtext else ""
    st.markdown(
        f"""
        <div class="kpi-card" style="border-left-color: {color};">
            <div class="kpi-title">{title}</div>
            <div class="kpi-value">{value}</div>
            {sub_html}
        </div>
        """,
        unsafe_allow_html=True,
    )
