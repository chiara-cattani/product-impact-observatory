"""
Data management: session state initialisation and simulated data generation.
"""

import json
import numpy as np
import pandas as pd
import streamlit as st
from datetime import date, timedelta
from pathlib import Path

# ── Constants ──────────────────────────────────────────────────────────────────

PRODUCTS = [
    "Activia Probiotic Yogurt",
    "Actimel Daily Probiotic",
    "Nutricia Fortijuice",
]

GOALS = [
    "Improve digestion",
    "Boost energy",
    "Strengthen immunity",
    "Reduce bloating",
]

SYMPTOMS = [
    "Bloating",
    "Abdominal discomfort",
    "Fatigue",
    "Irregular digestion",
    "Low energy",
    "Nausea",
]

DATA_DIR   = Path(__file__).parent.parent / "data"
SIM_FILE   = DATA_DIR / "simulated_data.csv"
USER_FILE  = DATA_DIR / "user_checkins.json"


# ── Session state ──────────────────────────────────────────────────────────────

def init_session_state() -> None:
    defaults = {
        "onboarded":        False,
        "user_name":        "",
        "user_product":     PRODUCTS[0],
        "user_goal":        GOALS[0],
        "current_page":     "consumer",
        "checkins":         [],
        "today_submitted":  False,
        "demo_mode":        True,
        "api_key":          "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ── Checkin persistence ────────────────────────────────────────────────────────

def save_checkin(checkin: dict) -> None:
    st.session_state.checkins.append(checkin)
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        existing: list = []
        if USER_FILE.exists():
            existing = json.loads(USER_FILE.read_text(encoding="utf-8"))
        existing.append({**checkin, "date": str(checkin["date"])})
        USER_FILE.write_text(json.dumps(existing, indent=2, default=str), encoding="utf-8")
    except Exception:
        pass


def load_checkins() -> list:
    if USER_FILE.exists():
        try:
            return json.loads(USER_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return []


# ── Simulated data ─────────────────────────────────────────────────────────────

def get_simulated_data() -> pd.DataFrame:
    if SIM_FILE.exists():
        try:
            df = pd.read_csv(SIM_FILE)
            df["date"] = pd.to_datetime(df["date"])
            return df
        except Exception:
            pass
    return _generate_and_save()


def _generate_and_save() -> pd.DataFrame:
    df = _generate_simulated_data()
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        df.to_csv(SIM_FILE, index=False)
    except Exception:
        pass
    return df


def _generate_simulated_data(n_users: int = 25, n_days: int = 30) -> pd.DataFrame:
    rng = np.random.default_rng(42)
    start_date = date.today() - timedelta(days=n_days - 1)

    user_profiles = []
    for i in range(1, n_users + 1):
        product = PRODUCTS[i % len(PRODUCTS)]
        goal    = GOALS[i % len(GOALS)]
        user_profiles.append({
            "user_id":          f"U{i:03d}",
            "user_name":        f"Participant {i:02d}",
            "product":          product,
            "goal":             goal,
            "baseline_dig":     float(rng.uniform(1.5, 3.0)),
            "baseline_eng":     float(rng.uniform(1.5, 3.0)),
            "max_improvement":  float(rng.uniform(1.2, 2.2)),
            "compliance":       float(rng.uniform(0.72, 0.97)),
        })

    records = []
    for u in user_profiles:
        for day in range(n_days):
            if rng.random() > u["compliance"]:
                continue

            progress    = (day / (n_days - 1)) ** 0.65
            improvement = progress * u["max_improvement"]

            dig = float(np.clip(
                u["baseline_dig"] + improvement + rng.normal(0, 0.35),
                1.0, 5.0,
            ))
            eng = float(np.clip(
                u["baseline_eng"] + improvement * 0.85 + rng.normal(0, 0.35),
                1.0, 5.0,
            ))

            # Symptoms more frequent early, fade as scores improve
            symptom_list = []
            if day < 15:
                symp_prob = max(0, (3.0 - dig) / 4.0)
                for sym in ["Bloating", "Abdominal discomfort", "Fatigue", "Irregular digestion"]:
                    if rng.random() < symp_prob:
                        symptom_list.append(sym)

            records.append({
                "user_id":            u["user_id"],
                "user_name":          u["user_name"],
                "product":            u["product"],
                "goal":               u["goal"],
                "date":               (start_date + timedelta(days=day)).isoformat(),
                "day_number":         day + 1,
                "digestion_score":    round(dig, 2),
                "energy_score":       round(eng, 2),
                "symptoms":           "|".join(symptom_list),
                "product_taken":      bool(rng.random() > 0.08),
                "baseline_digestion": round(u["baseline_dig"], 2),
                "baseline_energy":    round(u["baseline_eng"], 2),
            })

    df = pd.DataFrame(records)
    df["date"] = pd.to_datetime(df["date"])
    return df
