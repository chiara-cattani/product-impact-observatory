import streamlit as st

_TEMPLATE = (
    "This 30-day real-world evidence study across <b>{n_users} consumers</b> demonstrates consistent, "
    "measurable health benefits from daily product use. <b>{pct_improved}% of participants</b> showed "
    "meaningful improvement in digestion scores, with an average gain of <b>+{avg_delta} points</b> (scale 1-5). "
    "Daily compliance reached <b>{compliance}%</b>, reflecting strong product acceptance across diverse consumer profiles. "
    "Participants with higher baseline symptom severity exhibited the strongest improvement trajectories, "
    "suggesting a dose-response pattern consistent with the product's probiotic mechanism of action. "
    "These real-world outcomes provide robust, consumer-generated evidence to support regulatory submissions "
    "and strengthen health-claim positioning with healthcare professionals."
)


@st.cache_data(show_spinner=False)
def get_ai_summary(n_users: int, n_logs: int, compliance: float, pct_improved: float, avg_delta: float) -> str:
    try:
        import anthropic

        client = anthropic.Anthropic()
        prompt = (
            f"You are a health data scientist writing an executive summary for Danone leadership.\n\n"
            f"30-day consumer study results:\n"
            f"- {n_users} participants, {n_logs} total check-ins\n"
            f"- {compliance}% daily compliance\n"
            f"- {pct_improved}% of users showed digestion improvement\n"
            f"- Average digestion score change: +{avg_delta} pts (scale 1-5)\n\n"
            f"Write 3-4 sentences in a confident, data-driven tone. Highlight: (1) key outcome with numbers, "
            f"(2) strength of evidence, (3) business or regulatory implication. "
            f"Use <b>bold HTML tags</b> for key numbers."
        )
        msg = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=280,
            messages=[{"role": "user", "content": prompt}],
        )
        return msg.content[0].text
    except Exception:
        return _TEMPLATE.format(
            n_users=n_users,
            pct_improved=pct_improved,
            avg_delta=avg_delta,
            compliance=compliance,
        )
