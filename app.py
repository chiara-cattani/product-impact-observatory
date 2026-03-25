import streamlit as st

st.set_page_config(
    page_title="Product Impact Observatory",
    page_icon="&#128300;",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={"About": "Product Impact Observatory — Danone real-world evidence prototype"},
)

st.markdown("""
<style>
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
header    { visibility: hidden; }

/* ---- Nav radio styled as pill toggle ---- */
div[data-testid="stRadio"] > div {
    flex-direction: row;
    gap: 0.5rem;
}
div[data-testid="stRadio"] label {
    border: 2px solid #D5D8DC !important;
    border-radius: 30px !important;
    padding: 0.45rem 1.3rem !important;
    cursor: pointer;
    font-weight: 600 !important;
    font-size: 0.93rem !important;
    color: #5D6D7E !important;
    transition: all 0.18s;
    background: white !important;
}
div[data-testid="stRadio"] label:has(input:checked) {
    background: #1B4F72 !important;
    border-color: #1B4F72 !important;
    color: white !important;
}
div[data-testid="stRadio"] label p {
    color: inherit !important;
}

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

/* ---- Metrics ---- */
[data-testid="metric-container"] {
    background: white;
    border-radius: 12px;
    padding: 0.8rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

/* ---- Divider ---- */
hr { margin: 0.5rem 0 1.2rem 0; border-color: #ECF0F1; }
</style>
""", unsafe_allow_html=True)

from utils.data_manager import init_session_state      # noqa: E402
from components.onboarding import render_onboarding    # noqa: E402
from components.checkin import render_checkin          # noqa: E402
from components.dashboard import render_dashboard      # noqa: E402

init_session_state()

# ── Top navigation — always visible ──────────────────────────────────────────
nav_left, nav_center, nav_right = st.columns([2, 3, 1])

with nav_left:
    st.markdown(
        "<div style='padding:0.45rem 0;'>"
        "<span style='font-size:1.1rem;font-weight:800;color:#1B4F72;'>&#128300; Product Impact Observatory</span>"
        "<span style='font-size:0.72rem;color:#AEB6BF;margin-left:0.5rem;'>by Danone</span>"
        "</div>",
        unsafe_allow_html=True,
    )

with nav_center:
    view = st.radio(
        "nav",
        ["&#128241;  Consumer App", "&#128202;  Researcher Dashboard"],
        horizontal=True,
        label_visibility="collapsed",
        key="nav_radio",
    )

with nav_right:
    if st.button("Reset", help="Reset consumer session"):
        st.session_state.onboarded       = False
        st.session_state.checkins        = []
        st.session_state.today_submitted = False
        st.rerun()

st.divider()

# ── Route ─────────────────────────────────────────────────────────────────────
if "Consumer" in view:
    _, col_app, _ = st.columns([1, 2, 1])
    with col_app:
        if not st.session_state.onboarded:
            render_onboarding()
        else:
            render_checkin()
else:
    # Optional API key in sidebar for AI summary
    with st.sidebar:
        st.markdown("### Settings")
        api_key = st.text_input(
            "Anthropic API key *(optional)*",
            type="password",
            placeholder="sk-ant-...",
            help="Leave empty to use the built-in template summary",
            value=st.session_state.api_key,
        )
        st.session_state.api_key = api_key
        st.caption("Key is used only for the AI summary feature.")
    render_dashboard()
