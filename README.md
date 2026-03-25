Personal project with AI-generated data - example on a company

# Product Impact Observatory (PIO)

A Streamlit prototype demonstrating how a company could collect real-world consumer data and generate continuous evidence on product health impact.

---

## What it does

| Component | Description |
|---|---|
| **Consumer App** | Mobile-friendly daily check-in: digestion score, energy, symptoms |
| **Analytics Dashboard** | Live evidence generation: trends, before/after, segmentation, AI summary |

---

## Quick start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run
streamlit run app.py
```

The app opens at `http://localhost:8501`.

---

## Project structure

```
product_impact_observatory/
├── app.py                   # Main entry point
├── requirements.txt
├── README.md
│
├── components/
│   ├── onboarding.py        # Welcome + profile setup
│   ├── checkin.py           # Daily check-in form + personal history
│   └── dashboard.py         # Analytics dashboard
│
├── data/
│   ├── simulated_data.csv   # Auto-generated on first run (25 users × 30 days)
│   └── user_checkins.json   # Persisted real check-ins
│
└── utils/
    ├── data_manager.py      # Session state + data generation
    ├── analytics.py         # compute_trends / compute_improvement / compute_segments
    └── llm_summary.py       # AI summary (Anthropic Claude or template fallback)
```

---

## Using the AI summary

The dashboard includes an AI-generated executive summary.

- **Without API key**: uses a data-driven template (always works)
- **With API key**: calls Claude claude-sonnet-4-6 on aggregated data only

Add your key in the sidebar under **AI summary settings**.

To use programmatically:
```python
import anthropic
# set ANTHROPIC_API_KEY env var, or pass key via sidebar
```

---

## Deploying to Streamlit Cloud

1. Push this folder to a GitHub repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect the repo, set main file to `app.py`
4. (Optional) Add `ANTHROPIC_API_KEY` as a secret in the Streamlit Cloud settings

---

## Demo mode

The dashboard loads 25 pre-generated participants × 30 days automatically.
Toggle **Demo mode** off in the sidebar to use only real check-in data.

---

## Key analytics functions

| Function | Location | Description |
|---|---|---|
| `compute_trends()` | `utils/analytics.py` | Daily avg scores over time |
| `compute_improvement()` | `utils/analytics.py` | Before/after per user, distribution |
| `compute_segments()` | `utils/analytics.py` | By product and severity group |
| `generate_insights()` | `utils/analytics.py` | Auto-generated text insights |
| `get_ai_summary()` | `utils/llm_summary.py` | LLM executive brief |
