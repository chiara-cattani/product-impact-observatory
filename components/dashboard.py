"""
Analytics Dashboard — evidence generation view for management / stakeholders.
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.analytics import (
    compute_day_trends,
    compute_improvement,
    compute_overview,
    compute_segments,
    compute_symptom_freq,
    generate_insights,
)
from utils.data_manager import get_simulated_data
from utils.llm_summary import get_ai_summary

# ── Shared style helpers ───────────────────────────────────────────────────────

_BLUE   = "#2E86AB"
_GREEN  = "#27AE60"
_AMBER  = "#F39C12"
_RED    = "#E74C3C"
_DARK   = "#1B4F72"
_BG     = "rgba(0,0,0,0)"

_FONT   = dict(family="Inter, sans-serif", size=13, color="#2D3436")
_GRID   = "#ECF0F1"

_CHART_LAYOUT = dict(
    plot_bgcolor=_BG,
    paper_bgcolor=_BG,
    font=_FONT,
    margin=dict(l=10, r=10, t=44, b=10),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
)


def _section(icon: str, title: str) -> None:
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:0.6rem;
                margin:2rem 0 1rem 0; padding-bottom:0.5rem;
                border-bottom:2px solid #EBF5FB;">
        <span style="font-size:1.4rem;">{icon}</span>
        <span style="font-size:1.2rem; font-weight:700; color:{_DARK};">{title}</span>
    </div>
    """, unsafe_allow_html=True)


def _metric_card(value: str, label: str, delta: str = "", color: str = _BLUE) -> str:
    delta_html = (
        f'<div style="font-size:0.85rem; color:{_GREEN}; font-weight:600; margin-top:0.2rem;">'
        f'{delta}</div>'
        if delta else ""
    )
    return f"""
    <div style="background:white; border-radius:14px; padding:1.3rem 1rem;
                box-shadow:0 4px 14px rgba(0,0,0,0.07); border-top:4px solid {color};
                text-align:center;">
        <div style="font-size:2rem; font-weight:800; color:{_DARK}; line-height:1.2;">{value}</div>
        <div style="font-size:0.8rem; color:#7F8C8D; font-weight:600;
                    text-transform:uppercase; letter-spacing:0.4px; margin-top:0.3rem;">{label}</div>
        {delta_html}
    </div>"""


# ── Main entry ─────────────────────────────────────────────────────────────────

def render_dashboard() -> None:
    df = get_simulated_data()

    # ── Dashboard header ──────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="
        background:linear-gradient(135deg, {_DARK} 0%, {_BLUE} 70%, #85C1E9 100%);
        border-radius:18px; padding:1.8rem 2rem; margin-bottom:1.5rem;
        display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:1rem;
    ">
        <div>
            <div style="color:rgba(255,255,255,0.7); font-size:0.8rem; font-weight:700;
                        letter-spacing:1px; text-transform:uppercase;">Product Impact Observatory</div>
            <div style="color:white; font-size:1.6rem; font-weight:800; margin-top:0.3rem;">
                Evidence Dashboard
            </div>
            <div style="color:rgba(255,255,255,0.75); font-size:0.9rem; margin-top:0.3rem;">
                30-day real-world consumer study · {df['user_id'].nunique()} participants
            </div>
        </div>
        <div style="display:flex; gap:0.8rem; flex-wrap:wrap;">
            <div style="background:rgba(255,255,255,0.15); color:white; padding:0.4rem 1rem;
                        border-radius:20px; font-size:0.82rem; font-weight:600;">🔴 Live data</div>
            <div style="background:rgba(255,255,255,0.15); color:white; padding:0.4rem 1rem;
                        border-radius:20px; font-size:0.82rem; font-weight:600;">📊 Demo mode</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Overview metrics ──────────────────────────────────────────────────────
    _section("📊", "Overview")
    ov  = compute_overview(df)
    imp = compute_improvement(df)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(_metric_card(
            str(ov["total_users"]), "Participants", color=_BLUE
        ), unsafe_allow_html=True)
    with c2:
        st.markdown(_metric_card(
            str(ov["total_logs"]), "Days Logged", color="#8E44AD"
        ), unsafe_allow_html=True)
    with c3:
        st.markdown(_metric_card(
            f"{ov['compliance_pct']}%", "Compliance Rate",
            delta="↑ High engagement", color=_GREEN
        ), unsafe_allow_html=True)
    with c4:
        st.markdown(_metric_card(
            f"{imp['pct_improved']}%", "Users Improved",
            delta=f"+{imp['avg_delta']} pts avg", color=_AMBER
        ), unsafe_allow_html=True)

    # ── Trend analysis ────────────────────────────────────────────────────────
    _section("📈", "Trend Analysis")

    trends = compute_day_trends(df)

    col_l, col_r = st.columns([3, 2])

    with col_l:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=trends["day_number"], y=trends["dig_smooth"],
            name="Digestion", mode="lines",
            line=dict(color=_BLUE, width=3),
            fill="tozeroy",
            fillcolor="rgba(46,134,171,0.08)",
        ))
        fig.add_trace(go.Scatter(
            x=trends["day_number"], y=trends["eng_smooth"],
            name="Energy", mode="lines",
            line=dict(color=_AMBER, width=2.5, dash="dot"),
        ))
        # Annotation at day 14
        fig.add_vline(x=14, line_dash="dash", line_color="#BDC3C7", line_width=1.5)
        fig.add_annotation(x=14, y=4.8, text="Week 2", showarrow=False,
                           font=dict(size=11, color="#7F8C8D"))
        fig.update_layout(
            title="Digestion & energy scores over 30 days",
            xaxis_title="Study day",
            yaxis_title="Score (1–5)",
            yaxis=dict(range=[1, 5.2], dtick=1),
            height=340,
            **_CHART_LAYOUT,
        )
        fig.update_xaxes(showgrid=True, gridcolor=_GRID)
        fig.update_yaxes(showgrid=True, gridcolor=_GRID)
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        sym_freq = compute_symptom_freq(df)
        if not sym_freq.empty:
            fig_sym = px.bar(
                sym_freq, x="count", y="symptom", color="week",
                orientation="h",
                color_discrete_sequence=[_RED, _AMBER, _GREEN, "#85C1E9"],
                title="Symptom frequency by week",
                labels={"count": "Reports", "symptom": ""},
            )
            fig_sym.update_layout(
                height=340,
                **_CHART_LAYOUT,
                legend_title="Week",
            )
            fig_sym.update_xaxes(showgrid=True, gridcolor=_GRID)
            st.plotly_chart(fig_sym, use_container_width=True)

    # ── Product impact ─────────────────────────────────────────────────────────
    _section("💊", "Product Impact")

    col_ba, col_dist = st.columns(2)

    with col_ba:
        # Before vs After
        fig_ba = go.Figure()
        categories = ["Digestion Score", "Energy Score"]
        baseline_vals = [imp["avg_baseline"],
                         round(float(df.sort_values("day_number").groupby("user_id").apply(
                             lambda g: g.head(3)["energy_score"].mean()
                         ).mean()), 2)]
        current_vals  = [imp["avg_current"],
                         round(float(df.sort_values("day_number").groupby("user_id").apply(
                             lambda g: g.tail(7)["energy_score"].mean()
                         ).mean()), 2)]

        fig_ba.add_trace(go.Bar(
            name="Baseline (Days 1–3)", x=categories, y=baseline_vals,
            marker_color="#AED6F1", text=[f"{v:.2f}" for v in baseline_vals],
            textposition="outside",
        ))
        fig_ba.add_trace(go.Bar(
            name="End of Study (Days 24–30)", x=categories, y=current_vals,
            marker_color=_BLUE, text=[f"{v:.2f}" for v in current_vals],
            textposition="outside",
        ))
        fig_ba.update_layout(
            title="Before vs after: average scores",
            yaxis=dict(range=[0, 5.8], dtick=1, title="Score (1–5)"),
            barmode="group",
            height=320,
            **_CHART_LAYOUT,
        )
        fig_ba.update_yaxes(showgrid=True, gridcolor=_GRID)
        st.plotly_chart(fig_ba, use_container_width=True)

    with col_dist:
        dist = imp["distribution"]
        labels = list(dist.keys())
        values = [dist.get(l, 0) for l in labels]
        colors = [_RED, "#BDC3C7", _BLUE, _GREEN]

        fig_dist = go.Figure(go.Pie(
            labels=labels, values=values,
            hole=0.52,
            marker=dict(colors=colors[:len(labels)]),
            textinfo="label+percent",
            textfont=dict(size=12),
        ))
        fig_dist.add_annotation(
            text=f"<b>{imp['pct_improved']}%</b><br>improved",
            x=0.5, y=0.5, font_size=16, showarrow=False,
            font=dict(color=_DARK),
        )
        fig_dist.update_layout(
            title="Improvement distribution",
            height=320,
            margin=dict(l=10, r=10, t=44, b=10),
            paper_bgcolor=_BG,
            font=_FONT,
            showlegend=False,
        )
        st.plotly_chart(fig_dist, use_container_width=True)

    # ── Segmentation ───────────────────────────────────────────────────────────
    _section("🔬", "Segmentation Analysis")

    segs    = compute_segments(df)
    col_p, col_s = st.columns(2)

    with col_p:
        by_prod = segs["by_product"].sort_values("avg_digestion", ascending=True)
        fig_prod = go.Figure()
        fig_prod.add_trace(go.Bar(
            y=by_prod["product"], x=by_prod["avg_digestion"],
            orientation="h", name="Digestion",
            marker_color=_BLUE,
            text=[f"{v:.2f}" for v in by_prod["avg_digestion"]],
            textposition="outside",
        ))
        fig_prod.add_trace(go.Bar(
            y=by_prod["product"], x=by_prod["avg_energy"],
            orientation="h", name="Energy",
            marker_color=_AMBER,
            text=[f"{v:.2f}" for v in by_prod["avg_energy"]],
            textposition="outside",
        ))
        fig_prod.update_layout(
            title="Average scores by product",
            xaxis=dict(range=[0, 5.5], dtick=1, title="Score (1–5)"),
            barmode="group",
            height=280,
            **_CHART_LAYOUT,
        )
        fig_prod.update_xaxes(showgrid=True, gridcolor=_GRID)
        st.plotly_chart(fig_prod, use_container_width=True)

    with col_s:
        by_sev = segs["by_severity"]
        if not by_sev.empty:
            _ORDER = ["High severity", "Moderate", "Low severity"]
            by_sev = by_sev[by_sev["severity_group"].isin(_ORDER)].copy()
            by_sev["severity_group"] = pd.Categorical(
                by_sev["severity_group"], categories=_ORDER, ordered=True
            )
            by_sev = by_sev.sort_values("severity_group")

            fig_sev = go.Figure()
            fig_sev.add_trace(go.Bar(
                x=by_sev["severity_group"].astype(str),
                y=by_sev["avg_baseline"],
                name="Baseline", marker_color="#AED6F1",
                text=[f"{v:.2f}" for v in by_sev["avg_baseline"]],
                textposition="outside",
            ))
            fig_sev.add_trace(go.Bar(
                x=by_sev["severity_group"].astype(str),
                y=by_sev["avg_current"],
                name="End of study", marker_color=_GREEN,
                text=[f"{v:.2f}" for v in by_sev["avg_current"]],
                textposition="outside",
            ))
            fig_sev.update_layout(
                title="Improvement by baseline severity group",
                yaxis=dict(range=[0, 5.8], dtick=1, title="Digestion score"),
                barmode="group",
                height=280,
                **_CHART_LAYOUT,
            )
            fig_sev.update_yaxes(showgrid=True, gridcolor=_GRID)
            st.plotly_chart(fig_sev, use_container_width=True)

    # Severity delta highlight
    if not by_sev.empty:
        sev_rows = {str(r["severity_group"]): r for _, r in by_sev.iterrows()}
        m1, m2, m3 = st.columns(3)
        for col_w, sev_label in zip([m1, m2, m3], _ORDER):
            row = sev_rows.get(sev_label)
            if row is not None:
                delta_val = round(float(row["avg_current"]) - float(row["avg_baseline"]), 2)
                with col_w:
                    st.metric(
                        sev_label,
                        f"{row['avg_current']:.2f}",
                        delta=f"+{delta_val:.2f} pts",
                    )

    # ── Insights ───────────────────────────────────────────────────────────────
    _section("💡", "Auto-Generated Insights")

    insights = generate_insights(df)
    for ins in insights:
        st.markdown(f"""
        <div style="
            background:linear-gradient(135deg, #EBF5FB 0%, #D6EAF8 100%);
            border-left:4px solid {_BLUE}; border-radius:0 12px 12px 0;
            padding:0.85rem 1.2rem; margin-bottom:0.7rem;
            font-size:0.95rem; color:{_DARK}; line-height:1.6;
        ">
            {ins}
        </div>
        """, unsafe_allow_html=True)

    # ── AI Summary ─────────────────────────────────────────────────────────────
    _section("🤖", "AI Executive Summary")

    st.markdown("""
    <p style="color:#7F8C8D; font-size:0.88rem; margin-bottom:1rem;">
        Generated from aggregated, anonymised population data only.
        No individual records are processed by the AI model.
    </p>
    """, unsafe_allow_html=True)

    api_key = st.session_state.get("api_key", "")

    if st.button("Generate AI summary", type="primary"):
        with st.spinner("Generating summary…"):
            summary = get_ai_summary(ov, imp, api_key=api_key)
        st.markdown(f"""
        <div style="
            background:linear-gradient(135deg, {_DARK} 0%, {_BLUE} 100%);
            color:white; border-radius:16px; padding:1.8rem 2rem; margin-top:0.5rem;
            line-height:1.8; font-size:0.97rem;
        ">
            <div style="background:rgba(255,255,255,0.18); color:white; padding:0.3rem 0.9rem;
                        border-radius:20px; font-size:0.78rem; font-weight:700;
                        display:inline-block; margin-bottom:1rem; letter-spacing:0.5px;">
                ✦ AI SUMMARY
            </div>
            <div>{summary}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="
            background:#F4F6F9; border:2px dashed #BDC3C7;
            border-radius:14px; padding:1.5rem; text-align:center; color:#AEB6BF;
        ">
            Click <strong>Generate AI summary</strong> above to create an executive brief
            from the population data.
        </div>
        """, unsafe_allow_html=True)


