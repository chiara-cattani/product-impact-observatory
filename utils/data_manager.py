import json
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

PRODUCTS = [
    "Activia Probiotic Yogurt",
    "Actimel Daily Probiotic",
    "Nutricia Fortimel",
]
GOALS = [
    "Improve digestion",
    "Boost energy",
    "Reduce bloating",
    "Strengthen immunity",
]
SYMPTOMS = [
    "Bloating",
    "Abdominal discomfort",
    "Fatigue",
    "Irregular digestion",
    "Low energy",
]

DATA_DIR = Path(__file__).parent.parent / "data"
SIM_FILE = DATA_DIR / "simulated_data.csv"
CHECKINS_FILE = DATA_DIR / "user_checkins.json"


def init_session_state():
    defaults = {
        "onboarded": False,
        "user_name": "",
        "user_product": PRODUCTS[0],
        "user_goal": GOALS[0],
        "user_id": f"live_{date.today().isoformat()}",
        "checkins": [],
        "today_submitted": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def save_checkin(entry: dict):
    st.session_state.checkins.append(entry)
    try:
        DATA_DIR.mkdir(exist_ok=True)
        existing = []
        if CHECKINS_FILE.exists():
            existing = json.loads(CHECKINS_FILE.read_text())
        existing.append({k: str(v) if not isinstance(v, (str, int, float, bool, list)) else v
                         for k, v in entry.items()})
        CHECKINS_FILE.write_text(json.dumps(existing, indent=2, default=str))
    except Exception:
        pass


def get_user_df() -> pd.DataFrame:
    if not st.session_state.checkins:
        return pd.DataFrame()
    return pd.DataFrame(st.session_state.checkins)


def get_sim_df() -> pd.DataFrame:
    DATA_DIR.mkdir(exist_ok=True)
    if SIM_FILE.exists():
        return pd.read_csv(SIM_FILE)
    df = _generate_sim_data()
    df.to_csv(SIM_FILE, index=False)
    return df


def _sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-6.0 * (x - 0.5)))


def _generate_sim_data() -> pd.DataFrame:
    rng = np.random.default_rng(42)
    today = date.today()
    start = today - timedelta(days=29)

    product_dist = [PRODUCTS[0]] * 11 + [PRODUCTS[1]] * 9 + [PRODUCTS[2]] * 5
    goal_dist = [GOALS[0]] * 10 + [GOALS[1]] * 8 + [GOALS[2]] * 4 + [GOALS[3]] * 3

    records = []
    for i in range(25):
        uid = f"U{i + 1:03d}"
        product = product_dist[i]
        goal = goal_dist[i]
        baseline_dig = rng.uniform(1.4, 2.8)
        baseline_eng = rng.uniform(1.6, 2.9)
        max_imp_dig = rng.uniform(1.2, 2.1)
        max_imp_eng = rng.uniform(0.9, 1.7)
        compliance = rng.uniform(0.70, 0.96)

        for day in range(30):
            if rng.random() > compliance:
                continue
            current_date = start + timedelta(days=day)
            progress = day / 29.0
            imp = float(_sigmoid(np.array([progress]))[0] - _sigmoid(np.array([0.0]))[0])

            dig = float(np.clip(baseline_dig + imp * max_imp_dig + rng.normal(0, 0.35), 1.0, 5.0))
            eng = float(np.clip(baseline_eng + imp * max_imp_eng + rng.normal(0, 0.35), 1.0, 5.0))

            syms = []
            if baseline_dig < 2.2 and day < 18:
                if rng.random() > 0.45:
                    syms.append("Bloating")
                if rng.random() > 0.55:
                    syms.append("Abdominal discomfort")
            if baseline_eng < 2.2 and day < 20:
                if rng.random() > 0.5:
                    syms.append("Fatigue")

            records.append({
                "user_id": uid,
                "user_name": f"Participant {i + 1}",
                "product": product,
                "goal": goal,
                "date": current_date.isoformat(),
                "day_number": day + 1,
                "digestion_score": round(dig, 2),
                "energy_score": round(eng, 2),
                "symptoms": "|".join(syms),
                "product_taken": bool(rng.random() > 0.08),
                "baseline_digestion": round(baseline_dig, 2),
                "baseline_energy": round(baseline_eng, 2),
            })

    return pd.DataFrame(records)
