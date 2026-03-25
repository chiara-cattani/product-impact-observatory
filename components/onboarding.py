import streamlit as st
from utils.data_manager import PRODUCTS, GOALS


def render_onboarding() -> None:
    st.markdown("""
    <div style="background:linear-gradient(135deg,#1B4F72 0%,#2E86AB 60%,#85C1E9 100%);
                border-radius:20px;padding:2.5rem 1.5rem;text-align:center;margin-bottom:1.5rem;">
        <div style="font-size:3.5rem;margin-bottom:0.5rem;">&#127807;</div>
        <h1 style="color:white;font-size:1.7rem;margin:0 0 0.5rem 0;font-weight:800;">
            Track how this product impacts you
        </h1>
        <p style="color:rgba(255,255,255,0.85);font-size:1rem;margin:0;">
            Join consumers generating real-world health evidence
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    for col, icon, label in zip(
        [col1, col2, col3],
        ["&#128202;", "&#128300;", "&#128154;"],
        ["Track progress", "Contribute science", "See real results"],
    ):
        with col:
            st.markdown(
                f"<div style='text-align:center;padding:0.8rem;background:white;"
                f"border-radius:12px;box-shadow:0 2px 8px rgba(0,0,0,0.07);'>"
                f"<div style='font-size:1.6rem;'>{icon}</div>"
                f"<div style='font-size:0.8rem;color:#5D6D7E;font-weight:600;margin-top:0.3rem;'>"
                f"{label}</div></div>",
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    with st.form("onboarding_form", clear_on_submit=False):
        st.markdown("#### Tell us about yourself")
        name    = st.text_input("Your first name", placeholder="e.g. Maria")
        product = st.selectbox("Product you are using", PRODUCTS)
        goal    = st.selectbox("Your main health goal", GOALS)

        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("Start my journey", type="primary", use_container_width=True)

    if submitted:
        if not name.strip():
            st.error("Please enter your first name to continue.")
        else:
            st.session_state.user_name    = name.strip()
            st.session_state.user_product = product
            st.session_state.user_goal    = goal
            st.session_state.onboarded    = True
            st.rerun()

    st.markdown(
        "<p style='text-align:center;color:#AEB6BF;font-size:0.78rem;margin-top:1.5rem;'>"
        "Your data is used only to generate aggregated population insights.</p>",
        unsafe_allow_html=True,
    )
