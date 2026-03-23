"""
Product Impact Observatory — main Streamlit entry point.

Run with:
    streamlit run app.py
"""

import streamlit as st

# ── Page config must be first Streamlit call ───────────────────────────────────
st.set_page_config(
    page_title="Product Impact Observatory",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "Product Impact Observatory — Danone real-world evidence prototype",
    },
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ---- Global ---- */
#MainMenu  { visibility: hidden; }
footer     { visibility: hidden; }
header     { visibility: hidden; }

.stApp {
    background-color: #F4F6F9;
}

/* ---- Sidebar ---- */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1B4F72 0%, #154360 100%) !important;
    border-right: none !important;
}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] .stRadio,
[data-testid="stSidebar"] .stToggle,
[data-testid="stSidebar"] button {
    color: white !important;
}
[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.2) !important;
}

/* ---- Inputs (keep text dark) ---- */
.stTextInput input,
.stTextArea textarea {
    color: #2D3436 !important;
    background: white !important;
    border-radius: 10px !important;
    border-color: #D5D8DC !important;
}

/* ---- Buttons ---- */
.stButton > button {
    border-radius: 12px !important;
    font-weight: 700 !important;
    padding: 0.65rem 1.5rem !important;
    font-size: 0.97rem !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #1B4F72, #2E86AB) !important;
    border: none !important;
    color: white !important;
}

/* ---- Tabs ---- */
.stTabs [data-baseweb="tab"] {
    font-weight: 600 !important;
    color: #5D6D7E !important;
}
.stTabs [aria-selected="true"] {
    color: #1B4F72 !important;
}

/* ---- Metrics ---- */
[data-testid="metric-container"] {
    background: white;
    border-radius: 12px;
    padding: 1rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
</style>
""", unsafe_allow_html=True)

# ── Imports (after page config) ────────────────────────────────────────────────
from utils.data_manager import init_session_state          # noqa: E402
from components.onboarding import render_onboarding        # noqa: E402
from components.checkin import render_checkin              # noqa: E402
from components.dashboard import render_dashboard          # noqa: E402

# ── Session state ──────────────────────────────────────────────────────────────
init_session_state()

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    # Logo / brand
    st.markdown("""
    <div style="text-align:center; padding:1.2rem 0 0.8rem 0;">
        <div style="font-size:2.2rem;">🔬</div>
        <div style="font-size:0.72rem; font-weight:700; letter-spacing:1.5px;
                    color:rgba(255,255,255,0.6); text-transform:uppercase; margin-top:0.3rem;">
            Product Impact
        </div>
        <div style="font-size:1rem; font-weight:800; color:white; letter-spacing:0.5px;">
            Observatory
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Navigation
    st.markdown("""
    <div style="font-size:0.72rem; font-weight:700; letter-spacing:1px;
                color:rgba(255,255,255,0.5); text-transform:uppercase; margin-bottom:0.6rem;">
        Navigate
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "page",
        ["Consumer App", "Analytics Dashboard"],
        label_visibility="collapsed",
    )

    st.divider()

    # Demo mode toggle
    st.markdown("""
    <div style="font-size:0.72rem; font-weight:700; letter-spacing:1px;
                color:rgba(255,255,255,0.5); text-transform:uppercase; margin-bottom:0.6rem;">
        Settings
    </div>
    """, unsafe_allow_html=True)

    st.session_state.demo_mode = st.toggle(
        "Demo mode", value=st.session_state.demo_mode,
        help="Use pre-generated data for the dashboard",
    )

    # Optional API key for AI summary
    with st.expander("AI summary settings"):
        api_key = st.text_input(
            "Anthropic API key *(optional)*",
            type="password",
            placeholder="sk-ant-…",
            help="Leave empty to use the built-in template summary",
            value=st.session_state.api_key,
        )
        st.session_state.api_key = api_key

    # Reset consumer session
    st.divider()
    if st.button("Reset consumer session", use_container_width=True):
        for k in ["onboarded", "user_name", "user_product", "user_goal",
                  "checkins", "today_submitted"]:
            if k in st.session_state:
                del st.session_state[k]
        init_session_state()
        st.rerun()

    # Footer
    st.markdown("""
    <div style="position:absolute; bottom:1rem; left:0; right:0; text-align:center;
                color:rgba(255,255,255,0.3); font-size:0.72rem;">
        PIO · Prototype v1.0
    </div>
    """, unsafe_allow_html=True)

# ── Routing ────────────────────────────────────────────────────────────────────
if page == "Consumer App":
    # Narrow column for mobile feel
    _, col, _ = st.columns([1, 3, 1])
    with col:
        if not st.session_state.onboarded:
            render_onboarding()
        else:
            render_checkin()
else:
    render_dashboard()
