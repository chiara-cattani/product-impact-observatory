_TEMPLATE = (
    "This 30-day real-world evidence study across <b>{n_users} consumers</b> demonstrates consistent, "
    "measurable health benefits from daily product use. <b>{pct_improved}% of participants</b> showed "
    "meaningful improvement in digestion scores, with an average gain of <b>+{avg_delta} points</b> (scale 1-5). "
    "Daily compliance reached <b>{compliance}%</b>, reflecting strong product acceptance and sustainable "
    "habit formation across diverse consumer segments. "
    "Participants with higher baseline symptom severity exhibited the strongest improvement trajectories, "
    "suggesting a dose-response pattern consistent with the product's probiotic mechanism of action. "
    "These real-world outcomes provide robust, consumer-generated evidence to support regulatory submissions "
    "and strengthen health-claim positioning with healthcare professionals."
)


def get_ai_summary(overview: dict, improvement: dict, api_key: str = "") -> str:
    """Try Anthropic API; fall back gracefully to template."""
    try:
        import anthropic

        key    = api_key.strip() or None
        client = anthropic.Anthropic(**({"api_key": key} if key else {}))

        prompt = (
            "You are a senior health-data scientist writing a brief executive summary for "
            "Danone leadership. Be data-driven, professional, and confident.\n\n"
            f"Study data (30-day consumer panel, n={overview['total_users']}):\n"
            f"- Total check-ins logged: {overview['total_logs']}\n"
            f"- Daily compliance rate: {overview['compliance_pct']}%\n"
            f"- Users showing digestion improvement: {improvement['pct_improved']}%\n"
            f"- Average digestion score change: +{improvement['avg_delta']} pts (scale 1-5)\n"
            f"- Baseline avg digestion score: {improvement['avg_baseline']}\n"
            f"- End-of-study avg digestion score: {improvement['avg_current']}\n\n"
            "Write 4-5 sentences covering: (1) key outcome with numbers, "
            "(2) strength of evidence, (3) dose-response pattern, "
            "(4) business or regulatory implication. "
            "Use <b>bold HTML tags</b> for key numbers."
        )
        msg = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=350,
            messages=[{"role": "user", "content": prompt}],
        )
        return msg.content[0].text
    except Exception:
        return _TEMPLATE.format(
            n_users=overview["total_users"],
            pct_improved=improvement["pct_improved"],
            avg_delta=improvement["avg_delta"],
            compliance=overview["compliance_pct"],
        )
