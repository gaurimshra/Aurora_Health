import concurrent.futures
import html
import json
from datetime import date

import httpx
import pandas as pd
import streamlit as st

try:
    import plotly.graph_objects as go
except ModuleNotFoundError:
    go = None


DEFAULT_API_URL = "https://aurora-health.onrender.com"
SECTIONS = [
    "Home",
    "Plans",
    "Progress",
    "Daily Tracking",
    "Women's Health",
    "Memory & History",
    "Weekly Report",
    "Aurora Coach",
    "Profile",
]
SNAPSHOT_PATHS = {
    "profile": "/profile/me",
    "streak": "/streaks/me",
    "progress": "/progress/me",
    "women": "/women-health/dashboard",
    "history": "/tracking/history",
    "weekly_report": "/tracking/weekly-report",
}

st.set_page_config(page_title="Aurora Health Studio", page_icon="A", layout="wide", initial_sidebar_state="expanded")
st.markdown(
    """
    <style>
    :root { --bg:#F8F7FB; --card:#FFFFFF; --primary:#7C6CF6; --secondary:#FADADD; --text:#1F2937; --muted:#6B7280; --line:#E9E5F5; }
    .stApp { background: radial-gradient(circle at top left, rgba(250,218,221,.7), transparent 24%), linear-gradient(180deg, #FCFBFE 0%, var(--bg) 100%); color:var(--text); }
    .stApp [data-testid="stSidebar"] { background: linear-gradient(180deg, #FFF9FC 0%, #F8F7FB 100%); border-right:1px solid var(--line); }
    .stApp [data-testid="stSidebar"] * { color:var(--text); }
    .block-container { padding-top:1.3rem; }
    .shell, .card, .navtop { background:rgba(255,255,255,.95); border:1px solid var(--line); border-radius:24px; box-shadow:0 18px 42px rgba(124,108,246,.10); }
    .shell { padding:26px; }
    .hero { background:linear-gradient(145deg, rgba(124,108,246,.96), rgba(100,82,228,.90)); color:white; border-radius:30px; padding:30px; min-height:480px; box-shadow:0 26px 48px rgba(103,87,227,.25); }
    .hero h1 { color:white; font-size:2.8rem; line-height:1.02; margin:.45rem 0 1rem 0; }
    .eyebrow { text-transform:uppercase; letter-spacing:.14em; font-size:.72rem; font-weight:700; color:var(--muted); }
    .hero .eyebrow { color:rgba(255,255,255,.74); }
    .hero p, .copy { line-height:1.62; color:inherit; }
    .pillrow { display:flex; flex-wrap:wrap; gap:.6rem; margin-top:1.1rem; }
    .pill { padding:.45rem .8rem; border-radius:999px; background:rgba(255,255,255,.14); border:1px solid rgba(255,255,255,.18); font-size:.82rem; }
    .navtop { padding:18px 22px; margin-bottom:1rem; }
    .navtitle { font-size:1.8rem; font-weight:800; margin:.2rem 0 .35rem 0; color:var(--text); }
    .kpi, .card { padding:18px 20px; }
    .klabel { text-transform:uppercase; letter-spacing:.12em; font-size:.7rem; font-weight:700; color:var(--muted); margin-bottom:.7rem; }
    .kvalue { font-size:1.55rem; font-weight:800; color:var(--text); }
    .kcopy { color:var(--muted); font-size:.92rem; line-height:1.5; margin-top:.45rem; }
    .ctitle { font-size:1.08rem; font-weight:800; color:var(--text); margin-bottom:.8rem; }
    .listitem { padding:.8rem .9rem; margin-bottom:.6rem; border-radius:16px; background:#FBFAFE; border:1px solid rgba(124,108,246,.08); line-height:1.55; color:var(--text); }
    .avatar { width:150px; height:150px; margin:0 auto .9rem auto; border-radius:50%; background:radial-gradient(circle at 50% 35%, #FFE9EC 0 24%, #F5CCD3 25% 42%, #7C6CF6 43% 100%); position:relative; overflow:hidden; box-shadow:0 16px 32px rgba(124,108,246,.18); }
    .avatar:before { content:""; position:absolute; width:72px; height:72px; border-radius:50%; background:#FFE6DE; top:28px; left:39px; }
    .avatar:after { content:""; position:absolute; width:114px; height:70px; border-radius:58px 58px 24px 24px; background:#FFF4F3; bottom:10px; left:18px; }
    .empty { padding:20px; border-radius:22px; border:1px dashed rgba(124,108,246,.24); background:rgba(255,255,255,.78); color:var(--muted); }
    .watermark { position:fixed; right:16px; bottom:10px; z-index:9999; font-size:.76rem; font-weight:700; letter-spacing:.04em; color:rgba(31,41,55,.55); background:rgba(255,255,255,.72); border:1px solid rgba(124,108,246,.14); padding:.3rem .55rem; border-radius:999px; backdrop-filter:blur(6px); pointer-events:none; }
    </style>
    """,
    unsafe_allow_html=True,
)


def init_state():
    defaults = {
        "api_url": DEFAULT_API_URL,
        "auth_token": None,
        "auth_user": None,
        "selected_section": "Home",
        "snapshot_version": 0,
        "plan_result": None,
        "coach_result": None,
        "memory_search_result": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def headers(auth=False):
    token = st.session_state.get("auth_token")
    return {"Authorization": f"Bearer {token}"} if auth and token else {}


def api_request(method, base_url, path, payload=None, auth=False):
    with httpx.Client(timeout=httpx.Timeout(45.0, connect=8.0)) as client:
        response = client.request(method, f"{base_url.rstrip('/')}{path}", json=payload, headers=headers(auth))
        response.raise_for_status()
        return response.json()


def safe_api(method, api_url, path, payload=None, auth=False, show_errors=True):
    try:
        return api_request(method, api_url, path, payload, auth)
    except httpx.HTTPStatusError as exc:
        if show_errors:
            message = exc.response.text if exc.response is not None else str(exc)
            st.error(f"Request failed: {message}")
    except Exception as exc:
        if show_errors:
            st.error(f"Backend error: {exc}")
    return None


def bump_snapshot(clear_outputs=False):
    st.session_state.snapshot_version += 1
    if clear_outputs:
        st.session_state.plan_result = None
        st.session_state.coach_result = None
        st.session_state.memory_search_result = None


def get_lines(value, empty_text="No data available yet."):
    if value is None:
        return [empty_text]
    if isinstance(value, list):
        items = [str(item).strip() for item in value if str(item).strip()]
        return items or [empty_text]
    text = str(value).replace("\r", "").strip()
    if not text:
        return [empty_text]
    items = []
    for raw in text.split("\n"):
        item = raw.strip(" -*0123456789.:\t")
        if item:
            items.append(item)
    return items or [text]


def card(title, lines):
    items = "".join(f"<div class='listitem'>{html.escape(line)}</div>" for line in get_lines(lines))
    st.markdown(f"<div class='card'><div class='ctitle'>{html.escape(title)}</div>{items}</div>", unsafe_allow_html=True)


def metric(label, value, copy):
    st.markdown(
        f"<div class='kpi'><div class='klabel'>{html.escape(label)}</div><div class='kvalue'>{html.escape(value)}</div><div class='kcopy'>{html.escape(copy)}</div></div>",
        unsafe_allow_html=True,
    )


def section_header(eyebrow, title, copy):
    st.markdown(
        f"<div style='margin:.2rem 0 1rem 0;'><div class='eyebrow'>{html.escape(eyebrow)}</div><h2 style='margin:.35rem 0;'>{html.escape(title)}</h2><p class='copy' style='color:var(--muted); max-width:52rem; margin:0;'>{html.escape(copy)}</p></div>",
        unsafe_allow_html=True,
    )


def needs_profile(snapshot):
    profile = snapshot.get("profile") or {}
    return not all([profile.get("name"), profile.get("goal"), profile.get("age"), profile.get("weight"), profile.get("height_cm")])


def fetch_one(api_url, token, path):
    try:
        with httpx.Client(timeout=httpx.Timeout(20.0, connect=5.0)) as client:
            headers = {"Authorization": f"Bearer {token}"} if token else {}
            response = client.get(f"{api_url.rstrip('/')}{path}", headers=headers)
            response.raise_for_status()
            return response.json()
    except Exception:
        return None


@st.cache_data(ttl=20, show_spinner=False)
def fetch_snapshot(api_url, token, version):
    del version
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(SNAPSHOT_PATHS)) as pool:
        futures = {name: pool.submit(fetch_one, api_url, token, path) for name, path in SNAPSHOT_PATHS.items()}
        return {name: future.result() for name, future in futures.items()}


def render_sidebar():
    with st.sidebar:
        st.markdown("<div class='card'><div class='ctitle'>Aurora Health</div><div class='copy' style='color:var(--muted)'>Soft health workspace for women-focused coaching and tracking.</div></div>", unsafe_allow_html=True)
        st.markdown("<div class='eyebrow'>Connection</div>", unsafe_allow_html=True)
        st.session_state.api_url = st.text_input("API Base URL", value=st.session_state.api_url, label_visibility="collapsed")
        if st.button("Check Backend", use_container_width=True):
            health = safe_api("GET", st.session_state.api_url, "/")
            if health:
                st.success(health.get("message", "Backend reachable"))
        if not st.session_state.auth_user:
            st.caption("Sign in from the main area to continue.")
            return
        st.markdown("<div class='eyebrow' style='margin-top:1rem;'>Navigation</div>", unsafe_allow_html=True)
        st.session_state.selected_section = st.radio(
            "Workspace",
            SECTIONS,
            index=SECTIONS.index(st.session_state.selected_section) if st.session_state.selected_section in SECTIONS else 0,
            label_visibility="collapsed",
        )
        if st.button("Refresh Account", use_container_width=True):
            me = safe_api("GET", st.session_state.api_url, "/auth/me", auth=True)
            if me:
                st.session_state.auth_user = me
                bump_snapshot()
                st.rerun()
        if st.button("Logout", use_container_width=True):
            for key in ["auth_token", "auth_user", "plan_result", "coach_result", "memory_search_result"]:
                st.session_state[key] = None
            st.session_state.selected_section = "Home"
            bump_snapshot(clear_outputs=True)
            st.rerun()


def render_auth():
    left, right = st.columns([1.2, 0.8], gap="large")
    with left:
        st.markdown(
            """
            <div class="hero">
                <div class="eyebrow">Aurora Health</div>
                <h1>Health support that feels like a product, not a prototype.</h1>
                <p>Track workouts, cycle health, progress, weekly reports, and AI coaching .</p>
                <div class="pillrow">
                    <span class="pill">Login flow</span>
                    <span class="pill">Cycle-aware</span>
                    <span class="pill">AI plans</span>
                    <span class="pill">Progress cards</span>
                    <span class="pill">Coaching memory</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with right:
        st.markdown("<div class='shell'><div class='eyebrow'>Welcome</div><h2 style='margin:.35rem 0;'>Login or create your account</h2><p class='copy' style='color:var(--muted); margin:0 0 1rem 0;'>The app starts with authentication </p></div>", unsafe_allow_html=True)
        tabs = st.tabs(["Login", "Sign Up", "Clerk Token"])
        with tabs[0]:
            with st.form("login_form"):
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Login", use_container_width=True)
            if submitted:
                auth = safe_api("POST", st.session_state.api_url, "/auth/login", {"email": email, "password": password})
                if auth:
                    st.session_state.auth_token = auth["token"]
                    st.session_state.auth_user = auth
                    bump_snapshot(clear_outputs=True)
                    st.rerun()
        with tabs[1]:
            with st.form("register_form"):
                name = st.text_input("Full name")
                username = st.text_input("Username")
                email = st.text_input("Email", key="register_email")
                password = st.text_input("Password", type="password", key="register_password")
                submitted = st.form_submit_button("Create Account", use_container_width=True)
            if submitted:
                auth = safe_api("POST", st.session_state.api_url, "/auth/register", {"name": name, "username": username, "email": email, "password": password})
                if auth:
                    st.session_state.auth_token = auth["token"]
                    st.session_state.auth_user = auth
                    bump_snapshot(clear_outputs=True)
                    st.rerun()
        with tabs[2]:
            with st.form("clerk_form"):
                clerk_token = st.text_area("Clerk token", height=140)
                submitted = st.form_submit_button("Use Clerk Token", use_container_width=True)
            if submitted and clerk_token.strip():
                st.session_state.auth_token = clerk_token.strip()
                me = safe_api("GET", st.session_state.api_url, "/auth/me", auth=True)
                if me:
                    st.session_state.auth_user = me
                    bump_snapshot(clear_outputs=True)
                    st.rerun()
                st.session_state.auth_token = None


def render_topbar(snapshot):
    profile = snapshot.get("profile") or {}
    progress = snapshot.get("progress") or {}
    streak = snapshot.get("streak") or {}
    name = profile.get("name") or st.session_state.auth_user.get("name") or "there"
    goal = profile.get("goal") or "Set goal"
    trend = progress.get("trend") or "No trend yet"
    momentum = f"{streak.get('current_streak', 0)} day streak"
    st.markdown(
        f"<div class='navtop'><div class='eyebrow'>Dashboard</div><div class='navtitle'>Hi {html.escape(name)}</div><div class='copy' style='color:var(--muted);'>Goal: {html.escape(str(goal))} | Trend: {html.escape(str(trend))} | Momentum: {html.escape(momentum)}</div></div>",
        unsafe_allow_html=True,
    )


def render_profile_form(snapshot, submit_label="Save Profile"):
    profile = snapshot.get("profile") or {}
    lifestyle = profile.get("lifestyle") or {}
    with st.form("profile_form"):
        c1, c2 = st.columns(2, gap="large")
        with c1:
            name = st.text_input("Name", value=profile.get("name", st.session_state.auth_user.get("name", "")))
            age = st.number_input("Age", min_value=13, max_value=100, value=int(profile.get("age") or 26), step=1)
            gender_options = ["female", "male", "other"]
            gender_value = profile.get("gender", "female")
            gender = st.selectbox("Gender", gender_options, index=gender_options.index(gender_value) if gender_value in gender_options else 0)
            weight = st.number_input("Weight (kg)", min_value=20.0, max_value=300.0, value=float(profile.get("weight") or 62.0), step=1.0)
            height_cm = st.number_input("Height (cm)", min_value=100.0, max_value=230.0, value=float(profile.get("height_cm") or 165.0), step=1.0)
            goal_options = ["fat loss", "muscle gain", "strength", "endurance", "general fitness", "pregnancy wellness", "postpartum recovery"]
            goal_value = profile.get("goal", "general fitness")
            goal = st.selectbox("Primary goal", goal_options, index=goal_options.index(goal_value) if goal_value in goal_options else 4)
            level_options = ["beginner", "intermediate", "advanced"]
            level_value = profile.get("level", "beginner")
            level = st.selectbox("Training level", level_options, index=level_options.index(level_value) if level_value in level_options else 0)
        with c2:
            pregnant = st.checkbox("Pregnant", value=bool(profile.get("pregnant", False)))
            postpartum = st.checkbox("Postpartum", value=bool(profile.get("postpartum", False)))
            trimester_values = [None, 1, 2, 3]
            trimester = st.selectbox("Pregnancy trimester", trimester_values, index=trimester_values.index(profile.get("pregnancy_trimester")) if profile.get("pregnancy_trimester") in trimester_values else 0, format_func=lambda value: "Not set" if value is None else str(value))
            postpartum_weeks = st.number_input("Postpartum weeks", min_value=0, max_value=156, value=int(profile.get("postpartum_weeks") or 0), step=1)
            hormonal_concerns = st.multiselect("Hormonal concerns", ["pcos", "thyroid", "acne", "fatigue", "mood swings", "irregular periods", "bloating"], default=profile.get("hormonal_concerns", []))
            dietary_restrictions = st.multiselect("Dietary restrictions", ["vegetarian", "vegan", "gluten-free", "lactose-free", "high-protein", "diabetic-friendly"], default=profile.get("dietary_restrictions", []))
            activity_options = ["low", "moderate", "active", "athletic"]
            activity_default = lifestyle.get("activity_level", "moderate")
            activity_level = st.selectbox("Activity level", activity_options, index=activity_options.index(activity_default) if activity_default in activity_options else 1)
            diet_options = ["balanced", "high-protein", "vegetarian", "vegan", "low-carb", "Mediterranean"]
            diet_default = lifestyle.get("dietary_preference", "balanced")
            dietary_preference = st.selectbox("Diet style", diet_options, index=diet_options.index(diet_default) if diet_default in diet_options else 0)
        c3, c4, c5 = st.columns(3)
        with c3:
            sleep_hours = st.slider("Sleep hours", 0.0, 12.0, float(lifestyle.get("sleep_hours") or 7.0), 0.5)
        with c4:
            water_liters = st.slider("Water liters", 0.0, 5.0, float(lifestyle.get("water_liters") or 2.5), 0.1)
        with c5:
            stress_level = st.slider("Stress level", 1, 10, int(lifestyle.get("stress_level") or 5))
        health_goals = st.multiselect("Lifestyle targets", ["better sleep", "better energy", "cycle support", "weight management", "stress control", "muscle tone", "pregnancy support"], default=lifestyle.get("health_goals", []))
        submitted = st.form_submit_button(submit_label, use_container_width=True)
    if submitted:
        result = safe_api(
            "POST",
            st.session_state.api_url,
            "/profile",
            {
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
            },
            auth=True,
        )
        if result:
            st.success("Profile saved.")
            bump_snapshot()
            st.session_state.selected_section = "Home"
            st.rerun()


def render_home(snapshot):
    profile = snapshot.get("profile") or {}
    streak = snapshot.get("streak") or {}
    progress = snapshot.get("progress") or {}
    women = snapshot.get("women") or {}
    history = snapshot.get("history") or {}
    report = snapshot.get("weekly_report") or {}
    section_header("Overview", "A daily dashboard", "The cards, hierarchy, and a softer wellness look.")
    if needs_profile(snapshot):
        st.info("Finish your profile to unlock better personalization and stronger plans.")
    row = st.columns(4)
    with row[0]:
        metric("Current Goal", profile.get("goal", "Set profile"), "Your main focus")
    with row[1]:
        metric("Streak", f"{streak.get('current_streak', 0)} days", "Consistency first")
    with row[2]:
        metric("Cycle Phase", women.get("predicted_phase", "Unknown"), "Based on saved logs")
    with row[3]:
        metric("Trend", str(progress.get("trend", "No data")), "Recent momentum")
    left, right = st.columns([1.2, 0.8], gap="large")
    with left:
        card("This Week's Focus", [f"Goal: {profile.get('goal', 'Complete your profile')}", f"Energy trend: {progress.get('trend', 'No trend yet')}", f"Next period: {women.get('next_period_start', 'Not enough data')}", f"Workout logs: {len(history.get('workout_logs', []))}", f"Diet logs: {len(history.get('diet_logs', []))}"])
    with right:
        st.markdown("<div class='card' style='text-align:center;'><div class='avatar'></div><div class='ctitle'>Aurora AI Coach</div><div class='copy' style='color:var(--muted)'>..... always yours... .</div></div>", unsafe_allow_html=True)
    progress_cols = st.columns(2, gap="large")
    adherence = float(progress.get("adherence_score") or 0)
    energy = float(progress.get("energy_level") or 0)
    with progress_cols[0]:
        st.markdown("<div class='ctitle'>Adherence</div>", unsafe_allow_html=True)
        st.progress(max(0.0, min(adherence / 10.0, 1.0)))
        st.caption(f"{adherence:.1f}/10")
    with progress_cols[1]:
        st.markdown("<div class='ctitle'>Energy</div>", unsafe_allow_html=True)
        st.progress(max(0.0, min(energy / 10.0, 1.0)))
        st.caption(f"{energy:.1f}/10")
    cards = st.columns(3, gap="large")
    with cards[0]:
        card("Workout Plan Preview", (st.session_state.plan_result or {}).get("workout"),)
    with cards[1]:
        card("Diet Plan Preview", (st.session_state.plan_result or {}).get("diet"),)
    with cards[2]:
        card("Suggested Next Steps", report.get("recommendations") or women.get("nutrition_focus") or ["Generate a plan and log progress to unlock recommendations."])
    history_rows = progress.get("history") or []
    if history_rows:
        frame = pd.DataFrame(history_rows).sort_values("date")
        series = [col for col in ["energy_level", "adherence_score", "workout_minutes", "weight"] if col in frame.columns]
        if "date" in frame.columns and series:
            frame["date"] = pd.to_datetime(frame["date"])
            if go:
                fig = go.Figure()
                colors = ["#7C6CF6", "#F59EAE", "#22C55E", "#0EA5E9"]
                for idx, column in enumerate(series):
                    fig.add_trace(go.Scatter(x=frame["date"], y=frame[column], mode="lines+markers", name=column.replace("_", " ").title(), line=dict(color=colors[idx % len(colors)], width=3)))
                fig.update_layout(margin=dict(t=16, b=16, l=0, r=0), height=320, template="plotly_white", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.line_chart(frame.set_index("date")[series], use_container_width=True)


def render_plans(snapshot):
    profile = snapshot.get("profile") or {}
    women = snapshot.get("women") or {}
    lifestyle = profile.get("lifestyle") or {}
    section_header("Plans", "Generate a plan that reads well", "Plan generation is AI-backed,")
    with st.form("plan_form"):
        c1, c2, c3 = st.columns(3, gap="large")
        with c1:
            plan_goal = st.selectbox("Plan goal", ["fat loss", "muscle gain", "strength", "endurance", "general fitness", "pregnancy wellness", "postpartum recovery"])
            plan_level = st.selectbox("Training level", ["beginner", "intermediate", "advanced"])
            plan_weight = st.number_input("Current weight", min_value=20.0, max_value=300.0, value=float(profile.get("weight") or 62.0), step=1.0)
        with c2:
            options = ["female", "male", "other"]
            gender_value = profile.get("gender", "female")
            plan_gender = st.selectbox("Context", options, index=options.index(gender_value) if gender_value in options else 0)
            phase_options = ["", "menstrual", "follicular", "ovulation", "luteal"]
            phase = women.get("predicted_phase", "")
            phase = phase if phase in phase_options else ""
            cycle_phase = st.selectbox("Cycle phase", phase_options, index=phase_options.index(phase))
            pregnant_plan = st.checkbox("Pregnancy-aware", value=bool(profile.get("pregnant", False)))
        with c3:
            postpartum_plan = st.checkbox("Postpartum-aware", value=bool(profile.get("postpartum", False)))
            trimester_values = [None, 1, 2, 3]
            trimester_plan = st.selectbox("Trimester", trimester_values, index=trimester_values.index(profile.get("pregnancy_trimester")) if profile.get("pregnancy_trimester") in trimester_values else 0, format_func=lambda value: "Not set" if value is None else str(value))
            postpartum_weeks = st.number_input("Postpartum weeks", min_value=0, max_value=156, value=int(profile.get("postpartum_weeks") or 0), step=1)
        hormonal_plan = st.multiselect("Hormonal concerns", ["pcos", "thyroid", "fatigue", "irregular periods", "mood swings", "bloating"], default=profile.get("hormonal_concerns", []))
        restrictions = st.multiselect("Dietary restrictions", ["vegetarian", "vegan", "gluten-free", "lactose-free", "diabetic-friendly"], default=profile.get("dietary_restrictions", []))
        submitted = st.form_submit_button("Generate Aurora Plan", use_container_width=True)
    if submitted:
        with st.spinner("Generating your plan..."):
            st.session_state.plan_result = safe_api("POST", st.session_state.api_url, "/generate-plan", {"goal": plan_goal, "level": plan_level, "weight": plan_weight, "gender": plan_gender, "cycle_phase": cycle_phase or None, "age": profile.get("age"), "activity_level": lifestyle.get("activity_level"), "pregnant": pregnant_plan, "postpartum": postpartum_plan, "pregnancy_trimester": trimester_plan, "postpartum_weeks": postpartum_weeks if postpartum_plan else None, "hormonal_concerns": hormonal_plan, "dietary_restrictions": restrictions})
    plan = st.session_state.plan_result
    if not plan:
        st.markdown("<div class='empty'>No plan generated yet.</div>", unsafe_allow_html=True)
        return
    row = st.columns(3, gap="large")
    with row[0]:
        card("Workout Plan", plan.get("workout"))
    with row[1]:
        card("Diet Plan", plan.get("diet"))
    with row[2]:
        card("Women's Health Guidance", plan.get("women_health"),)
    st.download_button("Download Plan JSON", data=json.dumps(plan, indent=2).encode("utf-8"), file_name="aurora_plan.json", mime="application/json", use_container_width=True)


def render_women_health(snapshot):
    women = snapshot.get("women") or {}
    section_header("Women's Health", "Cycle-aware view with hierarchy", ".")
    left, right = st.columns([0.95, 1.05], gap="large")
    with left:
        with st.form("period_form"):
            start_date = st.date_input("Period start", value=date.today())
            end_date = st.date_input("Period end", value=date.today())
            symptoms = st.multiselect("Symptoms", ["cramps", "fatigue", "acne", "mood swings", "bloating", "headache", "dizziness"])
            flow_level = st.selectbox("Flow", ["light", "moderate", "heavy"])
            mood = st.selectbox("Mood", ["stable", "low", "anxious", "irritable", "energized"])
            cravings = st.multiselect("Cravings", ["sweet", "salty", "carbs", "chocolate", "none"])
            notes = st.text_area("Notes", placeholder="Pain, sleep, cravings, spotting, or context Aurora should remember.")
            submitted = st.form_submit_button("Save Period Log", use_container_width=True)
        if submitted:
            result = safe_api("POST", st.session_state.api_url, "/women-health/log-period", {"start_date": start_date.isoformat(), "end_date": end_date.isoformat(), "symptoms": symptoms, "flow_level": flow_level, "mood": mood, "cravings": [] if "none" in cravings else cravings, "notes": notes}, auth=True)
            if result:
                st.success("Period log saved.")
                bump_snapshot()
                st.rerun()
    with right:
        stats = st.columns(3)
        with stats[0]:
            metric("Average Cycle", str(women.get("average_cycle_length") or "n/a"), "Days between cycles")
        with stats[1]:
            metric("Average Period", str(women.get("average_period_length") or "n/a"), "Days logged")
        with stats[2]:
            metric("Irregularity", str(women.get("irregularity_score") or "unknown"), "Signal, not diagnosis")
        c1, c2 = st.columns(2, gap="large")
        with c1:
            card("Forecast", [f"Predicted phase: {women.get('predicted_phase', 'unknown')}", f"Next period: {women.get('next_period_start', 'unknown')}"])
            card("Nutrition Focus", women.get("nutrition_focus"))
        with c2:
            card("Workout Focus", women.get("workout_focus"))
            concerns = women.get("possible_concerns") or []
            if concerns:
                card("Flags to Notice", [f"{item.get('flag')}: {item.get('detail')}" for item in concerns])
        if women.get("recent_logs"):
            st.dataframe(pd.DataFrame(women["recent_logs"]), use_container_width=True)
        if women.get("disclaimer"):
            st.info(women["disclaimer"])


def render_tracking():
    section_header("Daily Tracking", "Two clean logging flows", "Workout and nutrition logging .")
    left, right = st.columns(2, gap="large")
    with left:
        with st.form("workout_log_form"):
            workout_type = st.selectbox("Workout type", ["strength", "cardio", "walking", "mobility", "yoga", "sports", "recovery"])
            duration_minutes = st.slider("Duration minutes", 0, 180, 40)
            intensity = st.select_slider("Intensity", options=["low", "moderate", "high"], value="moderate")
            completed = st.radio("Completed", [True, False], format_func=lambda value: "Yes" if value else "No", horizontal=True)
            notes = st.text_area("Workout notes", placeholder="Energy, soreness, pain, performance, or favorite movement.")
            submitted = st.form_submit_button("Save Workout Log", use_container_width=True)
        if submitted:
            result = safe_api("POST", st.session_state.api_url, "/tracking/workout", {"workout_type": workout_type, "duration_minutes": duration_minutes, "intensity": intensity, "completed": completed, "notes": notes}, auth=True)
            if result:
                st.success("Workout log saved.")
                bump_snapshot()
                st.rerun()
    with right:
        with st.form("diet_log_form"):
            meals_followed = st.select_slider("Meals followed", options=[0, 1, 2, 3, 4, 5, 6], value=3)
            hydration_liters = st.slider("Hydration liters", 0.0, 5.0, 2.4, 0.1)
            protein_grams = st.slider("Protein grams", 0, 220, 90)
            cravings = st.multiselect("Cravings", ["sweet", "salty", "fried", "late-night", "carbs", "none"])
            notes = st.text_area("Diet notes", placeholder="Hunger, digestion, supplements, cravings, or meal quality.")
            submitted = st.form_submit_button("Save Diet Log", use_container_width=True)
        if submitted:
            result = safe_api("POST", st.session_state.api_url, "/tracking/diet", {"meals_followed": meals_followed, "hydration_liters": hydration_liters, "protein_grams": protein_grams, "cravings": [] if "none" in cravings else cravings, "notes": notes}, auth=True)
            if result:
                st.success("Diet log saved.")
                bump_snapshot()
                st.rerun()


def render_progress(snapshot):
    progress = snapshot.get("progress") or {}
    streak = snapshot.get("streak") or {}
    section_header("Progress", "Mood, adherence, and consistency", "Progress, feedback, and streak check-ins .")
    left, right = st.columns(2, gap="large")
    with left:
        with st.form("progress_form"):
            weight = st.number_input("Weight (optional)", min_value=20.0, max_value=300.0, value=62.0, step=1.0)
            energy_level = st.slider("Energy", 1, 10, 6)
            mood = st.selectbox("Mood", ["strong", "steady", "low", "stressed", "motivated", "drained"])
            workout_minutes = st.slider("Workout minutes", 0, 180, 35)
            adherence_score = st.slider("Adherence score", 1, 10, 7)
            notes = st.text_area("Progress notes", placeholder="What improved, what felt hard, what should change next week.")
            submitted = st.form_submit_button("Save Progress Log", use_container_width=True)
        if submitted:
            result = safe_api("POST", st.session_state.api_url, "/progress/log", {"weight": weight, "energy_level": energy_level, "mood": mood, "workout_minutes": workout_minutes, "adherence_score": adherence_score, "notes": notes}, auth=True)
            if result:
                st.success("Progress log saved.")
                bump_snapshot()
                st.rerun()
        with st.form("feedback_form"):
            category = st.selectbox("Feedback category", ["plan", "coach", "cycle", "diet", "workout", "app experience"])
            feedback = st.text_area("Feedback", placeholder="Tell Aurora what worked and what should change.")
            rating = st.slider("Rating", 1, 10, 7)
            submitted = st.form_submit_button("Save Feedback", use_container_width=True)
        if submitted:
            result = safe_api("POST", st.session_state.api_url, "/tracking/feedback", {"category": category, "feedback": feedback, "rating": rating}, auth=True)
            if result:
                st.success("Feedback saved.")
                bump_snapshot()
    with right:
        stats = st.columns(3)
        with stats[0]:
            metric("Trend", str(progress.get("trend", "no-data")), "Current momentum")
        with stats[1]:
            metric("Entries", str(progress.get("entries", 0)), "Saved logs")
        with stats[2]:
            metric("Streak", f"{streak.get('current_streak', 0)} days", "Daily rhythm")
        history_rows = progress.get("history") or []
        if history_rows:
            frame = pd.DataFrame(history_rows).sort_values("date")
            series = [col for col in ["energy_level", "adherence_score", "workout_minutes", "weight"] if col in frame.columns]
            if series:
                st.line_chart(frame.set_index("date")[series], use_container_width=True)
            st.dataframe(frame, use_container_width=True)
        with st.form("streak_form"):
            workout_completed = st.checkbox("Workout completed today", value=True)
            nutrition_completed = st.checkbox("Nutrition goals completed today")
            journal_note = st.text_area("Daily note", placeholder="One sentence is enough.")
            submitted = st.form_submit_button("Daily Check-In", use_container_width=True)
        if submitted:
            result = safe_api("POST", st.session_state.api_url, "/streaks/check-in", {"workout_completed": workout_completed, "nutrition_completed": nutrition_completed, "journal_note": journal_note}, auth=True)
            if result:
                st.success("Daily check-in saved.")
                bump_snapshot()
                st.rerun()


def render_memory_history(snapshot):
    history = snapshot.get("history") or {}
    report = snapshot.get("weekly_report") or {}
    section_header("Memory & History", "Search and export ", "Search results")
    cols = st.columns([1.2, 0.8], gap="large")
    with cols[0]:
        with st.form("memory_search_form"):
            query = st.text_input("Search Aurora memory", placeholder="low energy before period, protein consistency, walking streak")
            top_k = st.slider("Results", 1, 10, 5)
            submitted = st.form_submit_button("Search Memory", use_container_width=True)
        if submitted and query.strip():
            st.session_state.memory_search_result = safe_api("POST", st.session_state.api_url, "/tracking/memory-search", {"query": query.strip(), "top_k": top_k}, auth=True)
    with cols[1]:
        package = {"history": history, "weekly_report": report, "exported_on": date.today().isoformat()}
        st.download_button("Download Full Health Data", data=json.dumps(package, indent=2).encode("utf-8"), file_name="aurora_health_data.json", mime="application/json", use_container_width=True)
    if st.session_state.memory_search_result:
        result = st.session_state.memory_search_result
        card("Search Results", [f"Query: {result.get('query', '')}"])
        rows = result.get("results") or []
        if rows:
            st.dataframe(pd.DataFrame(rows), use_container_width=True)
    for title, key in [("Workout History", "workout_logs"), ("Diet History", "diet_logs"), ("Progress History", "progress_logs"), ("Period History", "period_logs"), ("Semantic Memory", "recent_memories")]:
        rows = history.get(key) or []
        with st.expander(f"{title} ({len(rows)})", expanded=False):
            if rows:
                st.dataframe(pd.DataFrame(rows), use_container_width=True)
            else:
                st.caption("No data saved yet.")


def render_weekly_report(snapshot):
    report = snapshot.get("weekly_report")
    section_header("Weekly Report", "A  weekly summary", "Wins, risks, and recommendations .")
    if not report:
        st.markdown("<div class='empty'>Weekly report is not available yet.</div>", unsafe_allow_html=True)
        return
    cols = st.columns(3, gap="large")
    with cols[0]:
        card("Wins", report.get("wins"))
    with cols[1]:
        card("Risks", report.get("risks"))
    with cols[2]:
        card("Recommendations", report.get("recommendations"))
    card("Summary", report.get("summary"))
    st.caption(f"Report window: {report.get('period_start')} to {report.get('period_end')}")


def render_coach():
    section_header("Aurora Coach", "Focused coaching screen", "The AI response central .")
    with st.form("coach_form"):
        message = st.text_area("Ask Aurora", placeholder="I lose motivation during luteal phase and miss protein targets. How should my next 7 days change?", height=160)
        submitted = st.form_submit_button("Get Coaching", use_container_width=True)
    if submitted:
        with st.spinner("Preparing coaching guidance..."):
            st.session_state.coach_result = safe_api("POST", st.session_state.api_url, "/progress/coach", {"message": message}, auth=True)
    coach = st.session_state.coach_result
    if not coach:
        st.markdown("<div class='empty'>Ask a question to receive coaching grounded in your saved data.</div>", unsafe_allow_html=True)
        return
    cols = st.columns(3, gap="large")
    with cols[0]:
        card("Aurora Reply", coach.get("reply"))
    with cols[1]:
        card("Insights", coach.get("insights"))
    with cols[2]:
        card("Next Steps", coach.get("next_steps"))


init_state()
st.markdown("<div class='watermark'>Gauri_mshra</div>", unsafe_allow_html=True)
render_sidebar()
if not st.session_state.auth_user:
    render_auth()
    st.stop()

with st.spinner("Loading Aurora workspace..."):
    snapshot = fetch_snapshot(st.session_state.api_url, st.session_state.auth_token or "", st.session_state.snapshot_version)

render_topbar(snapshot)
if needs_profile(snapshot) and st.session_state.selected_section == "Home":
    st.info("Onboarding is incomplete. Open the Profile section to finish your basic health context.")

section = st.session_state.selected_section
if section == "Home":
    render_home(snapshot)
elif section == "Plans":
    render_plans(snapshot)
elif section == "Progress":
    render_progress(snapshot)
elif section == "Daily Tracking":
    render_tracking()
elif section == "Women's Health":
    render_women_health(snapshot)
elif section == "Memory & History":
    render_memory_history(snapshot)
elif section == "Weekly Report":
    render_weekly_report(snapshot)
elif section == "Aurora Coach":
    render_coach()
elif section == "Profile":
    section_header("Profile", "Personal details and health context", " onboarding step .")
    render_profile_form(snapshot, submit_label="Save Profile")
