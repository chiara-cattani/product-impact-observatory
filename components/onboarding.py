import streamlit as st

from utils.data_manager import GOALS, PRODUCTS


def render_onboarding():
    st.markdown(
        """
        <div style="text-align:center;padding:2rem 0 1.5rem 0;">
            <div style="font-size:3.5rem;">&#127807;</div>
            <h1 style="font-size:1.9rem;font-weight:800;color:#1B4F72;margin:0.5rem 0 0.3rem 0;">
                Track how this product impacts you
            </h1>
            <p style="color:#7F8C8D;font-size:1rem;margin:0;">
                Join consumers generating real-world health evidence
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("onboarding_form"):
        name = st.text_input("Your first name", placeholder="e.g. Maria")
        product = st.selectbox("Product you are using", PRODUCTS)
        goal = st.selectbox("Your main goal", GOALS)

        st.markdown("<br>", unsafe_allow_html=True)
        col_demo, col_start = st.columns(2)
        with col_demo:
            demo = st.form_submit_button("Quick demo fill", use_container_width=True)
        with col_start:
            submitted = st.form_submit_button("Start my journey", type="primary", use_container_width=True)

    if demo:
        st.session_state.user_name = "Maria"
        st.session_state.user_product = PRODUCTS[0]
        st.session_state.user_goal = GOALS[0]
        st.session_state.onboarded = True
        st.rerun()

    if submitted:
        if not name.strip():
            st.error("Please enter your name.")
        else:
            st.session_state.user_name = name.strip()
            st.session_state.user_product = product
            st.session_state.user_goal = goal
            st.session_state.onboarded = True
            st.rerun()
