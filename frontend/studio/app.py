import json
from datetime import date
from pathlib import Path

import httpx
import pandas as pd
import streamlit as st

try:
    import plotly.graph_objects as go
except ModuleNotFoundError:
    go = None

try:
    from streamlit_lottie import st_lottie
except ModuleNotFoundError:
    st_lottie = None


DEFAULT_API_URL = "http://127.0.0.1:8000"
SECTION_OPTIONS = [
    "Home",
    "Profile",
    "Plans",
    "Women's Health",
    "Daily Tracking",
    "Progress",
    "Memory & History",
    "Weekly Report",
    "Aurora Coach",
]

ASSET_DIR = Path(__file__).resolve().parent / "assets"
AI_AVATAR_PATH = ASSET_DIR / "aurora.png"
AVATAR_FALLBACK_URL = "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?auto=format&fit=crop&w=400&q=80"
LOTTIE_COACH_URL = "https://assets7.lottiefiles.com/packages/lf20_jcikwtux.json"


st.set_page_config(page_title="Aurora Health Studio", page_icon="A", layout="wide", initial_sidebar_state="expanded")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Fraunces:opsz,wght@9..144,600;9..144,700&display=swap');

    .stApp {
        background:
            radial-gradient(circle at 0% 0%, rgba(255, 209, 173, 0.72), transparent 22%),
            radial-gradient(circle at 100% 0%, rgba(153, 215, 205, 0.50), transparent 24%),
            radial-gradient(circle at 50% 100%, rgba(255, 224, 239, 0.58), transparent 26%),
            linear-gradient(155deg, #fff7f1 0%, #f7fbff 42%, #fdf3f9 100%);
        color: #203148;
        font-family: "Manrope", sans-serif;
    }
    .stApp [data-testid="stSidebar"] {
        background:
            linear-gradient(180deg, rgba(21, 38, 63, 0.98), rgba(29, 61, 79, 0.96));
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }
    .stApp [data-testid="stSidebar"] * {
        color: #f7fbff;
    }
    .stApp [data-testid="stSidebar"] .stTextInput input {
        background: rgba(255, 255, 255, 0.08);
        color: white;
    }
    .stApp h1, .stApp h2, .stApp h3 {
        color: #15314f;
        letter-spacing: -0.02em;
    }
    .stApp h1, .hero h1, .section-hero h2 {
        font-family: "Fraunces", serif;
    }
    .hero, .mini-card, .panel, .section-hero, .feature-card {
        border: 1px solid rgba(36, 48, 75, 0.08);
        box-shadow: 0 16px 40px rgba(36, 48, 75, 0.08);
    }
    .hero {
        background:
            radial-gradient(circle at top right, rgba(255, 211, 159, 0.24), transparent 24%),
            linear-gradient(135deg, rgba(19, 46, 77, 0.98), rgba(42, 100, 107, 0.94));
        color: white;
        border-radius: 30px;
        padding: 34px 36px;
        margin-bottom: 1.15rem;
    }
    .hero h1 {
        margin: 0;
        font-size: 2.7rem;
        line-height: 1.04;
    }
    .hero p {
        margin: 0.85rem 0 0 0;
        max-width: 920px;
        line-height: 1.55;
        color: rgba(255, 255, 255, 0.92);
    }
    .hero-grid {
        display: grid;
        grid-template-columns: 1.25fr 0.75fr;
        gap: 1rem;
        align-items: end;
    }
    .hero-side {
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 22px;
        padding: 18px;
        backdrop-filter: blur(14px);
    }
    .hero-side-title {
        text-transform: uppercase;
        letter-spacing: 0.12em;
        font-size: 0.74rem;
        color: rgba(255, 255, 255, 0.72);
        margin-bottom: 0.5rem;
    }
    .mini-card {
        background: rgba(255, 255, 255, 0.82);
        border-radius: 22px;
        padding: 18px 20px;
        min-height: 116px;
        backdrop-filter: blur(12px);
    }
    .mini-card .label {
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: #6c7586;
        font-size: 0.74rem;
        margin-bottom: 0.5rem;
    }
    .mini-card .value {
        color: #173957;
        font-size: 1.22rem;
        font-weight: 800;
        line-height: 1.25;
    }
    .panel {
        background: rgba(255, 255, 255, 0.80);
        border-radius: 24px;
        padding: 20px 22px;
        backdrop-filter: blur(12px);
    }
    .section-title {
        color: #21455f;
        font-size: 0.74rem;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        margin-bottom: 0.7rem;
    }
    .panel-body {
        color: #30445d;
        line-height: 1.65;
        font-size: 0.98rem;
    }
    .section-hero {
        background: linear-gradient(145deg, rgba(255,255,255,0.82), rgba(248, 252, 255, 0.72));
        border-radius: 28px;
        padding: 22px 24px;
        margin: 0.5rem 0 1rem 0;
    }
    .section-hero h2 {
        margin: 0;
        font-size: 2rem;
    }
    .section-hero p {
        margin: 0.7rem 0 0 0;
        max-width: 920px;
        color: #546579;
        line-height: 1.65;
    }
    .feature-card {
        background: rgba(255, 255, 255, 0.7);
        border-radius: 22px;
        padding: 18px 20px;
        min-height: 132px;
    }
    .feature-card-title {
        color: #173957;
        font-size: 1rem;
        font-weight: 800;
        margin-bottom: 0.4rem;
    }
    .feature-card-copy {
        color: #546579;
        line-height: 1.55;
        font-size: 0.95rem;
    }
    .mini-card, .panel, .feature-card {
        transition: transform 0.45s ease, box-shadow 0.45s ease;
    }
    .mini-card:hover, .panel:hover, .feature-card:hover {
        transform: translateY(-6px);
        box-shadow: 0 28px 50px rgba(36, 48, 75, 0.14);
    }
    .progress-hint {
        font-size: 0.85rem;
        color: #3a4a63;
        margin-top: 0.35rem;
    }
    .ai-avatar {
        width: 172px;
        border-radius: 28px;
        border: 6px solid rgba(255, 255, 255, 0.7);
        box-shadow: 0 18px 35px rgba(16, 35, 60, 0.28);
        animation: float 6s ease-in-out infinite;
    }
    .floating-card {
        background: rgba(255, 255, 255, 0.72);
        border-radius: 28px;
        padding: 18px 20px;
        border: 1px solid rgba(255, 255, 255, 0.5);
        box-shadow: 0 20px 60px rgba(16, 35, 60, 0.12);
        backdrop-filter: blur(16px);
    }
    .lottie-wrapper {
        border-radius: 30px;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.15);
        background: rgba(255, 255, 255, 0.05);
        padding: 12px;
        box-shadow: 0 18px 45px rgba(15, 31, 47, 0.2);
    }
    @keyframes float {
        0% {
            transform: translateY(0);
        }
        50% {
            transform: translateY(-10px);
        }
        100% {
            transform: translateY(0);
        }
    }
    .pill-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.55rem;
        margin-top: 1rem;
    }
    .pill {
        background: rgba(255, 255, 255, 0.16);
        border: 1px solid rgba(255, 255, 255, 0.18);
        border-radius: 999px;
        padding: 0.4rem 0.82rem;
        font-size: 0.84rem;
    }
    .status-strip {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 0.9rem;
        margin: 0.25rem 0 1.15rem 0;
    }
    .status-item {
        border-radius: 20px;
        padding: 16px 18px;
        background: rgba(255, 255, 255, 0.76);
        border: 1px solid rgba(36, 48, 75, 0.07);
        box-shadow: 0 12px 28px rgba(36, 48, 75, 0.06);
    }
    .status-kicker {
        text-transform: uppercase;
        letter-spacing: 0.14em;
        color: #728197;
        font-size: 0.7rem;
        margin-bottom: 0.5rem;
    }
    .status-value {
        color: #173957;
        font-size: 1.02rem;
        font-weight: 800;
    }
    @media (max-width: 900px) {
        .hero-grid, .status-strip {
            grid-template-columns: 1fr;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def get_headers() -> dict:
    token = st.session_state.get("auth_token")
    return {"Authorization": f"Bearer {token}"} if token else {}


def api_request(method: str, base_url: str, path: str, payload: dict | None = None, auth: bool = False) -> dict:
    headers = get_headers() if auth else {}
    with httpx.Client(timeout=45.0) as client:
        response = client.request(method, f"{base_url.rstrip('/')}{path}", json=payload, headers=headers)
        response.raise_for_status()
        return response.json()


def safe_api(
    method: str,
    api_url: str,
    path: str,
    payload: dict | None = None,
    auth: bool = False,
    show_errors: bool = True,
) -> dict | None:
    try:
        return api_request(method, api_url, path, payload, auth=auth)
    except httpx.HTTPStatusError as exc:
        if show_errors:
            message = exc.response.text if exc.response is not None else str(exc)
            st.error(f"Request failed: {message}")
    except Exception as exc:
        if show_errors:
            st.error(f"Backend error: {exc}")
    return None


def render_panel(title: str, body: str) -> None:
    st.markdown(
        f"""<div class="panel"><div class="section-title">{title}</div><div class="panel-body">{body}</div></div>""",
        unsafe_allow_html=True,
    )


def render_metric_card(label: str, value: str) -> None:
    st.markdown(
        f"""<div class="mini-card"><div class="label">{label}</div><div class="value">{value}</div></div>""",
        unsafe_allow_html=True,
    )


def render_section_hero(title: str, copy: str) -> None:
    st.markdown(
        f"""
        <div class="section-hero">
            <div class="section-title">Workspace</div>
            <h2>{title}</h2>
            <p>{copy}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_feature_card(title: str, copy: str) -> None:
    st.markdown(
        f"""
        <div class="feature-card">
            <div class="feature-card-title">{title}</div>
            <div class="feature-card-copy">{copy}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def ensure_asset_folder() -> None:
    ASSET_DIR.mkdir(exist_ok=True)


def load_lottie_url(url: str) -> dict | None:
    try:
        response = httpx.get(url, timeout=10.0)
        response.raise_for_status()
        return response.json()
    except Exception:
        return None


def render_ai_avatar() -> None:
    caption = "Aurora, your AI health coach avatar"
    src = AI_AVATAR_PATH.as_uri() if AI_AVATAR_PATH.exists() else AVATAR_FALLBACK_URL
    st.markdown(
        f"""<div class='floating-card'>
            <img src='{src}' class='ai-avatar' alt='Aurora avatar'/>
            <div class='progress-hint'>{caption}</div>
        </div>""",
        unsafe_allow_html=True,
    )


def init_state() -> None:
    defaults = {
        "auth_token": None,
        "auth_user": None,
        "plan_result": None,
        "coach_result": None,
        "streak_result": None,
        "memory_search_result": None,
        "selected_section": "Home",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def to_csv_bytes(rows: list[dict]) -> bytes:
    if not rows:
        return b""
    return pd.DataFrame(rows).to_csv(index=False).encode("utf-8")


def to_json_bytes(payload: dict | list) -> bytes:
    return json.dumps(payload, indent=2, ensure_ascii=True, default=str).encode("utf-8")


def normalize_table(rows: list[dict]) -> pd.DataFrame:
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows)


def render_export_buttons(history: dict, report: dict | None) -> None:
    package = {
        "history": history,
        "weekly_report": report or {},
        "exported_on": date.today().isoformat(),
    }
    st.download_button(
        "Download Full Health Data (JSON)",
        data=to_json_bytes(package),
        file_name="aurora_health_data.json",
        mime="application/json",
        use_container_width=True,
    )

    for label, key in [
        ("Workout CSV", "workout_logs"),
        ("Diet CSV", "diet_logs"),
        ("Progress CSV", "progress_logs"),
        ("Period CSV", "period_logs"),
        ("Memory CSV", "recent_memories"),
    ]:
        rows = history.get(key, [])
        if rows:
            st.download_button(
                f"Download {label}",
                data=to_csv_bytes(rows),
                file_name=f"{key}.csv",
                mime="text/csv",
                use_container_width=True,
            )


def render_history_block(title: str, rows: list[dict], csv_name: str, include_header: bool = True) -> None:
    if include_header:
        st.markdown(f"#### {title}")
    if not rows:
        st.caption("No data saved yet.")
        return
    frame = normalize_table(rows)
    st.dataframe(frame, use_container_width=True)
    st.download_button(
        f"Export {title} CSV",
        data=to_csv_bytes(rows),
        file_name=csv_name,
        mime="text/csv",
        use_container_width=True,
    )


def fetch_snapshot(api_url: str) -> dict:
    return {
        "profile": safe_api("GET", api_url, "/profile/me", auth=True, show_errors=False),
        "streak": safe_api("GET", api_url, "/streaks/me", auth=True, show_errors=False),
        "progress": safe_api("GET", api_url, "/progress/me", auth=True, show_errors=False),
        "women": safe_api("GET", api_url, "/women-health/dashboard", auth=True, show_errors=False),
        "history": safe_api("GET", api_url, "/tracking/history", auth=True, show_errors=False),
        "weekly_report": safe_api("GET", api_url, "/tracking/weekly-report", auth=True, show_errors=False),
    }


def sidebar_auth(api_url: str) -> None:
    st.subheader("Identity")
    if st.session_state.auth_user:
        st.success(f"{st.session_state.auth_user['name']} (@{st.session_state.auth_user.get('username', 'user')})")
        st.caption(st.session_state.auth_user["email"])
        if st.button("Refresh Account", use_container_width=True):
            me = safe_api("GET", api_url, "/auth/me", auth=True)
            if me:
                st.session_state.auth_user = me
                st.rerun()
        if st.button("Logout", use_container_width=True):
            for key in ["auth_token", "auth_user", "plan_result", "coach_result", "memory_search_result"]:
                st.session_state[key] = None
            st.rerun()
        return

    local_tab, clerk_tab = st.tabs(["Local Login", "Clerk Token"])
    with local_tab:
        login_tab, register_tab = st.tabs(["Login", "Register"])
        with login_tab:
            with st.form("login_form"):
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Login", use_container_width=True)
            if submitted:
                auth = safe_api("POST", api_url, "/auth/login", {"email": email, "password": password})
                if auth:
                    st.session_state.auth_token = auth["token"]
                    st.session_state.auth_user = auth
                    st.rerun()
        with register_tab:
            with st.form("register_form"):
                name = st.text_input("Full name")
                username = st.text_input("Username")
                email = st.text_input("Email", key="register_email")
                password = st.text_input("Password", type="password", key="register_password")
                submitted = st.form_submit_button("Create Account", use_container_width=True)
            if submitted:
                auth = safe_api(
                    "POST",
                    api_url,
                    "/auth/register",
                    {"name": name, "username": username, "email": email, "password": password},
                )
                if auth:
                    st.session_state.auth_token = auth["token"]
                    st.session_state.auth_user = auth
                    st.rerun()
    with clerk_tab:
        st.caption("Use this if you already have a Clerk-issued JWT and the backend is configured to verify it.")
        with st.form("clerk_form"):
            clerk_token = st.text_area("Clerk token", height=120)
            submitted = st.form_submit_button("Use Clerk Token", use_container_width=True)
        if submitted and clerk_token.strip():
            st.session_state.auth_token = clerk_token.strip()
            me = safe_api("GET", api_url, "/auth/me", auth=True)
            if me:
                st.session_state.auth_user = me
                st.rerun()
            st.session_state.auth_token = None


def render_home(snapshot: dict) -> None:
    profile = snapshot.get("profile") or {}
    streak = snapshot.get("streak") or {}
    progress = snapshot.get("progress") or {}
    women = snapshot.get("women") or {}
    history = snapshot.get("history") or {}
    lottie_coach = load_lottie_url(LOTTIE_COACH_URL) if st_lottie else None

    render_section_hero(
        "Operational health view",
        "Track readiness, adherence, cycle-aware context, and memory-backed recommendations from one control surface.",
    )

    header_cols = st.columns([1.25, 0.75], gap="large")
    with header_cols[0]:
        st.markdown(
            """
            <div class="floating-card">
                <div class="section-title">Aurora stream</div>
                <p>
                    Live data feedback, coaching memory, cycle-aware context, and export-ready metrics are all within
                    reach. Use the tabs to jump between workspace, hormonal status, and studio creativity without losing
                    track of the goals you care about.
                </p>
                <div class="progress-hint">Hover cards to reveal motion; loading states stay gentle but intentional.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with header_cols[1]:
        render_ai_avatar()

    adherence_score = progress.get("adherence_score", 0.0)
    energy_score = progress.get("energy_level", 0.0)
    adherence_percent = min(max(adherence_score / 10.0, 0.0), 1.0)
    energy_percent = min(max(energy_score / 10.0, 0.0), 1.0)

    history_df = pd.DataFrame(progress.get("history", [])).sort_values("date") if progress.get("history") else pd.DataFrame()
    if not history_df.empty and "date" in history_df.columns:
        history_df["date"] = pd.to_datetime(history_df["date"])
    chart_columns = [col for col in ["energy_level", "adherence_score", "workout_minutes", "weight"] if col in history_df.columns]

    home_tabs = st.tabs(["Live Workspace", "Cycle Pulse", "Studio Insights"])
    with home_tabs[0]:
        top = st.columns(4)
        with top[0]:
            render_metric_card("Current Goal", profile.get("goal", "Set profile"))
        with top[1]:
            render_metric_card("Streak", f"{streak.get('current_streak', 0)} days")
        with top[2]:
            render_metric_card("Progress Trend", progress.get("trend", "no-data"))
        with top[3]:
            render_metric_card("Cycle Phase", women.get("predicted_phase", "n/a"))

        progress_row = st.columns(2)
        with progress_row[0]:
            st.progress(adherence_percent, key="adherence_progress")
            st.caption(f"Adherence {adherence_score:.1f}/10 · {history_df.shape[0]} logs included")
        with progress_row[1]:
            st.progress(energy_percent, key="energy_progress")
            st.caption(f"Energy {energy_score:.1f}/10 · keep fueling consistency")

        left, right = st.columns([1.1, 0.9], gap="large")
        with left:
            render_panel(
                "Aurora Overview",
                (
                    f"{profile.get('name', st.session_state.auth_user['name'])} is tracking "
                    f"{len(history.get('workout_logs', []))} workouts, {len(history.get('diet_logs', []))} diet entries, "
                    f"and {len(history.get('progress_logs', []))} progress check-ins. "
                    f"Aurora keeps semantic memory from coaching, logging, and feedback to personalize future plans."
                ),
            )
            quick = st.columns(3)
            with quick[0]:
                if st.button("Go To Plans", use_container_width=True):
                    st.session_state.selected_section = "Plans"
                    st.rerun()
            with quick[1]:
                if st.button("Log Today", use_container_width=True):
                    st.session_state.selected_section = "Daily Tracking"
                    st.rerun()
            with quick[2]:
                if st.button("Open Memory", use_container_width=True):
                    st.session_state.selected_section = "Memory & History"
                    st.rerun()
        with right:
            render_panel(
                "Weekly Focus",
                "<br>".join(
                    [
                        f"Goal: {profile.get('goal', 'Save your profile')}",
                        f"Energy trend: {progress.get('trend', 'no-data')}",
                        f"Women health phase: {women.get('predicted_phase', 'n/a')}",
                        f"Last check-in streak: {streak.get('current_streak', 0)} days",
                    ]
                ),
            )

    with home_tabs[1]:
        cycle_kpis = st.columns(3)
        with cycle_kpis[0]:
            st.metric("Cycle Phase", women.get("predicted_phase", "n/a"))
        with cycle_kpis[1]:
            st.metric("Next Period", women.get("next_period_start", "TBD"))
        with cycle_kpis[2]:
            st.metric("Irregularity", women.get("irregularity_score", "unknown"))

        with st.expander("Cycle Forecast & Focus", expanded=False):
            render_panel(
                "Cycle Forecast",
                (
                    f"Predicted phase: {women.get('predicted_phase', 'unknown')}<br>"
                    f"Next period start: {women.get('next_period_start', 'unknown')}"
                ),
            )
            render_panel(
                "Women Health Guidance",
                "<br>".join(women.get("nutrition_focus", [])) or "Keep logging to unlock cycle-specific nutrition guidance.",
            )

        if chart_columns and "date" in history_df.columns:
            if go:
                fig = go.Figure()
                for col in chart_columns:
                    fig.add_trace(
                        go.Scatter(
                            x=history_df["date"],
                            y=history_df[col],
                            mode="lines+markers",
                            name=col.replace("_", " ").title(),
                            line=dict(width=2),
                        )
                    )
                fig.update_layout(
                    margin=dict(t=20, b=20, l=0, r=0),
                    height=320,
                    template="plotly_white",
                    paper_bgcolor="rgba(0,0,0,0)",
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.line_chart(history_df.set_index("date")[chart_columns], use_container_width=True)
        elif chart_columns:
            st.caption("Add a date to each progress entry to unlock the full trend view.")
        else:
            st.caption("Log a few progress entries to activate the trend visualization.")

    with home_tabs[2]:
        highlight = st.columns([1.1, 0.9], gap="large")
        with highlight[0]:
            render_feature_card(
                "Adaptive plan engine",
                "Plans combine profile, lifestyle, hormonal context, and recent logs so recommendations can evolve instead of staying static.",
            )
            render_feature_card(
                "Semantic memory",
                "Aurora stores coaching, feedback, workouts, diet, and progress entries so future responses can retrieve the right context quickly.",
            )
            render_feature_card(
                "Clinical caution layer",
                "Women's health and postpartum guidance stay available without collapsing the app into a medical-claims experience.",
            )
        with highlight[1]:
            st.markdown("<div class='lottie-wrapper'>", unsafe_allow_html=True)
            if st_lottie and lottie_coach:
                st_lottie(lottie_coach, height=260, loop=True, quality="high")
            else:
                st.caption("Aurora is preparing a premium animation.")
            st.markdown("</div>", unsafe_allow_html=True)
            delta_value = int(adherence_percent * 100) - 70
            st.metric("Adherence confidence", f"{adherence_score:.1f}/10", delta=f"{delta_value}% vs target")
            st.progress(adherence_percent, key="adherence_highlight")
            st.caption(f"Energy {energy_score:.1f}/10 · let Aurora keep your habits tracked.")


def render_profile(api_url: str, snapshot: dict) -> None:
    profile = snapshot.get("profile") or {}
    lifestyle = profile.get("lifestyle") or {}
    render_section_hero(
        "Profile and physiological context",
        "Save the baseline Aurora uses for plans, cycle-aware guidance, weekly reporting, and recovery-sensitive coaching.",
    )
    with st.form("profile_form"):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Name", value=profile.get("name", st.session_state.auth_user["name"]))
            age = st.number_input("Age", min_value=13, max_value=100, value=int(profile.get("age", 26)), step=1)
            gender_options = ["female", "male", "other"]
            gender_value = profile.get("gender", "female")
            gender = st.selectbox("Gender", gender_options, index=gender_options.index(gender_value) if gender_value in gender_options else 0)
            weight = st.number_input("Weight (kg)", min_value=20.0, max_value=300.0, value=float(profile.get("weight", 62.0)), step=1.0)
            height_cm = st.number_input("Height (cm)", min_value=100.0, max_value=230.0, value=float(profile.get("height_cm", 165.0)), step=1.0)
            goal_options = ["fat loss", "muscle gain", "strength", "endurance", "general fitness", "pregnancy wellness", "postpartum recovery"]
            goal_value = profile.get("goal", "general fitness")
            goal = st.selectbox("Primary goal", goal_options, index=goal_options.index(goal_value) if goal_value in goal_options else 0)
            level_options = ["beginner", "intermediate", "advanced"]
            level_value = profile.get("level", "beginner")
            level = st.selectbox("Training level", level_options, index=level_options.index(level_value) if level_value in level_options else 0)
        with c2:
            pregnant = st.checkbox("Pregnant", value=bool(profile.get("pregnant", False)))
            postpartum = st.checkbox("Postpartum", value=bool(profile.get("postpartum", False)))
            trimester_values = [None, 1, 2, 3]
            trimester = st.selectbox(
                "Pregnancy trimester",
                trimester_values,
                index=trimester_values.index(profile.get("pregnancy_trimester")) if profile.get("pregnancy_trimester") in trimester_values else 0,
                format_func=lambda value: "Not set" if value is None else str(value),
            )
            postpartum_weeks = st.number_input("Postpartum weeks", min_value=0, max_value=156, value=int(profile.get("postpartum_weeks") or 0), step=1)
            hormonal_concerns = st.multiselect(
                "Hormonal concerns",
                ["pcos", "thyroid", "acne", "fatigue", "mood swings", "irregular periods", "bloating"],
                default=profile.get("hormonal_concerns", []),
            )
            dietary_restrictions = st.multiselect(
                "Dietary restrictions",
                ["vegetarian", "vegan", "gluten-free", "lactose-free", "high-protein", "diabetic-friendly"],
                default=profile.get("dietary_restrictions", []),
            )
            activity_options = ["low", "moderate", "active", "athletic"]
            diet_style_options = ["balanced", "high-protein", "vegetarian", "vegan", "low-carb", "Mediterranean"]
            activity_level = st.selectbox(
                "Activity level",
                activity_options,
                index=activity_options.index(lifestyle.get("activity_level", "moderate")) if lifestyle.get("activity_level", "moderate") in activity_options else 1,
            )
            dietary_preference = st.selectbox(
                "Diet style",
                diet_style_options,
                index=diet_style_options.index(lifestyle.get("dietary_preference", "balanced")) if lifestyle.get("dietary_preference", "balanced") in diet_style_options else 0,
            )
        c3, c4, c5 = st.columns(3)
        with c3:
            sleep_hours = st.slider("Sleep hours", 0.0, 12.0, float(lifestyle.get("sleep_hours", 7.0)), 0.5)
        with c4:
            water_liters = st.slider("Water liters", 0.0, 5.0, float(lifestyle.get("water_liters", 2.5)), 0.1)
        with c5:
            stress_level = st.slider("Stress level", 1, 10, int(lifestyle.get("stress_level", 5)))
        health_goals = st.multiselect(
            "Lifestyle targets",
            ["better sleep", "better energy", "cycle support", "weight management", "stress control", "muscle tone", "pregnancy support"],
            default=lifestyle.get("health_goals", []),
        )
        submitted = st.form_submit_button("Save Profile", use_container_width=True)
    if submitted:
        payload = {
            "name": name,
            "age": age,
            "gender": gender,
            "weight": weight,
            "height_cm": height_cm,
            "goal": goal,
            "level": level,
            "pregnant": pregnant,
            "postpartum": postpartum,
            "pregnancy_trimester": trimester,
            "postpartum_weeks": postpartum_weeks if postpartum else None,
            "hormonal_concerns": hormonal_concerns,
            "dietary_restrictions": dietary_restrictions,
            "lifestyle": {
                "sleep_hours": sleep_hours,
                "water_liters": water_liters,
                "stress_level": stress_level,
                "activity_level": activity_level,
                "dietary_preference": dietary_preference,
                "health_goals": health_goals,
            },
        }
        result = safe_api("POST", api_url, "/profile", payload, auth=True)
        if result:
            st.success("Profile saved.")
            st.rerun()


def render_plans(api_url: str, snapshot: dict) -> None:
    profile = snapshot.get("profile") or {}
    lifestyle = profile.get("lifestyle") or {}
    women = snapshot.get("women") or {}

    render_section_hero(
        "Plan generation studio",
        "Generate workout, diet, and context-aware women’s health guidance from the current account state without losing the manual controls.",
    )

    with st.form("plan_form"):
        c1, c2, c3 = st.columns(3)
        with c1:
            plan_goal = st.selectbox("Plan goal", ["fat loss", "muscle gain", "strength", "endurance", "general fitness", "pregnancy wellness", "postpartum recovery"])
            plan_level = st.selectbox("Training level", ["beginner", "intermediate", "advanced"])
            plan_weight = st.number_input("Current weight", min_value=20.0, max_value=300.0, value=float(profile.get("weight", 62.0)), step=1.0)
        with c2:
            context_options = ["female", "male", "other"]
            context_value = profile.get("gender", "female")
            plan_gender = st.selectbox("Context", context_options, index=context_options.index(context_value) if context_value in context_options else 0)
            cycle_phase_options = ["", "menstrual", "follicular", "ovulation", "luteal"]
            phase_default = women.get("predicted_phase", "")
            normalized_phase = phase_default if phase_default in cycle_phase_options else ""
            cycle_phase = st.selectbox("Cycle phase", cycle_phase_options, index=cycle_phase_options.index(normalized_phase))
            pregnant_plan = st.checkbox("Pregnancy-aware", value=bool(profile.get("pregnant", False)))
        with c3:
            postpartum_plan = st.checkbox("Postpartum-aware", value=bool(profile.get("postpartum", False)))
            trimester_values = [None, 1, 2, 3]
            trimester_plan = st.selectbox(
                "Trimester",
                trimester_values,
                index=trimester_values.index(profile.get("pregnancy_trimester")) if profile.get("pregnancy_trimester") in trimester_values else 0,
                format_func=lambda value: "Not set" if value is None else str(value),
            )
            postpartum_weeks = st.number_input("Postpartum weeks", min_value=0, max_value=156, value=int(profile.get("postpartum_weeks") or 0), step=1)
        hormonal_plan = st.multiselect(
            "Hormonal concerns",
            ["pcos", "thyroid", "fatigue", "irregular periods", "mood swings", "bloating"],
            default=profile.get("hormonal_concerns", []),
        )
        restrictions = st.multiselect(
            "Dietary restrictions",
            ["vegetarian", "vegan", "gluten-free", "lactose-free", "diabetic-friendly"],
            default=profile.get("dietary_restrictions", []),
        )
        submitted = st.form_submit_button("Generate Aurora Plan", use_container_width=True)

    if submitted:
        st.session_state.plan_result = safe_api(
            "POST",
            api_url,
            "/generate-plan",
            {
                "goal": plan_goal,
                "level": plan_level,
                "weight": plan_weight,
                "gender": plan_gender,
                "cycle_phase": cycle_phase or None,
                "age": profile.get("age"),
                "activity_level": lifestyle.get("activity_level"),
                "pregnant": pregnant_plan,
                "postpartum": postpartum_plan,
                "pregnancy_trimester": trimester_plan,
                "postpartum_weeks": postpartum_weeks if postpartum_plan else None,
                "hormonal_concerns": hormonal_plan,
                "dietary_restrictions": restrictions,
            },
        )

    plan = st.session_state.plan_result
    if plan:
        left, right = st.columns(2, gap="large")
        with left:
            render_panel("Workout Plan", plan.get("workout", ""))
        with right:
            render_panel("Diet Plan", plan.get("diet", ""))
        if plan.get("women_health"):
            render_panel("Women Health Guidance", plan["women_health"])
        st.download_button(
            "Download Plan JSON",
            data=to_json_bytes(plan),
            file_name="aurora_plan.json",
            mime="application/json",
            use_container_width=True,
        )


def render_women_health(api_url: str, snapshot: dict) -> None:
    women = snapshot.get("women") or {}
    render_section_hero(
        "Cycle and women’s health dashboard",
        "Log periods, review predicted phase, and surface nutrition or training adjustments without hiding the uncertainty of limited data.",
    )
    left, right = st.columns([1, 1], gap="large")
    with left:
        with st.form("period_form"):
            start_date = st.date_input("Period start", value=date.today())
            end_date = st.date_input("Period end", value=date.today())
            symptoms = st.multiselect("Symptoms", ["cramps", "fatigue", "acne", "mood swings", "bloating", "headache", "dizziness"])
            flow_level = st.selectbox("Flow", ["light", "moderate", "heavy"])
            mood = st.selectbox("Mood", ["stable", "low", "anxious", "irritable", "energized"])
            cravings = st.multiselect("Cravings", ["sweet", "salty", "carbs", "chocolate", "none"])
            notes = st.text_area("Notes", placeholder="Pain levels, sleep, cravings, spotting, or anything Aurora should remember.")
            submitted = st.form_submit_button("Save Period Log", use_container_width=True)
        if submitted:
            result = safe_api(
                "POST",
                api_url,
                "/women-health/log-period",
                {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "symptoms": symptoms,
                    "flow_level": flow_level,
                    "mood": mood,
                    "cravings": [] if "none" in cravings else cravings,
                    "notes": notes,
                },
                auth=True,
            )
            if result:
                st.success("Period log saved.")
                st.rerun()
    with right:
        a, b, c = st.columns(3)
        with a:
            st.metric("Avg cycle", women.get("average_cycle_length") or "n/a")
        with b:
            st.metric("Avg period", women.get("average_period_length") or "n/a")
        with c:
            st.metric("Irregularity", women.get("irregularity_score", "unknown"))
        render_panel(
            "Cycle Forecast",
            (
                f"Predicted phase: {women.get('predicted_phase', 'unknown')}<br>"
                f"Next period start: {women.get('next_period_start', 'unknown')}"
            ),
        )
        render_panel("Nutrition Focus", "<br>".join(women.get("nutrition_focus", [])) or "Keep logging to unlock cycle-specific nutrition guidance.")
        render_panel("Workout Focus", "<br>".join(women.get("workout_focus", [])) or "Keep logging to unlock cycle-specific training guidance.")
        for concern in women.get("possible_concerns", []):
            st.warning(f"{concern.get('flag')}: {concern.get('detail')}")
        if women.get("recent_logs"):
            st.dataframe(pd.DataFrame(women["recent_logs"]), use_container_width=True)
        if women.get("disclaimer"):
            st.info(women["disclaimer"])


def render_tracking(api_url: str) -> None:
    render_section_hero(
        "Daily tracking workspace",
        "Capture the events that make Aurora smarter later: workout load, diet adherence, cravings, and the notes that explain them.",
    )
    top = st.columns(2, gap="large")
    with top[0]:
        with st.form("workout_log_form"):
            workout_type = st.selectbox("Workout type", ["strength", "cardio", "walking", "mobility", "yoga", "sports", "recovery"])
            duration_minutes = st.slider("Duration minutes", 0, 180, 40)
            intensity = st.select_slider("Intensity", options=["low", "moderate", "high"], value="moderate")
            completed = st.radio("Completed", [True, False], format_func=lambda value: "Yes" if value else "No", horizontal=True)
            notes = st.text_area("Workout notes", placeholder="Energy, pain, performance, soreness, favorite exercise.")
            submitted = st.form_submit_button("Save Workout Log", use_container_width=True)
        if submitted:
            result = safe_api(
                "POST",
                api_url,
                "/tracking/workout",
                {
                    "workout_type": workout_type,
                    "duration_minutes": duration_minutes,
                    "intensity": intensity,
                    "completed": completed,
                    "notes": notes,
                },
                auth=True,
            )
            if result:
                st.success("Workout log saved.")
    with top[1]:
        with st.form("diet_log_form"):
            meals_followed = st.select_slider("Meals followed", options=[0, 1, 2, 3, 4, 5, 6], value=3)
            hydration_liters = st.slider("Hydration liters", 0.0, 5.0, 2.4, 0.1)
            protein_grams = st.slider("Protein grams", 0, 220, 90)
            cravings = st.multiselect("Cravings", ["sweet", "salty", "fried", "late-night", "carbs", "none"])
            notes = st.text_area("Diet notes", placeholder="Hunger, digestion, cravings, meal quality, supplements.")
            submitted = st.form_submit_button("Save Diet Log", use_container_width=True)
        if submitted:
            result = safe_api(
                "POST",
                api_url,
                "/tracking/diet",
                {
                    "meals_followed": meals_followed,
                    "hydration_liters": hydration_liters,
                    "protein_grams": protein_grams,
                    "cravings": [] if "none" in cravings else cravings,
                    "notes": notes,
                },
                auth=True,
            )
            if result:
                st.success("Diet log saved.")
    render_panel(
        "Memory + Tracking",
        "Aurora saves workout logs, diet logs, progress logs, period patterns, and your feedback as structured history plus semantic memory. That data is used later for coaching, weekly reports, and RAG-based personalization.",
    )


def render_progress(api_url: str, snapshot: dict) -> None:
    progress = snapshot.get("progress") or {}
    streak = snapshot.get("streak") or {}

    render_section_hero(
        "Progress, adherence, and accountability",
        "This view connects raw progress logs with streak check-ins and user feedback so coaching has both numbers and narrative context.",
    )

    left, right = st.columns([1, 1], gap="large")
    with left:
        with st.form("progress_form"):
            weight = st.number_input("Weight (optional)", min_value=20.0, max_value=300.0, value=62.0, step=1.0)
            energy_level = st.slider("Energy", 1, 10, 6)
            mood = st.selectbox("Mood", ["strong", "steady", "low", "stressed", "motivated", "drained"])
            workout_minutes = st.slider("Workout minutes", 0, 180, 35)
            adherence_score = st.slider("Adherence score", 1, 10, 7)
            notes = st.text_area("Progress notes", placeholder="What improved, what felt hard, what Aurora should adapt next.")
            submitted = st.form_submit_button("Save Progress Log", use_container_width=True)
        if submitted:
            result = safe_api(
                "POST",
                api_url,
                "/progress/log",
                {
                    "weight": weight,
                    "energy_level": energy_level,
                    "mood": mood,
                    "workout_minutes": workout_minutes,
                    "adherence_score": adherence_score,
                    "notes": notes,
                },
                auth=True,
            )
            if result:
                st.success("Progress log saved.")
                st.rerun()

        with st.form("feedback_form"):
            category = st.selectbox("Feedback category", ["plan", "coach", "cycle", "diet", "workout", "app experience"])
            feedback = st.text_area("Feedback", placeholder="Tell Aurora what worked and what should change.")
            rating = st.slider("Rating", 1, 10, 7)
            submitted = st.form_submit_button("Save Feedback", use_container_width=True)
        if submitted:
            result = safe_api("POST", api_url, "/tracking/feedback", {"category": category, "feedback": feedback, "rating": rating}, auth=True)
            if result:
                st.success("Feedback saved to memory.")
    with right:
        st.metric("Trend", progress.get("trend", "no-data"))
        st.metric("Entries", progress.get("entries", 0))
        st.metric("Streak", f"{streak.get('current_streak', 0)} days")
        if progress.get("history"):
            history_df = pd.DataFrame(progress["history"]).sort_values("date")
            chart_columns = [col for col in ["energy_level", "adherence_score", "workout_minutes", "weight"] if col in history_df.columns]
            if chart_columns:
                st.line_chart(history_df.set_index("date")[chart_columns], use_container_width=True)
            st.dataframe(history_df, use_container_width=True)
        render_panel("Accountability", streak.get("motivation", "Keep showing up."))
        with st.form("streak_form"):
            workout_completed = st.checkbox("Workout completed today", value=True)
            nutrition_completed = st.checkbox("Nutrition goals completed today")
            journal_note = st.text_area("Daily note", placeholder="One sentence is enough.")
            submitted = st.form_submit_button("Daily Check-In", use_container_width=True)
        if submitted:
            result = safe_api(
                "POST",
                api_url,
                "/streaks/check-in",
                {
                    "workout_completed": workout_completed,
                    "nutrition_completed": nutrition_completed,
                    "journal_note": journal_note,
                },
                auth=True,
            )
            if result:
                st.session_state.streak_result = result
                st.success("Daily check-in saved.")


def render_memory_history(api_url: str, snapshot: dict) -> None:
    history = snapshot.get("history") or {}
    report = snapshot.get("weekly_report")

    render_section_hero(
        "Memory and export center",
        "Search semantic memory, inspect structured history, and export the full health record without losing the original backend payloads.",
    )

    controls = st.columns([1.4, 0.6], gap="large")
    with controls[0]:
        with st.form("memory_search_form"):
            query = st.text_input("Search Aurora memory", placeholder="Examples: low energy before period, protein consistency, walking streak")
            top_k = st.slider("Results", 1, 10, 5)
            submitted = st.form_submit_button("Search Memory", use_container_width=True)
        if submitted and query.strip():
            st.session_state.memory_search_result = safe_api(
                "POST",
                api_url,
                "/tracking/memory-search",
                {"query": query.strip(), "top_k": top_k},
                auth=True,
            )
    with controls[1]:
        render_export_buttons(history, report)

    memory_result = st.session_state.memory_search_result
    with st.expander("Memory Search Results", expanded=bool(memory_result)):
        if memory_result:
            render_panel("Memory Search", f"Query: {memory_result.get('query', '')}")
            results = memory_result.get("results", [])
            if results:
                st.dataframe(pd.DataFrame(results), use_container_width=True)
            else:
                st.caption("No relevant memory found yet.")
        else:
            st.caption("Search Aurora memory to see coaching context here.")

    history_sections = [
        ("Workout History", history.get("workout_logs", []), "aurora_workouts.csv"),
        ("Diet History", history.get("diet_logs", []), "aurora_diet.csv"),
        ("Progress History", history.get("progress_logs", []), "aurora_progress.csv"),
        ("Period History", history.get("period_logs", []), "aurora_periods.csv"),
        ("Semantic Memory", history.get("recent_memories", []), "aurora_memory.csv"),
    ]
    for title, rows, csv in history_sections:
        with st.expander(f"{title}  ({len(rows)} entries)", expanded=False):
            render_history_block(title, rows, csv, include_header=False)


def render_weekly_report(snapshot: dict) -> None:
    report = snapshot.get("weekly_report")
    render_section_hero(
        "Weekly executive summary",
        "Aurora rolls profile, progress, streak, and women’s health signals into a concise weekly readout with risks and next actions.",
    )
    if not report:
        st.info("Weekly report is not available yet. Log more activity and try again.")
        return
    render_panel("Aurora Weekly Summary", report.get("summary", ""))
    c1, c2, c3 = st.columns(3)
    with c1:
        render_panel("Wins", "<br>".join(report.get("wins", [])) or "No wins recorded yet.")
    with c2:
        render_panel("Risks", "<br>".join(report.get("risks", [])) or "No major risks flagged.")
    with c3:
        render_panel("Recommendations", "<br>".join(report.get("recommendations", [])) or "No recommendations yet.")
    st.caption(f"Report window: {report.get('period_start')} to {report.get('period_end')}")
    st.download_button(
        "Download Weekly Report JSON",
        data=to_json_bytes(report),
        file_name="aurora_weekly_report.json",
        mime="application/json",
        use_container_width=True,
    )


def render_aurora_chat(api_url: str) -> None:
    render_section_hero(
        "Aurora coach console",
        "Use the coach when you want a response grounded in saved profile data, progress trends, memory retrieval, and recent health behavior.",
    )
    render_panel(
        "Adaptive Coach",
        "Aurora uses your saved profile, progress logs, period history, workout and diet tracking, plus semantic memory retrieved through RAG to generate more personalized guidance over time.",
    )
    with st.form("coach_form"):
        coach_message = st.text_area(
            "Ask Aurora",
            placeholder="I lose motivation during luteal phase and miss protein targets. How should my next 7 days change?",
            height=160,
        )
        submitted = st.form_submit_button("Get Coaching", use_container_width=True)
    if submitted:
        st.session_state.coach_result = safe_api("POST", api_url, "/progress/coach", {"message": coach_message}, auth=True)
    coach = st.session_state.coach_result
    if coach:
        render_panel("Aurora Reply", coach.get("reply", ""))
        if coach.get("insights"):
            render_panel("Insights", "<br>".join(coach["insights"]))
        if coach.get("next_steps"):
            render_panel("Next Steps", "<br>".join(coach["next_steps"]))
        st.download_button(
            "Download Coach Reply",
            data=to_json_bytes(coach),
            file_name="aurora_coach_reply.json",
            mime="application/json",
            use_container_width=True,
        )


init_state()
ensure_asset_folder()

st.markdown(
    """
    <div class="hero">
        <div class="hero-grid">
            <div>
                <h1>Aurora Health Studio</h1>
                <p>
                    One place for adaptive plans, women-centered health support, pregnancy and postpartum guidance,
                    lifestyle tracking, semantic memory, streaks, weekly reporting, and a coach that gets smarter as
                    your data grows.
                </p>
                <div class="pill-row">
                    <span class="pill">Women + Men</span>
                    <span class="pill">Cycle Aware</span>
                    <span class="pill">Pregnancy + Postpartum</span>
                    <span class="pill">Memory + RAG</span>
                    <span class="pill">CSV + JSON Export</span>
                </div>
            </div>
            <div class="hero-side">
                <div class="hero-side-title">Studio Mode</div>
                <div style="font-size: 1.15rem; font-weight: 800; margin-bottom: 0.5rem;">Operational control over coaching, tracking, and reporting</div>
                <div style="line-height: 1.6; color: rgba(255,255,255,0.82);">
                    Use Streamlit as the admin-style health console while the Next app stays focused on the premium end-user experience.
                </div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.subheader("Connection")
    api_url = st.text_input("API Base URL", value=DEFAULT_API_URL)
    if st.button("Check Backend", use_container_width=True):
        health = safe_api("GET", api_url, "/")
        if health:
            st.success(health.get("message", "Backend reachable"))
    st.markdown("---")
    sidebar_auth(api_url)
    st.markdown("---")
    st.subheader("Navigation")
    st.session_state.selected_section = st.radio(
        "Workspace",
        SECTION_OPTIONS,
        index=SECTION_OPTIONS.index(st.session_state.selected_section) if st.session_state.selected_section in SECTION_OPTIONS else 0,
        label_visibility="collapsed",
    )
    st.caption("FastAPI: `python -m uvicorn backend.main:app --reload`")
    st.caption("Streamlit remembers session state, and Aurora stores health data in the backend database.")


metrics = st.columns(5)
with metrics[0]:
    render_metric_card("Identity", "Username + account")
with metrics[1]:
    render_metric_card("Memory", "Saved + searchable")
with metrics[2]:
    render_metric_card("Tracking", "Workout + diet + streak")
with metrics[3]:
    render_metric_card("Women's Health", "Cycle-aware insights")
with metrics[4]:
    render_metric_card("Exports", "CSV + JSON")


if not st.session_state.auth_user:
    st.info("Sign in from the sidebar to use Aurora.")
    st.stop()


with st.spinner("Refreshing Aurora workspace..."):
    snapshot = fetch_snapshot(api_url)
section = st.session_state.selected_section

if section == "Home":
    render_home(snapshot)
elif section == "Profile":
    render_profile(api_url, snapshot)
elif section == "Plans":
    render_plans(api_url, snapshot)
elif section == "Women's Health":
    render_women_health(api_url, snapshot)
elif section == "Daily Tracking":
    render_tracking(api_url)
elif section == "Progress":
    render_progress(api_url, snapshot)
elif section == "Memory & History":
    render_memory_history(api_url, snapshot)
elif section == "Weekly Report":
    render_weekly_report(snapshot)
elif section == "Aurora Coach":
    render_aurora_chat(api_url)
