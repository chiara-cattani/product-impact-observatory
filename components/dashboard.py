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

_BLUE   = "#2E86AB"
_GREEN  = "#27AE60"
_AMBER  = "#F39C12"
_RED    = "#E74C3C"
_DARK   = "#1B4F72"
_PURPLE = "#8E44AD"
_GRID   = "#ECF0F1"

_CHART = dict(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=10, r=10, t=44, b=10),
    font=dict(family="sans-serif", size=12, color="#2D3436"),
)


def _kpi(value: str, label: str, delta: str = "", color: str = _BLUE) -> str:
    dhtml = (
        f"<div style='font-size:0.82rem;color:{_GREEN};font-weight:600;margin-top:0.25rem;'>{delta}</div>"
        if delta else ""
    )
    return (
        f"<div style='background:white;border-radius:14px;padding:1.3rem 1rem;"
        f"box-shadow:0 2px 12px rgba(0,0,0,0.07);border-top:4px solid {color};text-align:center;'>"
        f"<div style='font-size:2.1rem;font-weight:800;color:{_DARK};line-height:1.2;'>{value}</div>"
        f"<div style='font-size:0.72rem;font-weight:700;color:#95A5A6;"
        f"text-transform:uppercase;letter-spacing:0.8px;margin-top:0.3rem;'>{label}</div>"
        f"{dhtml}</div>"
    )


def _section(title: str) -> None:
    st.markdown(
        f"<div style='border-bottom:2px solid #EBF5FB;padding-bottom:0.4rem;"
        f"margin:2rem 0 1rem 0;font-size:1.15rem;font-weight:700;color:{_DARK};'>"
        f"{title}</div>",
        unsafe_allow_html=True,
    )


def render_dashboard() -> None:
    df  = get_simulated_data()
    ov  = compute_overview(df)
    imp = compute_improvement(df)
    trends = compute_day_trends(df)
    segs   = compute_segments(df)
    sym_freq = compute_symptom_freq(df)
    insights = generate_insights(df)

    # ── Header ────────────────────────────────────────────────────────────
    st.markdown(
        f"<div style='background:linear-gradient(135deg,{_DARK} 0%,{_BLUE} 70%,#85C1E9 100%);"
        f"border-radius:16px;padding:1.5rem 2rem;margin-bottom:1.5rem;color:white;"
        f"display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:1rem;'>"
        f"<div>"
        f"<div style='color:rgba(255,255,255,0.7);font-size:0.72rem;font-weight:700;"
        f"letter-spacing:1px;text-transform:uppercase;'>Danone &middot; Real-World Evidence Platform</div>"
        f"<div style='font-size:1.7rem;font-weight:800;margin-top:0.3rem;'>Product Impact Observatory</div>"
        f"<div style='color:rgba(255,255,255,0.75);font-size:0.88rem;margin-top:0.25rem;'>"
        f"30-day consumer study &middot; {ov['total_users']} participants</div>"
        f"</div>"
        f"<div style='display:flex;gap:0.7rem;flex-wrap:wrap;'>"
        f"<div style='background:rgba(255,255,255,0.15);padding:0.35rem 1rem;"
        f"border-radius:20px;font-size:0.82rem;font-weight:600;'>&#128308; Live data</div>"
        f"<div style='background:rgba(255,255,255,0.15);padding:0.35rem 1rem;"
        f"border-radius:20px;font-size:0.82rem;font-weight:600;'>&#128202; Demo mode</div>"
        f"</div></div>",
        unsafe_allow_html=True,
    )

    # ── KPIs ──────────────────────────────────────────────────────────────
    _section("Overview")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(_kpi(str(ov["total_users"]), "Participants", color=_DARK), unsafe_allow_html=True)
    with c2:
        st.markdown(_kpi(str(ov["total_logs"]), "Total Check-ins", color=_BLUE), unsafe_allow_html=True)
    with c3:
        st.markdown(_kpi(f"{ov['compliance_pct']}%", "Compliance Rate", "Strong engagement", _GREEN), unsafe_allow_html=True)
    with c4:
        st.markdown(_kpi(f"{ov['pct_improved']}%", "Users Improved", f"avg +{ov['avg_improvement']} pts", _AMBER), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Trend + Symptom freq ──────────────────────────────────────────────
    _section("Trend Analysis")
    col_l, col_r = st.columns([3, 2])

    with col_l:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=trends["day_number"], y=trends["dig_smooth"],
            name="Digestion", mode="lines",
            line=dict(color=_BLUE, width=3),
            fill="tozeroy", fillcolor="rgba(46,134,171,0.08)",
        ))
        fig.add_trace(go.Scatter(
            x=trends["day_number"], y=trends["eng_smooth"],
            name="Energy", mode="lines",
            line=dict(color=_AMBER, width=2.5, dash="dot"),
        ))
        fig.add_vline(x=14, line_dash="dash", line_color=_GRID, line_width=1.5)
        fig.add_annotation(x=14, y=4.9, text="Week 2", showarrow=False,
                           font=dict(size=11, color="#7F8C8D"))
        fig.update_layout(
            **_CHART,
            title="Digestion & energy scores over 30 days",
            xaxis_title="Study day",
            yaxis=dict(range=[1, 5.2], dtick=1, title="Score (1-5)", gridcolor=_GRID),
            xaxis=dict(gridcolor=_GRID),
            legend=dict(orientation="h", y=-0.2, x=0.3),
            height=340,
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        if not sym_freq.empty:
            fig_sym = px.bar(
                sym_freq, x="count", y="symptom", color="week",
                orientation="h",
                color_discrete_sequence=[_RED, _AMBER, _GREEN, "#85C1E9"],
                title="Symptom frequency by week",
                labels={"count": "Reports", "symptom": ""},
            )
            fig_sym.update_layout(**_CHART, height=340, legend_title="Week",
                                  xaxis=dict(gridcolor=_GRID))
            st.plotly_chart(fig_sym, use_container_width=True)

    # ── Before / After ────────────────────────────────────────────────────
    _section("Product Impact: Before vs After")
    col_ba, col_dist = st.columns(2)

    with col_ba:
        categories   = ["Digestion Score", "Energy Score"]
        base_vals    = [imp["avg_baseline"],
                        round(float(df.sort_values("day_number").groupby("user_id")
                                    .apply(lambda g: g.head(3)["energy_score"].mean()).mean()), 2)]
        current_vals = [imp["avg_current"],
                        round(float(df.sort_values("day_number").groupby("user_id")
                                    .apply(lambda g: g.tail(7)["energy_score"].mean()).mean()), 2)]
        fig_ba = go.Figure()
        fig_ba.add_trace(go.Bar(
            name="Baseline (Days 1-3)", x=categories, y=base_vals,
            marker_color="#AED6F1",
            text=[f"{v:.2f}" for v in base_vals], textposition="outside",
        ))
        fig_ba.add_trace(go.Bar(
            name="End of study (Days 24-30)", x=categories, y=current_vals,
            marker_color=_BLUE,
            text=[f"{v:.2f}" for v in current_vals], textposition="outside",
        ))
        fig_ba.update_layout(
            **_CHART, title="Before vs after: average scores",
            barmode="group",
            yaxis=dict(range=[0, 5.8], dtick=1, title="Score (1-5)", gridcolor=_GRID),
            legend=dict(orientation="h", y=-0.28),
            height=320,
        )
        st.plotly_chart(fig_ba, use_container_width=True)

    with col_dist:
        dist   = imp["distribution"]
        labels = list(dist.keys())
        values = [dist[l] for l in labels]
        colors = [_RED, "#BDC3C7", _BLUE, _GREEN]
        fig_d = go.Figure(go.Pie(
            labels=labels, values=values, hole=0.52,
            marker=dict(colors=colors[:len(labels)]),
            textinfo="label+percent", textfont=dict(size=12),
        ))
        fig_d.add_annotation(
            text=f"<b>{imp['pct_improved']}%</b><br>improved",
            x=0.5, y=0.5, font_size=16, showarrow=False, font=dict(color=_DARK),
        )
        fig_d.update_layout(
            **_CHART, title="Improvement distribution",
            height=320, showlegend=False,
        )
        st.plotly_chart(fig_d, use_container_width=True)

    # ── Segmentation ──────────────────────────────────────────────────────
    _section("Segmentation Analysis")
    col_p, col_s = st.columns(2)

    with col_p:
        bp = segs["by_product"].sort_values("avg_digestion")
        fig_p = go.Figure()
        fig_p.add_trace(go.Bar(
            y=bp["product"], x=bp["avg_digestion"], orientation="h",
            name="Digestion", marker_color=_BLUE,
            text=[f"{v:.2f}" for v in bp["avg_digestion"]], textposition="outside",
        ))
        fig_p.add_trace(go.Bar(
            y=bp["product"], x=bp["avg_energy"], orientation="h",
            name="Energy", marker_color=_AMBER,
            text=[f"{v:.2f}" for v in bp["avg_energy"]], textposition="outside",
        ))
        fig_p.update_layout(
            **_CHART, title="Avg scores by product", barmode="group",
            xaxis=dict(range=[0, 5.5], dtick=1, gridcolor=_GRID),
            legend=dict(orientation="h", y=-0.28),
            height=280,
        )
        st.plotly_chart(fig_p, use_container_width=True)

    with col_s:
        bs = segs["by_severity"]
        if not bs.empty:
            _ORDER = ["High severity", "Moderate", "Low severity"]
            bs = bs[bs["severity_group"].isin(_ORDER)].copy()
            bs["severity_group"] = pd.Categorical(bs["severity_group"], categories=_ORDER, ordered=True)
            bs = bs.sort_values("severity_group")
            fig_s = go.Figure()
            fig_s.add_trace(go.Bar(
                x=bs["severity_group"].astype(str), y=bs["avg_baseline"],
                name="Baseline", marker_color="#AED6F1",
                text=[f"{v:.2f}" for v in bs["avg_baseline"]], textposition="outside",
            ))
            fig_s.add_trace(go.Bar(
                x=bs["severity_group"].astype(str), y=bs["avg_current"],
                name="End of study", marker_color=_GREEN,
                text=[f"{v:.2f}" for v in bs["avg_current"]], textposition="outside",
            ))
            fig_s.update_layout(
                **_CHART, title="Improvement by baseline severity",
                barmode="group",
                yaxis=dict(range=[0, 5.8], dtick=1, gridcolor=_GRID),
                legend=dict(orientation="h", y=-0.28),
                height=280,
            )
            st.plotly_chart(fig_s, use_container_width=True)

            m1, m2, m3 = st.columns(3)
            sev_rows = {str(r["severity_group"]): r for _, r in bs.iterrows()}
            for col_w, sev_lbl in zip([m1, m2, m3], _ORDER):
                row = sev_rows.get(sev_lbl)
                if row is not None:
                    delta_val = round(float(row["avg_current"]) - float(row["avg_baseline"]), 2)
                    with col_w:
                        st.metric(sev_lbl, f"{row['avg_current']:.2f}", delta=f"+{delta_val:.2f} pts")

    # ── Insights ──────────────────────────────────────────────────────────
    _section("Key Insights")
    for ins in insights:
        st.markdown(
            f"<div style='background:linear-gradient(135deg,#EBF5FB 0%,#D6EAF8 100%);"
            f"border-left:4px solid {_BLUE};border-radius:0 12px 12px 0;"
            f"padding:0.85rem 1.2rem;margin-bottom:0.7rem;"
            f"font-size:0.95rem;color:{_DARK};line-height:1.6;'>{ins}</div>",
            unsafe_allow_html=True,
        )

    # ── AI Summary ────────────────────────────────────────────────────────
    _section("AI Executive Summary")
    st.markdown(
        "<p style='color:#7F8C8D;font-size:0.88rem;margin-bottom:0.8rem;'>"
        "Generated from aggregated, anonymised population data only.</p>",
        unsafe_allow_html=True,
    )

    api_key = st.session_state.get("api_key", "")
    if st.button("Generate AI summary", type="primary"):
        with st.spinner("Generating summary..."):
            summary = get_ai_summary(ov, imp, api_key=api_key)
        st.markdown(
            f"<div style='background:linear-gradient(135deg,{_DARK} 0%,{_BLUE} 100%);"
            f"color:white;border-radius:14px;padding:1.5rem 2rem;line-height:1.85;font-size:0.95rem;'>"
            f"<div style='background:rgba(255,255,255,0.15);display:inline-block;"
            f"border-radius:20px;padding:0.2rem 0.9rem;font-size:0.72rem;"
            f"font-weight:700;letter-spacing:0.8px;margin-bottom:0.9rem;'>AI SUMMARY</div>"
            f"<div>{summary}</div></div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"<div style='background:#F4F6F9;border:2px dashed #BDC3C7;border-radius:14px;"
            f"padding:1.5rem;text-align:center;color:#AEB6BF;'>"
            f"Click <b>Generate AI summary</b> above to create an executive brief.</div>",
            unsafe_allow_html=True,
        )
