import numpy as np
import pandas as pd


def compute_overview(df: pd.DataFrame) -> dict:
    n_users = df["user_id"].nunique()
    n_logs = len(df)
    compliance = n_logs / (n_users * 30) * 100

    deltas = []
    for _, grp in df.groupby("user_id"):
        grp = grp.sort_values("day_number")
        if len(grp) >= 5:
            base = grp.head(3)["digestion_score"].mean()
            curr = grp.tail(7)["digestion_score"].mean()
            deltas.append(curr - base)

    return {
        "n_users": n_users,
        "n_logs": n_logs,
        "compliance_pct": round(compliance, 1),
        "avg_improvement": round(float(np.mean(deltas)), 2) if deltas else 0.0,
        "pct_improved": round(sum(1 for d in deltas if d > 0.3) / max(len(deltas), 1) * 100, 1),
    }


def compute_trends(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    t = (
        df.groupby("date")
        .agg(
            avg_digestion=("digestion_score", "mean"),
            avg_energy=("energy_score", "mean"),
            n_logs=("user_id", "count"),
        )
        .reset_index()
        .sort_values("date")
    )
    t["dig_smooth"] = t["avg_digestion"].rolling(3, min_periods=1).mean()
    t["eng_smooth"] = t["avg_energy"].rolling(3, min_periods=1).mean()
    return t


def compute_improvement(df: pd.DataFrame) -> dict:
    deltas = []
    for _, grp in df.groupby("user_id"):
        grp = grp.sort_values("day_number")
        if len(grp) >= 5:
            base = grp.head(3)["digestion_score"].mean()
            curr = grp.tail(7)["digestion_score"].mean()
            deltas.append(curr - base)

    ba_rows = []
    for prod, grp in df.groupby("product"):
        early = grp[grp["day_number"] <= 5]["digestion_score"].mean()
        late = grp[grp["day_number"] >= 25]["digestion_score"].mean()
        ba_rows.append({
            "product": prod,
            "Before (Day 1-5)": round(early, 2),
            "After (Day 25-30)": round(late, 2),
        })

    return {
        "avg_delta": round(float(np.mean(deltas)), 2) if deltas else 0.0,
        "pct_improved": round(sum(1 for d in deltas if d > 0.3) / max(len(deltas), 1) * 100, 1),
        "deltas": deltas,
        "before_after": pd.DataFrame(ba_rows),
    }


def compute_segments(df: pd.DataFrame) -> dict:
    by_product = (
        df.groupby("product")
        .agg(
            n_users=("user_id", "nunique"),
            avg_digestion=("digestion_score", "mean"),
            avg_energy=("energy_score", "mean"),
        )
        .reset_index()
    )
    by_product["avg_digestion"] = by_product["avg_digestion"].round(2)
    by_product["avg_energy"] = by_product["avg_energy"].round(2)

    baselines = df.groupby("user_id")["baseline_digestion"].first().reset_index()
    baselines["severity"] = pd.cut(
        baselines["baseline_digestion"],
        bins=[0, 2.0, 2.7, 5],
        labels=["High severity (<=2.0)", "Moderate (2.0-2.7)", "Low severity (>2.7)"],
    )
    merged = df.merge(baselines[["user_id", "severity"]], on="user_id")
    by_sev = (
        merged.groupby("severity", observed=True)
        .agg(n_users=("user_id", "nunique"), avg_digestion=("digestion_score", "mean"))
        .reset_index()
    )
    by_sev["avg_digestion"] = by_sev["avg_digestion"].round(2)

    return {"by_product": by_product, "by_severity": by_sev}


def compute_symptom_freq(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, r in df.iterrows():
        syms_val = r.get("symptoms", "")
        if isinstance(syms_val, str) and syms_val:
            week = min(int((r["day_number"] - 1) // 7) + 1, 4)
            for s in syms_val.split("|"):
                if s:
                    rows.append({"symptom": s, "week": f"Week {week}"})
    if not rows:
        return pd.DataFrame(columns=["symptom", "week", "count"])
    sf = pd.DataFrame(rows)
    return sf.groupby(["symptom", "week"]).size().reset_index(name="count")


def generate_insights(df: pd.DataFrame) -> list:
    ov = compute_overview(df)
    imp = compute_improvement(df)
    trends = compute_trends(df)
    insights = []

    if imp["pct_improved"] > 60:
        insights.append(
            f"<b>{imp['pct_improved']:.0f}%</b> of participants show measurable digestion improvement over 30 days."
        )
    if imp["avg_delta"] > 0.4:
        insights.append(
            f"Average digestion score improved by <b>+{imp['avg_delta']:.1f} pts</b> on a 1-5 scale."
        )
    if len(trends) > 10:
        w1 = trends.head(7)["dig_smooth"].mean()
        w4 = trends.tail(7)["dig_smooth"].mean()
        if w4 - w1 > 0.3:
            insights.append(
                f"Population-level scores rose from <b>{w1:.1f}</b> (Week 1) to <b>{w4:.1f}</b> (Week 4)."
            )

    segs = compute_segments(df)
    sev = segs["by_severity"]
    if len(sev) >= 2:
        high = sev[sev["severity"].astype(str).str.startswith("High")]
        if not high.empty:
            insights.append(
                "Participants with <b>high baseline severity</b> show the strongest relative improvement trajectory."
            )

    if ov["compliance_pct"] > 75:
        insights.append(
            f"<b>{ov['compliance_pct']:.0f}%</b> average daily compliance confirms strong user engagement with the product."
        )

    return insights
