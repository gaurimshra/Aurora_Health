from datetime import date, datetime, timedelta


def _parse_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def _average(values: list[int]) -> int | None:
    if not values:
        return None
    return round(sum(values) / len(values))


def analyze_cycle(period_logs: list[dict]) -> dict:
    sorted_logs = sorted(period_logs, key=lambda item: item["start_date"])
    if not sorted_logs:
        return {
            "average_cycle_length": None,
            "average_period_length": None,
            "next_period_start": None,
            "predicted_phase": "insufficient-data",
            "irregularity_score": "unknown",
        }

    cycle_lengths: list[int] = []
    period_lengths: list[int] = []
    for current, following in zip(sorted_logs, sorted_logs[1:]):
        cycle_lengths.append(
            (_parse_date(following["start_date"]) - _parse_date(current["start_date"])).days
        )

    for log in sorted_logs:
        period_lengths.append(
            (_parse_date(log["end_date"]) - _parse_date(log["start_date"])).days + 1
        )

    avg_cycle = _average(cycle_lengths)
    avg_period = _average(period_lengths)
    last_start = _parse_date(sorted_logs[-1]["start_date"])
    next_start = (last_start + timedelta(days=avg_cycle)).isoformat() if avg_cycle else None

    irregularity = "stable"
    if cycle_lengths:
        spread = max(cycle_lengths) - min(cycle_lengths)
        if spread >= 10:
            irregularity = "high"
        elif spread >= 5:
            irregularity = "moderate"

    today = date.today()
    days_since_last = (today - last_start).days
    predicted_phase = "follicular"
    if avg_cycle:
        if days_since_last <= (avg_period or 5):
            predicted_phase = "menstrual"
        elif days_since_last <= max(avg_cycle - 14, 7):
            predicted_phase = "follicular"
        elif days_since_last <= max(avg_cycle - 11, 10):
            predicted_phase = "ovulation-window"
        else:
            predicted_phase = "luteal"

    return {
        "average_cycle_length": avg_cycle,
        "average_period_length": avg_period,
        "next_period_start": next_start,
        "predicted_phase": predicted_phase,
        "irregularity_score": irregularity,
    }
