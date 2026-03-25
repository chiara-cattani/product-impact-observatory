from datetime import date

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.data_manager import SYMPTOMS, save_checkin

_SCORE_EMOJI  = {1: "&#128543;", 2: "&#128533;", 3: "&#128528;", 4: "&#128522;", 5: "&#128522;"}
_SCORE_COLOR  = {1: "#E74C3C", 2: "#E67E22", 3: "#F1C40F", 4: "#2ECC71", 5: "#27AE60"}
_SCORE_LABEL  = {1: "1  Very poor", 2: "2  Poor", 3: "3  Okay", 4: "4  Good", 5: "5  Great"}


def render_checkin() -> None:
    name       = st.session_state.user_name
    product    = st.session_state.user_product
    goal       = st.session_state.user_goal
    day_number = len(st.session_state.checkins) + 1

    st.markdown(
        f"<div style='background:linear-gradient(135deg,#1B4F72 0%,#2E86AB 100%);"
        f"border-radius:16px;padding:1.4rem 1.5rem;margin-bottom:1.2rem;"
        f"display:flex;align-items:center;gap:1rem;'>"
        f"<div style='font-size:2.4rem;'>&#128075;</div>"
        f"<div>"
        f"<div style='color:rgba(255,255,255,0.7);font-size:0.85rem;font-weight:600;'>WELCOME BACK</div>"
        f"<div style='color:white;font-size:1.3rem;font-weight:800;'>{name}</div>"
        f"<div style='color:rgba(255,255,255,0.8);font-size:0.88rem;margin-top:0.2rem;'>"
        f"{product} &nbsp;&middot;&nbsp; Day {day_number}</div>"
        f"</div></div>",
        unsafe_allow_html=True,
    )

    tab_today, tab_history = st.tabs(["Today's Check-in", "My History"])
    with tab_today:
        _render_today()
    with tab_history:
        _render_history()


def _render_today() -> None:
    if st.session_state.today_submitted:
        st.markdown("""
        <div style="text-align:center;padding:2.5rem 1rem;
                    background:linear-gradient(135deg,#EAF9EA 0%,#D5F5E3 100%);
                    border-radius:16px;margin-top:1rem;">
            <div style="font-size:3.5rem;">&#127881;</div>
            <h2 style="color:#1E8449;margin:0.5rem 0;">Check-in complete!</h2>
            <p style="color:#27AE60;font-size:1rem;margin:0;">
                Thanks! You are contributing to real-world research.
            </p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(
                "<div style='background:white;border-radius:12px;padding:1rem;"
                "box-shadow:0 2px 8px rgba(0,0,0,0.07);text-align:center;'>"
                "<div style='font-size:1.8rem;'>&#127885;</div>"
                "<div style='font-weight:700;color:#1B4F72;margin-top:0.4rem;'>Streak kept!</div>"
                "<div style='font-size:0.85rem;color:#7F8C8D;'>Keep it up</div></div>",
                unsafe_allow_html=True,
            )
        with col2:
            st.markdown(
                "<div style='background:white;border-radius:12px;padding:1rem;"
                "box-shadow:0 2px 8px rgba(0,0,0,0.07);text-align:center;'>"
                "<div style='font-size:1.8rem;'>&#128300;</div>"
                "<div style='font-weight:700;color:#1B4F72;margin-top:0.4rem;'>Data recorded</div>"
                "<div style='font-size:0.85rem;color:#7F8C8D;'>Powering insights</div></div>",
                unsafe_allow_html=True,
            )
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Log another day (demo)", use_container_width=True):
            st.session_state.today_submitted = False
            st.rerun()
        return

    with st.form("checkin_form"):
        st.markdown("#### How is your digestion today?")
        dig_score = st.select_slider(
            "Digestion score",
            options=[1, 2, 3, 4, 5],
            value=3,
            format_func=lambda x: _SCORE_LABEL[x],
            label_visibility="collapsed",
        )
        _score_bar(dig_score)

        st.markdown("---")
        st.markdown("#### Energy level")
        eng_score = st.select_slider(
            "Energy score",
            options=[1, 2, 3, 4, 5],
            value=3,
            format_func=lambda x: _SCORE_LABEL[x],
            label_visibility="collapsed",
        )
        _score_bar(eng_score)

        st.markdown("---")
        st.markdown("#### Any symptoms today? *(optional)*")
        selected_symptoms = []
        cols = st.columns(2)
        for i, sym in enumerate(SYMPTOMS):
            with cols[i % 2]:
                if st.checkbox(sym, key=f"sym_{sym}"):
                    selected_symptoms.append(sym)

        st.markdown("---")
        st.markdown("#### Did you take your product today?")
        product_taken = st.radio(
            "Product taken",
            ["Yes", "No"],
            horizontal=True,
            label_visibility="collapsed",
        )

        notes = st.text_area(
            "Additional notes *(optional)*",
            placeholder="How are you feeling? Any observations...",
            max_chars=300,
        )

        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button(
            "Submit today's check-in", use_container_width=True, type="primary"
        )

    if submitted:
        checkin = {
            "date":            str(date.today()),
            "day_number":      len(st.session_state.checkins) + 1,
            "user_name":       st.session_state.user_name,
            "product":         st.session_state.user_product,
            "goal":            st.session_state.user_goal,
            "digestion_score": dig_score,
            "energy_score":    eng_score,
            "symptoms":        "|".join(selected_symptoms),
            "product_taken":   product_taken == "Yes",
            "notes":           notes.strip(),
        }
        save_checkin(checkin)
        st.session_state.today_submitted = True
        st.rerun()


def _score_bar(score: int) -> None:
    color = _SCORE_COLOR[score]
    pct   = score / 5 * 100
    st.markdown(
        f"<div style='background:#ECF0F1;border-radius:8px;height:8px;margin:0.4rem 0 1rem 0;'>"
        f"<div style='background:{color};width:{pct}%;height:100%;border-radius:8px;'></div>"
        f"</div>",
        unsafe_allow_html=True,
    )


def _render_history() -> None:
    checkins = st.session_state.checkins
    if not checkins:
        st.info("No check-ins yet. Complete your first daily check-in to see your progress here.")
        return

    df = pd.DataFrame(checkins)
    df["day_number"]      = df["day_number"].astype(int)
    df["digestion_score"] = df["digestion_score"].astype(float)
    df["energy_score"]    = df["energy_score"].astype(float)
    df = df.sort_values("day_number")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Days logged", len(df))
    with c2:
        st.metric("Avg digestion", f"{df['digestion_score'].mean():.1f} / 5")
    with c3:
        st.metric("Avg energy", f"{df['energy_score'].mean():.1f} / 5")

    st.markdown("<br>", unsafe_allow_html=True)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["day_number"], y=df["digestion_score"],
        name="Digestion", mode="lines+markers",
        line=dict(color="#2E86AB", width=2.5), marker=dict(size=7),
    ))
    fig.add_trace(go.Scatter(
        x=df["day_number"], y=df["energy_score"],
        name="Energy", mode="lines+markers",
        line=dict(color="#F39C12", width=2.5, dash="dot"), marker=dict(size=7),
    ))
    fig.update_layout(
        title="Your personal trend",
        xaxis_title="Study day",
        yaxis=dict(range=[0.5, 5.5], dtick=1, title="Score (1-5)"),
        height=320,
        margin=dict(l=10, r=10, t=40, b=10),
        legend=dict(orientation="h", y=-0.25),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_xaxes(showgrid=True, gridcolor="#ECF0F1")
    fig.update_yaxes(showgrid=True, gridcolor="#ECF0F1")
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("View all entries"):
        display = df[["day_number", "date", "digestion_score", "energy_score", "symptoms"]].copy()
        display.columns = ["Day", "Date", "Digestion", "Energy", "Symptoms"]
        display["Symptoms"] = display["Symptoms"].apply(
            lambda s: s.replace("|", ", ") if isinstance(s, str) and s else "-"
        )
        st.dataframe(display, use_container_width=True, hide_index=True)
