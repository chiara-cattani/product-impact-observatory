"""
Daily check-in and personal history view — mobile-first consumer interface.
"""

from __future__ import annotations

from datetime import date

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.data_manager import SYMPTOMS, save_checkin


# ── Emoji helpers ──────────────────────────────────────────────────────────────

_SCORE_EMOJI = {1: "😣", 2: "😕", 3: "😐", 4: "🙂", 5: "😊"}
_SCORE_COLOR = {1: "#E74C3C", 2: "#E67E22", 3: "#F1C40F", 4: "#2ECC71", 5: "#27AE60"}


def _score_label(n: int) -> str:
    return f"{_SCORE_EMOJI[n]}  {n}"


# ── Main render ────────────────────────────────────────────────────────────────

def render_checkin() -> None:
    name    = st.session_state.user_name
    product = st.session_state.user_product
    goal    = st.session_state.user_goal

    # Header card
    day_number = len(st.session_state.checkins) + 1
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #1B4F72 0%, #2E86AB 100%);
        border-radius: 16px; padding: 1.4rem 1.5rem; margin-bottom: 1.2rem;
        display: flex; align-items: center; gap: 1rem;
    ">
        <div style="font-size:2.4rem;">👋</div>
        <div>
            <div style="color:rgba(255,255,255,0.7); font-size:0.85rem; font-weight:600;">
                WELCOME BACK
            </div>
            <div style="color:white; font-size:1.3rem; font-weight:800;">{name}</div>
            <div style="color:rgba(255,255,255,0.8); font-size:0.88rem; margin-top:0.2rem;">
                {product} &nbsp;·&nbsp; Day {day_number}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab_today, tab_history = st.tabs(["📋  Today's Check-in", "📈  My History"])

    with tab_today:
        _render_today(goal)

    with tab_history:
        _render_history(name)


# ── Today's check-in ───────────────────────────────────────────────────────────

def _render_today(goal: str) -> None:
    if st.session_state.today_submitted:
        _render_success()
        return

    with st.form("checkin_form"):
        # Digestion score
        st.markdown("#### 🫁 How's your digestion today?")
        dig_score = st.select_slider(
            "Digestion score",
            options=[1, 2, 3, 4, 5],
            value=3,
            format_func=_score_label,
            label_visibility="collapsed",
        )
        _score_bar(dig_score)

        st.markdown("---")

        # Energy score
        st.markdown("#### ⚡ Energy level")
        eng_score = st.select_slider(
            "Energy score",
            options=[1, 2, 3, 4, 5],
            value=3,
            format_func=_score_label,
            label_visibility="collapsed",
        )
        _score_bar(eng_score)

        st.markdown("---")

        # Symptoms
        st.markdown("#### 🔍 Any symptoms today? *(optional)*")
        selected_symptoms = []
        cols = st.columns(2)
        for i, sym in enumerate(SYMPTOMS):
            with cols[i % 2]:
                if st.checkbox(sym, key=f"sym_{sym}"):
                    selected_symptoms.append(sym)

        st.markdown("---")

        # Product taken
        st.markdown("#### 💊 Did you take your product today?")
        product_taken = st.radio(
            "Product taken",
            ["Yes ✅", "No ❌"],
            horizontal=True,
            label_visibility="collapsed",
        )

        # Notes
        notes = st.text_area(
            "Additional notes *(optional)*",
            placeholder="How are you feeling? Any observations…",
            max_chars=300,
        )

        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button(
            "Submit today's check-in  →",
            use_container_width=True,
            type="primary",
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
                "product_taken":   product_taken.startswith("Yes"),
                "notes":           notes.strip(),
            }
            save_checkin(checkin)
            st.session_state.today_submitted = True
            st.rerun()


def _score_bar(score: int) -> None:
    color = _SCORE_COLOR[score]
    pct   = score / 5 * 100
    st.markdown(f"""
    <div style="background:#ECF0F1; border-radius:8px; height:8px; margin:0.4rem 0 1rem 0;">
        <div style="background:{color}; width:{pct}%; height:100%; border-radius:8px;
                    transition:width 0.3s ease;"></div>
    </div>
    """, unsafe_allow_html=True)


def _render_success() -> None:
    st.markdown("""
    <div style="
        text-align:center; padding:2.5rem 1rem;
        background:linear-gradient(135deg,#EAF9EA 0%,#D5F5E3 100%);
        border-radius:16px; margin-top:1rem;
    ">
        <div style="font-size:3.5rem;">🎉</div>
        <h2 style="color:#1E8449; margin:0.5rem 0;">Check-in complete!</h2>
        <p style="color:#27AE60; font-size:1rem; margin:0;">
            Thanks! You're contributing to real-world research.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div style="background:white; border-radius:12px; padding:1rem;
                    box-shadow:0 2px 8px rgba(0,0,0,0.07); text-align:center;">
            <div style="font-size:1.8rem;">🏅</div>
            <div style="font-weight:700; color:#1B4F72; margin-top:0.4rem;">
                Streak maintained!
            </div>
            <div style="font-size:0.85rem; color:#7F8C8D;">Keep it up</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style="background:white; border-radius:12px; padding:1rem;
                    box-shadow:0 2px 8px rgba(0,0,0,0.07); text-align:center;">
            <div style="font-size:1.8rem;">🔬</div>
            <div style="font-weight:700; color:#1B4F72; margin-top:0.4rem;">
                Data recorded
            </div>
            <div style="font-size:0.85rem; color:#7F8C8D;">Powering insights</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Log another day", use_container_width=True):
        st.session_state.today_submitted = False
        st.rerun()


# ── History ────────────────────────────────────────────────────────────────────

def _render_history(name: str) -> None:
    checkins = st.session_state.checkins
    if not checkins:
        st.info("No check-ins yet. Complete your first daily check-in to see your progress here.")
        return

    df = pd.DataFrame(checkins)
    df["day_number"]      = df["day_number"].astype(int)
    df["digestion_score"] = df["digestion_score"].astype(float)
    df["energy_score"]    = df["energy_score"].astype(float)
    df = df.sort_values("day_number")

    # Summary stats
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Days logged", len(df))
    with c2:
        st.metric("Avg digestion", f"{df['digestion_score'].mean():.1f} / 5")
    with c3:
        st.metric("Avg energy", f"{df['energy_score'].mean():.1f} / 5")

    st.markdown("<br>", unsafe_allow_html=True)

    # Personal trend chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["day_number"], y=df["digestion_score"],
        name="Digestion", mode="lines+markers",
        line=dict(color="#2E86AB", width=2.5),
        marker=dict(size=7),
    ))
    fig.add_trace(go.Scatter(
        x=df["day_number"], y=df["energy_score"],
        name="Energy", mode="lines+markers",
        line=dict(color="#F39C12", width=2.5, dash="dot"),
        marker=dict(size=7),
    ))
    fig.update_layout(
        title="Your personal trend",
        xaxis_title="Study day",
        yaxis_title="Score (1–5)",
        yaxis=dict(range=[0.5, 5.5], dtick=1),
        height=320,
        margin=dict(l=10, r=10, t=40, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", size=13),
    )
    fig.update_xaxes(showgrid=True, gridcolor="#ECF0F1")
    fig.update_yaxes(showgrid=True, gridcolor="#ECF0F1")
    st.plotly_chart(fig, use_container_width=True)

    # Recent entries table
    with st.expander("View all entries"):
        display_df = df[["day_number", "date", "digestion_score", "energy_score", "symptoms"]].copy()
        display_df.columns = ["Day", "Date", "Digestion", "Energy", "Symptoms"]
        display_df["Symptoms"] = display_df["Symptoms"].apply(
            lambda s: s.replace("|", ", ") if isinstance(s, str) and s else "—"
        )
        st.dataframe(display_df, use_container_width=True, hide_index=True)
