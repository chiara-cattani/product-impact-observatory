"""
Core analytics functions for the Product Impact Observatory.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


# ── Overview ───────────────────────────────────────────────────────────────────

def compute_overview(df: pd.DataFrame) -> dict:
    n_users   = int(df["user_id"].nunique())
    n_logs    = int(len(df))
    n_days    = int(df["day_number"].max()) if n_users else 1
    compliance = round(n_logs / max(n_users * n_days, 1) * 100, 1)

    improvements = _per_user_delta(df, "digestion_score")
    avg_delta    = round(float(np.mean(list(improvements.values()))), 2) if improvements else 0.0
    pct_improved = round(
        sum(1 for v in improvements.values() if v > 0.3) / max(len(improvements), 1) * 100, 1
    )
    return {
        "total_users":    n_users,
        "total_logs":     n_logs,
        "compliance_pct": compliance,
        "avg_improvement": avg_delta,
        "pct_improved":   pct_improved,
    }


# ── Trends ─────────────────────────────────────────────────────────────────────

def compute_trends(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    trends = (
        df.groupby("date")
        .agg(
            avg_digestion=("digestion_score", "mean"),
            avg_energy=("energy_score", "mean"),
            daily_logs=("user_id", "count"),
        )
        .reset_index()
        .sort_values("date")
    )
    # 3-day rolling average for smoother lines
    trends["dig_smooth"]  = trends["avg_digestion"].rolling(3, min_periods=1).mean()
    trends["eng_smooth"]  = trends["avg_energy"].rolling(3, min_periods=1).mean()
    return trends


def compute_day_trends(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate by study day (1-30) across all users."""
    trends = (
        df.groupby("day_number")
        .agg(
            avg_digestion=("digestion_score", "mean"),
            avg_energy=("energy_score", "mean"),
            n_users=("user_id", "nunique"),
        )
        .reset_index()
        .sort_values("day_number")
    )
    trends["dig_smooth"] = trends["avg_digestion"].rolling(3, min_periods=1).mean()
    trends["eng_smooth"] = trends["avg_energy"].rolling(3, min_periods=1).mean()
    return trends


# ── Improvement ────────────────────────────────────────────────────────────────

def compute_improvement(df: pd.DataFrame) -> dict:
    per_user   = {}
    baselines  = []
    currents   = []

    for uid, grp in df.groupby("user_id"):
        grp = grp.sort_values("day_number")
        if len(grp) < 4:
            continue
        baseline = float(grp.head(3)["digestion_score"].mean())
        current  = float(grp.tail(7)["digestion_score"].mean())
        delta    = current - baseline
        per_user[uid] = {
            "baseline": round(baseline, 2),
            "current":  round(current, 2),
            "delta":    round(delta, 2),
            "improved": delta > 0.3,
        }
        baselines.append(baseline)
        currents.append(current)

    if not per_user:
        return {"per_user": {}, "avg_delta": 0.0, "pct_improved": 0.0,
                "avg_baseline": 0.0, "avg_current": 0.0, "distribution": {}}

    deltas      = [v["delta"] for v in per_user.values()]
    pct_improved = round(
        sum(1 for v in per_user.values() if v["improved"]) / len(per_user) * 100, 1
    )

    bins   = pd.cut(deltas, bins=[-3, -0.3, 0.3, 1.0, 3],
                    labels=["Declined", "No change", "Improved", "Strongly improved"])
    dist   = {str(k): int(v) for k, v in bins.value_counts().items()}

    return {
        "per_user":     per_user,
        "avg_delta":    round(float(np.mean(deltas)), 2),
        "pct_improved": pct_improved,
        "avg_baseline": round(float(np.mean(baselines)), 2),
        "avg_current":  round(float(np.mean(currents)), 2),
        "distribution": dist,
    }


# ── Segmentation ───────────────────────────────────────────────────────────────

def compute_segments(df: pd.DataFrame) -> dict:
    # By product
    by_product = (
        df.groupby("product")
        .agg(
            users       =("user_id",        "nunique"),
            avg_dig     =("digestion_score", "mean"),
            avg_eng     =("energy_score",    "mean"),
            compliance  =("product_taken",   "mean"),
        )
        .reset_index()
        .rename(columns={"avg_dig": "avg_digestion", "avg_eng": "avg_energy"})
    )
    by_product["avg_digestion"] = by_product["avg_digestion"].round(2)
    by_product["avg_energy"]    = by_product["avg_energy"].round(2)
    by_product["compliance"]    = (by_product["compliance"] * 100).round(1)

    # By baseline severity
    user_base = df.groupby("user_id")["baseline_digestion"].first().reset_index()
    user_base["severity_group"] = pd.cut(
        user_base["baseline_digestion"],
        bins=[0, 2.0, 2.8, 5],
        labels=["High severity", "Moderate", "Low severity"],
    )
    df_sev = df.merge(user_base[["user_id", "severity_group"]], on="user_id")

    # Compute delta per user then aggregate by severity
    deltas = []
    for uid, grp in df_sev.groupby("user_id"):
        grp = grp.sort_values("day_number")
        if len(grp) < 4:
            continue
        sev   = grp["severity_group"].iloc[0]
        base  = float(grp.head(3)["digestion_score"].mean())
        curr  = float(grp.tail(7)["digestion_score"].mean())
        deltas.append({"severity_group": sev, "delta": curr - base,
                       "baseline": base, "current": curr})
    sev_df = pd.DataFrame(deltas)

    if not sev_df.empty:
        by_severity = (
            sev_df.groupby("severity_group", observed=True)
            .agg(n_users=("delta", "count"),
                 avg_delta=("delta", "mean"),
                 avg_baseline=("baseline", "mean"),
                 avg_current=("current", "mean"))
            .reset_index()
        )
        by_severity["avg_delta"]    = by_severity["avg_delta"].round(2)
        by_severity["avg_baseline"] = by_severity["avg_baseline"].round(2)
        by_severity["avg_current"]  = by_severity["avg_current"].round(2)
    else:
        by_severity = pd.DataFrame()

    return {"by_product": by_product, "by_severity": by_severity}


# ── Symptom frequency ──────────────────────────────────────────────────────────

def compute_symptom_freq(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, row in df.iterrows():
        if not row["symptoms"] or not isinstance(row["symptoms"], str):
            continue
        week = min(int((row["day_number"] - 1) // 7) + 1, 4)
        for sym in row["symptoms"].split("|"):
            if sym.strip():
                rows.append({"symptom": sym.strip(), "week": f"Week {week}"})

    if not rows:
        return pd.DataFrame(columns=["symptom", "week", "count"])

    sym_df = pd.DataFrame(rows)
    return (
        sym_df.groupby(["symptom", "week"])
        .size()
        .reset_index(name="count")
        .sort_values(["week", "symptom"])
    )


# ── Insight generation ─────────────────────────────────────────────────────────

def generate_insights(df: pd.DataFrame) -> list[str]:
    ov   = compute_overview(df)
    imp  = compute_improvement(df)
    segs = compute_segments(df)
    insights: list[str] = []

    if imp["pct_improved"] >= 60:
        insights.append(
            f"{imp['pct_improved']:.0f}% of participants show measurable digestion improvement "
            f"over the study period."
        )

    if imp["avg_delta"] >= 0.4:
        insights.append(
            f"Average digestion score improved by **+{imp['avg_delta']:.1f} points** "
            f"(scale 1–5) from baseline {imp['avg_baseline']:.1f} to {imp['avg_current']:.1f}."
        )

    # Severity-response relationship
    sev = segs["by_severity"]
    if not sev.empty and "High severity" in sev["severity_group"].values:
        hs = sev[sev["severity_group"] == "High severity"]["avg_delta"].values
        ls = sev[sev["severity_group"] == "Low severity"]["avg_delta"].values if "Low severity" in sev["severity_group"].values else [0]
        if len(hs) and float(hs[0]) > float(ls[0]):
            insights.append(
                f"Dose-response pattern detected: high-severity participants improved by "
                f"**+{float(hs[0]):.1f} pts**, vs **+{float(ls[0]):.1f} pts** in low-severity group."
            )

    if ov["compliance_pct"] >= 80:
        insights.append(
            f"High user compliance (**{ov['compliance_pct']:.0f}%**) confirms strong product "
            f"acceptance and daily habit formation."
        )

    # Time-based trend
    trends = compute_day_trends(df)
    if len(trends) >= 14:
        w1 = float(trends[trends["day_number"] <= 7]["avg_digestion"].mean())
        w4 = float(trends[trends["day_number"] >= 22]["avg_digestion"].mean())
        if w4 - w1 >= 0.3:
            insights.append(
                f"Population-level digestion scores rose from **{w1:.1f}** (Week 1) "
                f"to **{w4:.1f}** (Week 4), suggesting sustained product efficacy."
            )

    return insights


# ── Helpers ────────────────────────────────────────────────────────────────────

def _per_user_delta(df: pd.DataFrame, col: str) -> dict[str, float]:
    result = {}
    for uid, grp in df.groupby("user_id"):
        grp = grp.sort_values("day_number")
        if len(grp) < 4:
            continue
        result[uid] = float(grp.tail(7)[col].mean()) - float(grp.head(3)[col].mean())
    return result
