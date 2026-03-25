import streamlit as st

from components.checkin import render_checkin
from components.dashboard import render_dashboard
from components.onboarding import render_onboarding
from utils.data_manager import init_session_state

st.set_page_config(
    page_title="Product Impact Observatory",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    #MainMenu  { visibility: hidden; }
    footer     { visibility: hidden; }
    header     { visibility: hidden; }

    /* ---- Top nav segmented-control styling ---- */
    div[data-testid="stHorizontalBlock"] { align-items: center; }

    /* Radio buttons styled as pill toggle */
    div[data-testid="stRadio"] > div {
        flex-direction: row;
        gap: 0.5rem;
    }
    div[data-testid="stRadio"] label {
        border: 2px solid #D5D8DC;
        border-radius: 30px;
        padding: 0.45rem 1.2rem;
        cursor: pointer;
        font-weight: 600;
        font-size: 0.92rem;
        color: #5D6D7E;
        transition: all 0.18s;
    }
    div[data-testid="stRadio"] label:has(input:checked) {
        background: #1B4F72;
        border-color: #1B4F72;
        color: white;
    }

    /* ---- Metric/KPI cards ---- */
    [data-testid="metric-container"] {
        background: white;
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.06);
    }

    /* ---- Divider ---- */
    hr { margin: 0.6rem 0 1.2rem 0; border-color: #ECF0F1; }

    /* ---- Tabs ---- */
    .stTabs [data-baseweb="tab"] {
        font-weight: 600;
        padding: 0.5rem 0.2rem;
    }

    /* ---- Buttons ---- */
    .stButton > button {
        border-radius: 10px !important;
        font-weight: 600 !important;
    }

    /* ---- Select slider track ---- */
    [data-baseweb="slider"] [data-testid="stThumbValue"] {
        background: #1B4F72 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

init_session_state()

# ── Top navigation bar — always visible ──────────────────────────────────────
nav_left, nav_center, nav_right = st.columns([2, 3, 1])

with nav_left:
    st.markdown(
        "<div style='padding:0.5rem 0;'>"
        "<span style='font-size:1.1rem;font-weight:800;color:#1B4F72;'>🔬 Product Impact Observatory</span>"
        "<span style='font-size:0.72rem;color:#AEB6BF;margin-left:0.5rem;'>by Danone</span>"
        "</div>",
        unsafe_allow_html=True,
    )

with nav_center:
    view = st.radio(
        "nav",
        ["📱  Consumer App", "📊  Researcher Dashboard"],
        horizontal=True,
        label_visibility="collapsed",
        key="nav_radio",
    )

with nav_right:
    if st.button("↺ Reset", help="Reset consumer onboarding"):
        st.session_state.onboarded = False
        st.session_state.checkins = []
        st.session_state.today_submitted = False
        st.rerun()

st.divider()

# ── Route ─────────────────────────────────────────────────────────────────────
if view == "📱  Consumer App":
    _, col_app, _ = st.columns([1, 2, 1])
    with col_app:
        if not st.session_state.onboarded:
            render_onboarding()
        else:
            render_checkin()
else:
    render_dashboard()
