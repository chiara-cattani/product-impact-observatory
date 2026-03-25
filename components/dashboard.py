import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.analytics import (
    compute_improvement,
    compute_overview,
    compute_segments,
    compute_symptom_freq,
    compute_trends,
    generate_insights,
)
from utils.data_manager import get_sim_df, get_user_df
from utils.llm_summary import get_ai_summary

_BLUE = "#2E86AB"
_GREEN = "#27AE60"
_AMBER = "#F39C12"
_RED = "#E74C3C"
_DARK = "#1B4F72"
_PURPLE = "#8E44AD"


def _kpi_card(label: str, value: str, delta: str = "", color: str = _BLUE) -> str:
    delta_html = (
        f"<div style='font-size:0.82rem;color:{_GREEN};font-weight:600;margin-top:0.25rem;'>{delta}</div>"
        if delta
        else ""
    )
    return (
        f"<div style='background:white;border-radius:14px;padding:1.3rem 1rem;"
        f"box-shadow:0 2px 12px rgba(0,0,0,0.07);border-top:4px solid {color};text-align:center;'>"
        f"<div style='font-size:0.72rem;font-weight:700;color:#95A5A6;"
        f"text-transform:uppercase;letter-spacing:0.8px;'>{label}</div>"
        f"<div style='font-size:2.1rem;font-weight:800;color:{_DARK};line-height:1.2;margin-top:0.4rem;'>{value}</div>"
        f"{delta_html}"
        f"</div>"
    )


def _chart_layout(height: int = 320) -> dict:
    return dict(
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=10, r=10, t=40, b=10),
        height=height,
        font=dict(family="sans-serif", size=12, color="#2D3436"),
    )


def render_dashboard():
    df = get_sim_df()
    live = get_user_df()
    if not live.empty:
        df = pd.concat([df, live], ignore_index=True)

    ov = compute_overview(df)
    trends = compute_trends(df)
    imp = compute_improvement(df)
    segs = compute_segments(df)
    sym_freq = compute_symptom_freq(df)
    insights = generate_insights(df)

    # ── Header ────────────────────────────────────────────────────────────
    st.markdown(
        """
        <div style="background:linear-gradient(135deg,#1B4F72 0%,#2E86AB 100%);
                    border-radius:16px;padding:1.4rem 2rem;margin-bottom:1.5rem;color:white;">
            <div style="font-size:0.72rem;font-weight:700;opacity:0.7;
                        letter-spacing:1.2px;text-transform:uppercase;">
                Danone &nbsp;&middot;&nbsp; Real-World Evidence Platform
            </div>
            <div style="font-size:1.7rem;font-weight:800;margin-top:0.3rem;">
                Product Impact Observatory
            </div>
            <div style="font-size:0.88rem;opacity:0.75;margin-top:0.25rem;">
                30-day consumer study &nbsp;&middot;&nbsp; Live aggregated data
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── KPI Cards ─────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(_kpi_card("Participants", str(ov["n_users"]), color=_DARK), unsafe_allow_html=True)
    with c2:
        st.markdown(_kpi_card("Total Check-ins", str(ov["n_logs"]), color=_BLUE), unsafe_allow_html=True)
    with c3:
        st.markdown(
            _kpi_card("Compliance Rate", f"{ov['compliance_pct']}%", "Strong engagement", _GREEN),
            unsafe_allow_html=True,
        )
    with c4:
        st.markdown(
            _kpi_card("Users Improved", f"{ov['pct_improved']}%", f"avg +{ov['avg_improvement']} pts", _AMBER),
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Trend Chart ───────────────────────────────────────────────────────
    st.markdown("### Score Trends Over 30 Days")
    fig_trend = go.Figure()
    fig_trend.add_trace(
        go.Scatter(
            x=trends["date"],
            y=trends["dig_smooth"],
            name="Digestion",
            mode="lines",
            line=dict(color=_BLUE, width=3),
            fill="tozeroy",
            fillcolor="rgba(46,134,171,0.07)",
        )
    )
    fig_trend.add_trace(
        go.Scatter(
            x=trends["date"],
            y=trends["eng_smooth"],
            name="Energy",
            mode="lines",
            line=dict(color=_GREEN, width=2.5, dash="dot"),
        )
    )
    fig_trend.update_layout(
        **_chart_layout(300),
        yaxis=dict(range=[1, 5.2], title="Avg Score (1-5)", tickvals=[1, 2, 3, 4, 5], gridcolor="#F0F0F0"),
        xaxis=dict(title="", gridcolor="#F0F0F0"),
        legend=dict(orientation="h", y=-0.2, x=0.35),
    )
    st.plotly_chart(fig_trend, use_container_width=True)

    st.markdown("---")

    # ── Before / After + Distribution ─────────────────────────────────────
    st.markdown("### Product Impact: Before vs After")
    col_ba, col_dist = st.columns(2)

    with col_ba:
        ba = imp["before_after"]
        fig_ba = go.Figure()
        fig_ba.add_trace(
            go.Bar(
                name="Before (Day 1-5)",
                x=ba["product"],
                y=ba["Before (Day 1-5)"],
                marker_color="rgba(189,195,199,0.85)",
                text=ba["Before (Day 1-5)"].apply(lambda v: f"{v:.1f}"),
                textposition="outside",
            )
        )
        fig_ba.add_trace(
            go.Bar(
                name="After (Day 25-30)",
                x=ba["product"],
                y=ba["After (Day 25-30)"],
                marker_color=_BLUE,
                text=ba["After (Day 25-30)"].apply(lambda v: f"{v:.1f}"),
                textposition="outside",
            )
        )
        fig_ba.update_layout(
            **_chart_layout(310),
            title="Digestion Score by Product",
            barmode="group",
            yaxis=dict(range=[0, 5.8], title="Avg Score", gridcolor="#F0F0F0"),
            xaxis=dict(tickangle=-10),
            legend=dict(orientation="h", y=-0.28),
        )
        st.plotly_chart(fig_ba, use_container_width=True)

    with col_dist:
        fig_dist = go.Figure(
            go.Histogram(
                x=imp["deltas"],
                nbinsx=14,
                marker_color=_BLUE,
                marker_line=dict(color="white", width=1),
                opacity=0.85,
            )
        )
        fig_dist.add_vline(
            x=0,
            line_dash="dash",
            line_color=_RED,
            line_width=1.5,
            annotation_text="No change",
            annotation_position="top right",
        )
        fig_dist.update_layout(
            **_chart_layout(310),
            title="Distribution of Improvement (delta digestion score)",
            xaxis=dict(title="Score change", gridcolor="#F0F0F0"),
            yaxis=dict(title="Participants", gridcolor="#F0F0F0"),
        )
        st.plotly_chart(fig_dist, use_container_width=True)

    st.markdown("---")

    # ── Segmentation ──────────────────────────────────────────────────────
    st.markdown("### Segmentation Analysis")
    col_prod, col_sev = st.columns(2)

    with col_prod:
        prod = segs["by_product"].sort_values("avg_digestion")
        colors_prod = [_BLUE, _GREEN, _AMBER][: len(prod)]
        fig_prod = go.Figure(
            go.Bar(
                x=prod["avg_digestion"],
                y=prod["product"],
                orientation="h",
                marker_color=colors_prod,
                text=prod["avg_digestion"].apply(lambda v: f"{v:.2f}"),
                textposition="outside",
            )
        )
        fig_prod.update_layout(
            **_chart_layout(240),
            title="Avg Digestion Score by Product",
            xaxis=dict(range=[0, 5.5], gridcolor="#F0F0F0"),
            yaxis=dict(title=""),
        )
        st.plotly_chart(fig_prod, use_container_width=True)

    with col_sev:
        sev = segs["by_severity"]
        colors_sev = [_RED, _AMBER, _GREEN][: len(sev)]
        fig_sev = go.Figure(
            go.Bar(
                x=sev["avg_digestion"],
                y=sev["severity"].astype(str),
                orientation="h",
                marker_color=colors_sev,
                text=sev["avg_digestion"].apply(lambda v: f"{v:.2f}"),
                textposition="outside",
            )
        )
        fig_sev.update_layout(
            **_chart_layout(240),
            title="Avg Digestion Score by Initial Severity",
            xaxis=dict(range=[0, 5.5], gridcolor="#F0F0F0"),
            yaxis=dict(title=""),
        )
        st.plotly_chart(fig_sev, use_container_width=True)

    # ── Symptom Frequency ─────────────────────────────────────────────────
    if not sym_freq.empty:
        st.markdown("---")
        st.markdown("### Symptom Frequency Over Time")
        fig_sym = px.bar(
            sym_freq,
            x="week",
            y="count",
            color="symptom",
            barmode="group",
            color_discrete_sequence=[_BLUE, _RED, _AMBER, _GREEN, _PURPLE],
        )
        fig_sym.update_layout(
            **_chart_layout(260),
            xaxis=dict(title=""),
            yaxis=dict(title="Reported occurrences", gridcolor="#F0F0F0"),
            legend=dict(orientation="h", y=-0.25, title=""),
        )
        st.plotly_chart(fig_sym, use_container_width=True)

    st.markdown("---")

    # ── Insights ──────────────────────────────────────────────────────────
    st.markdown("### Key Insights")
    for insight in insights:
        st.markdown(
            f"<div style='background:#EBF5FB;border-left:4px solid {_BLUE};"
            f"border-radius:0 10px 10px 0;padding:0.7rem 1rem;"
            f"margin-bottom:0.6rem;color:#1B4F72;font-size:0.95rem;'>"
            f"{insight}</div>",
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # ── AI Summary ────────────────────────────────────────────────────────
    st.markdown("### AI-Generated Evidence Summary")
    with st.spinner("Generating summary..."):
        summary = get_ai_summary(
            ov["n_users"],
            ov["n_logs"],
            ov["compliance_pct"],
            ov["pct_improved"],
            ov["avg_improvement"],
        )
    st.markdown(
        f"<div style='background:linear-gradient(135deg,#1B4F72,#2471A3);"
        f"color:white;border-radius:14px;padding:1.5rem 2rem;line-height:1.85;font-size:0.95rem;'>"
        f"<div style='background:rgba(255,255,255,0.15);display:inline-block;"
        f"border-radius:20px;padding:0.2rem 0.9rem;font-size:0.72rem;"
        f"font-weight:700;letter-spacing:0.8px;margin-bottom:0.9rem;'>AI SUMMARY</div>"
        f"<div>{summary}</div>"
        f"</div>",
        unsafe_allow_html=True,
    )
