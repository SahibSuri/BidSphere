import streamlit as st

CUSTOM_CSS = """
<style>
/* Global Modern Font and Styles */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Outfit:wght@400;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

h1, h2, h3, h4, .brand-title {
    font-family: 'Outfit', sans-serif;
    letter-spacing: -0.02em;
}

/* Custom Card Styling */
.bidsphere-card {
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.8) 100%);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 20px;
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3), 0 8px 10px -6px rgba(0, 0, 0, 0.3);
    backdrop-filter: blur(12px);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.bidsphere-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 20px 30px -10px rgba(0, 0, 0, 0.4);
    border-color: rgba(99, 102, 241, 0.4);
}

/* KPI Card */
.kpi-card {
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.9) 100%);
    border-left: 4px solid #6366f1;
    border-radius: 12px;
    padding: 18px 22px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
}

.kpi-title {
    font-size: 0.85rem;
    color: #94a3b8;
    text-transform: uppercase;
    font-weight: 600;
    letter-spacing: 0.05em;
    margin-bottom: 6px;
}

.kpi-value {
    font-size: 1.8rem;
    font-weight: 800;
    color: #f8fafc;
    font-family: 'Outfit', sans-serif;
}

/* Status Badges */
.badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}

.badge-active {
    background-color: rgba(16, 185, 129, 0.15);
    color: #10b981;
    border: 1px solid rgba(16, 185, 129, 0.3);
}

.badge-scheduled {
    background-color: rgba(59, 130, 246, 0.15);
    color: #3b82f6;
    border: 1px solid rgba(59, 130, 246, 0.3);
}

.badge-closed {
    background-color: rgba(148, 163, 184, 0.15);
    color: #94a3b8;
    border: 1px solid rgba(148, 163, 184, 0.3);
}

.badge-unsold {
    background-color: rgba(245, 158, 11, 0.15);
    color: #f59e0b;
    border: 1px solid rgba(245, 158, 11, 0.3);
}

.badge-cancelled {
    background-color: rgba(239, 68, 68, 0.15);
    color: #ef4444;
    border: 1px solid rgba(239, 68, 68, 0.3);
}

/* Role Pills */
.role-badge {
    padding: 2px 10px;
    border-radius: 6px;
    font-size: 0.72rem;
    font-weight: 700;
}
.role-admin { background: #dc2626; color: white; }
.role-seller { background: #d97706; color: white; }
.role-buyer { background: #2563eb; color: white; }

/* Currency Highlighting */
.price-inr {
    font-family: 'Outfit', sans-serif;
    font-weight: 700;
    color: #38bdf8;
}
</style>
"""


def apply_custom_styles():
    """Injects custom CSS design system into Streamlit page."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
