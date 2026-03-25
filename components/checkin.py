from datetime import date

import plotly.graph_objects as go
import streamlit as st

from utils.data_manager import SYMPTOMS, get_user_df, save_checkin

_LABELS = {1: "Very poor", 2: "Poor", 3: "Okay", 4: "Good", 5: "Great"}
_EMOJI = {1: "😣", 2: "😕", 3: "😐", 4: "🙂", 5: "😄"}


def render_checkin():
    name = st.session_state.user_name
    product = st.session_state.user_product
    goal = st.session_state.user_goal
    day_num = len(st.session_state.checkins) + 1

    st.markdown(
        f"""
        <div style="background:linear-gradient(135deg,#1B4F72,#2E86AB);
                    color:white;border-radius:16px;padding:1.5rem;
                    margin-bottom:1.2rem;text-align:center;">
            <div style="font-size:2rem;">&#128075;</div>
            <div style="font-size:1.5rem;font-weight:800;">Hi, {name}!</div>
            <div style="font-size:0.9rem;opacity:0.85;margin-top:0.3rem;">
                {product} &nbsp;&middot;&nbsp; Goal: {goal}
            </div>
            <div style="margin-top:0.8rem;background:rgba(255,255,255,0.2);
                        border-radius:20px;padding:0.3rem 1rem;display:inline-block;
                        font-size:0.85rem;font-weight:600;">
                Day {day_num} of your journey
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab_today, tab_history = st.tabs(["Today's Check-in", "My Progress"])

    with tab_today:
        _render_form(day_num)

    with tab_history:
        _render_history()


def _render_form(day_num: int):
    if st.session_state.today_submitted:
        st.success("Check-in submitted! Thank you for contributing to real-world research.")
        st.markdown(
            """
            <div style="background:#EBF5FB;border-radius:12px;padding:1.5rem;text-align:center;margin-top:1rem;">
                <div style="font-size:2.5rem;">&#128300;</div>
                <div style="font-weight:700;color:#1B4F72;font-size:1.1rem;margin-top:0.5rem;">
                    Your data is helping build evidence
                </div>
                <div style="color:#5D6D7E;font-size:0.9rem;margin-top:0.4rem;">
                    Come back tomorrow for your next check-in
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Submit another entry (demo)", use_container_width=True):
            st.session_state.today_submitted = False
            st.rerun()
        return

    with st.form("checkin_form"):
        st.markdown("#### How is your digestion today?")
        dig = st.select_slider(
            "Digestion",
            options=[1, 2, 3, 4, 5],
            format_func=lambda x: f"{_EMOJI[x]} {_LABELS[x]}",
            value=3,
            label_visibility="collapsed",
        )

        st.markdown("#### How is your energy level?")
        eng = st.select_slider(
            "Energy",
            options=[1, 2, 3, 4, 5],
            format_func=lambda x: f"{_EMOJI[x]} {_LABELS[x]}",
            value=3,
            label_visibility="collapsed",
        )

        st.markdown("#### Any symptoms today? *(optional)*")
        cols = st.columns(2)
        selected_syms = []
        for idx, sym in enumerate(SYMPTOMS):
            with cols[idx % 2]:
                if st.checkbox(sym, key=f"sym_{sym}"):
                    selected_syms.append(sym)

        st.markdown("#### Did you take the product today?")
        taken = st.radio(
            "Taken",
            ["Yes", "No"],
            horizontal=True,
            label_visibility="collapsed",
        )

        notes = st.text_area(
            "Notes (optional)",
            placeholder="How are you feeling overall?",
            height=80,
        )

        submitted = st.form_submit_button(
            "Submit today's check-in", type="primary", use_container_width=True
        )

    if submitted:
        checkins = st.session_state.checkins
        entry = {
            "user_id": st.session_state.user_id,
            "user_name": st.session_state.user_name,
            "product": st.session_state.user_product,
            "goal": st.session_state.user_goal,
            "date": date.today().isoformat(),
            "day_number": day_num,
            "digestion_score": dig,
            "energy_score": eng,
            "symptoms": "|".join(selected_syms),
            "product_taken": taken == "Yes",
            "notes": notes,
            "baseline_digestion": checkins[0]["digestion_score"] if checkins else dig,
            "baseline_energy": checkins[0]["energy_score"] if checkins else eng,
        }
        save_checkin(entry)
        st.session_state.today_submitted = True
        st.rerun()


def _render_history():
    df = get_user_df()
    if df.empty:
        st.info("No entries yet. Complete your first check-in to see your progress here.")
        return

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["day_number"],
            y=df["digestion_score"],
            mode="lines+markers",
            name="Digestion",
            line=dict(color="#2E86AB", width=2.5),
            marker=dict(size=8),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["day_number"],
            y=df["energy_score"],
            mode="lines+markers",
            name="Energy",
            line=dict(color="#27AE60", width=2.5, dash="dot"),
            marker=dict(size=8),
        )
    )
    fig.update_layout(
        title="Your scores over time",
        xaxis_title="Day",
        yaxis=dict(range=[0.5, 5.5], tickvals=[1, 2, 3, 4, 5], title="Score"),
        plot_bgcolor="white",
        paper_bgcolor="white",
        legend=dict(orientation="h", y=-0.25),
        margin=dict(l=10, r=10, t=40, b=10),
        height=320,
    )
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("View all entries"):
        st.dataframe(
            df[["date", "day_number", "digestion_score", "energy_score", "symptoms", "product_taken"]]
            .rename(columns={
                "day_number": "Day",
                "digestion_score": "Digestion",
                "energy_score": "Energy",
                "symptoms": "Symptoms",
                "product_taken": "Product taken",
            }),
            use_container_width=True,
        )
