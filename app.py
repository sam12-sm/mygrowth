import streamlit as st
import json
import os
from datetime import date, datetime, timedelta
import plotly.graph_objects as go
import gspread
from google.oauth2.service_account import Credentials

# ── Config ──────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MyGrowth – Habit Tracker",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

SHEET_NAME = "MyGrowth Habit Tracker"
SCOPES = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

DEFAULT_DATA = {
    "goals": {"1_week": "", "1_month": "", "6_months": "", "1_year": "", "5_year": "", "10_year": ""},
    "want_to_change": "",
    "want_to_accomplish": "",
    "weekly_habits": ["Wake up on time", "Read / Study", "Exercise / Move", "Drink enough water", "No social media before study", "Write 1 good thing"],
    "weekly_log": {},
    "challenge": {"habit": "", "start_date": "", "completed_days": []},
    "wheel": {"Study Habits": 5, "Sleep & Health": 5, "Mindset & Focus": 5, "Confidence": 5, "Time Management": 5, "Relationships": 5},
    "wheel_goals": {"Study Habits": 7, "Sleep & Health": 7, "Mindset & Focus": 7, "Confidence": 7, "Time Management": 7, "Relationships": 7},
    "timebox": {},
}

# ── Google Sheets connection ──────────────────────────────────────────────────
@st.cache_resource
def get_sheet():
    try:
        creds = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"], scopes=SCOPES
        )
        client = gspread.authorize(creds)
        sheet = client.open(SHEET_NAME).sheet1
        return sheet
    except Exception as e:
        st.error(f"Could not connect to Google Sheets: {e}")
        return None

# ── Data helpers ─────────────────────────────────────────────────────────────
def load_data():
    # Try Google Sheets first
    sheet = get_sheet()
    if sheet:
        try:
            val = sheet.cell(1, 1).value
            if val:
                return json.loads(val)
        except Exception:
            pass
    # Fallback to local file
    if os.path.exists("habit_data.json"):
        with open("habit_data.json", "r") as f:
            return json.load(f)
    import copy
    return copy.deepcopy(DEFAULT_DATA)

def save_data(data):
    # Save to Google Sheets
    sheet = get_sheet()
    if sheet:
        try:
            sheet.update("A1", [[json.dumps(data)]])
        except Exception as e:
            st.warning(f"Cloud save failed: {e}. Saving locally instead.")
    # Always save locally as backup
    with open("habit_data.json", "w") as f:
        json.dump(data, f, indent=2)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* ── Global text fix — works on both light and dark themes ── */
    .stApp { background-color: #f0f2f6 !important; }
    .stApp, .stApp p, .stApp li, .stApp label,
    .stApp span, .stApp div { color: #1a1a2e !important; }
    .stMarkdown, .stMarkdown p { color: #1a1a2e !important; }
    .stTextInput label, .stTextArea label,
    .stSlider label, .stSelectbox label,
    .stDateInput label, .stRadio label { color: #1a1a2e !important; }
    .stCaption, [data-testid="stCaptionContainer"] p { color: #555577 !important; }
    h1, h2, h3, h4 { color: #1a1a2e !important; }
    /* Fix metric text */
    [data-testid="stMetricValue"] { color: #1a1a2e !important; }
    [data-testid="stMetricLabel"] { color: #555577 !important; }
    [data-testid="stMetricDelta"] { color: #38b2ac !important; }
    /* Fix expander */
    .streamlit-expanderHeader { color: #1a1a2e !important; }
    /* Fix info/success/warning boxes */
    .stAlert p { color: #1a1a2e !important; }
    /* Fix sidebar text back to light since sidebar is dark */
    [data-testid="stSidebar"] *,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] span { color: #e0e0e0 !important; }

    /* ── Mobile-first base ── */
    .main .block-container {
        padding: 0.8rem 0.8rem 2rem 0.8rem !important;
        max-width: 100% !important;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] { background: #1a1a2e; }
    [data-testid="stSidebar"] * { color: #e0e0e0 !important; }
    [data-testid="stSidebar"] .stRadio label {
        font-size: 1.1rem; padding: 8px 4px; display: block;
    }

    /* ── Section headers ── */
    .section-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white; padding: 14px 18px; border-radius: 12px;
        margin-bottom: 16px; font-size: 1.15rem; font-weight: 700;
        line-height: 1.3;
    }
    .tb-header {
        background: linear-gradient(135deg, #f6d365 0%, #fda085 100%);
        color: white; padding: 14px 18px; border-radius: 12px;
        margin-bottom: 16px; font-size: 1.15rem; font-weight: 700;
    }

    /* ── Cards ── */
    .card {
        background: #f8f9ff; border-radius: 12px; padding: 14px 16px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.07); margin-bottom: 12px;
        border-left: 5px solid #667eea; font-size: 0.95rem;
        color: #1a1a2e !important;
    }
    .card * { color: #1a1a2e !important; }
    .card b, .card strong { color: #1a1a2e !important; font-weight: 700; }
    .card i { color: #3a3a5e !important; }
    .card-green  { border-left-color: #38b2ac; background: #f0fafa; }
    .card-orange { border-left-color: #ed8936; background: #fff8f0; }
    .card-red    { border-left-color: #e53e3e; background: #fff5f5; }
    .habit-row { color: #1a1a2e !important; }
    .habit-row * { color: #1a1a2e !important; }

    /* ── Stat boxes — stack 2x2 on mobile ── */
    .stat-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 10px;
        margin-bottom: 16px;
    }
    .stat-box {
        background: linear-gradient(135deg, #667eea, #764ba2);
        border-radius: 12px; padding: 14px 8px;
        text-align: center; color: white;
    }
    .stat-box .num { font-size: 1.7rem; font-weight: 800; line-height: 1.1; }
    .stat-box .lbl { font-size: 0.75rem; opacity: 0.9; margin-top: 4px; }

    /* ── Buttons — bigger touch targets on mobile ── */
    .stButton > button {
        min-height: 44px !important;
        font-size: 1rem !important;
        border-radius: 8px !important;
        width: 100%;
    }

    /* ── Column padding ── */
    div[data-testid="column"] { padding: 3px !important; }

    /* ── Inputs ── */
    .stTextInput input, .stTextArea textarea {
        font-size: 1rem !important;
        border-radius: 8px !important;
    }

    /* ── Time planner ── */
    .time-row-hour {
        background: #edf2f7; border-radius: 6px; padding: 4px 6px;
        font-weight: 700; color: #2d3748; font-size: 0.78rem;
        white-space: nowrap;
    }
    .time-row-half {
        background: #f7fafc; border-radius: 6px; padding: 4px 6px;
        color: #718096; font-size: 0.75rem; white-space: nowrap;
    }

    /* ── Habit tracker rows ── */
    .habit-row {
        background: #f8f9ff; border-radius: 10px; padding: 10px 12px;
        margin-bottom: 8px; border-left: 4px solid #667eea;
        font-size: 0.95rem;
    }

    /* ── 30-day calendar — tighter on mobile ── */
    div[data-testid="column"] .stButton > button {
        padding: 6px 2px !important;
        font-size: 0.78rem !important;
        min-height: 40px !important;
    }

    /* ── Metrics ── */
    [data-testid="stMetric"] {
        background: #f8f9ff; border-radius: 10px;
        padding: 10px 12px !important;
    }

    /* ── Streamlit default spacer reduction ── */
    .element-container { margin-bottom: 4px !important; }
    h1 { font-size: 1.5rem !important; }
    h2 { font-size: 1.2rem !important; }
    h3 { font-size: 1.05rem !important; }

    /* ── Responsive: wider screens get more padding ── */
    @media (min-width: 768px) {
        .main .block-container { padding: 1.5rem 2rem 2rem 2rem !important; }
        .stat-box .num { font-size: 2.2rem; }
        .stat-box .lbl { font-size: 0.85rem; }
        .section-header { font-size: 1.4rem; padding: 16px 24px; }
    }
</style>
""", unsafe_allow_html=True)

# ── Load state ────────────────────────────────────────────────────────────────
if "data" not in st.session_state:
    st.session_state.data = load_data()

d = st.session_state.data

# ── Sidebar navigation ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🌱 MyGrowth")
    st.markdown("---")
    page = st.radio("Navigate", [
        "🏠 Dashboard",
        "⏱️ Daily Timebox",
        "🎯 Goal Setting",
        "✅ Weekly Tracker",
        "🔥 30-Day Challenge",
        "🌀 Wheel of Growth",
    ])
    st.markdown("---")
    today_str = date.today().strftime("%A, %d %b %Y")
    st.markdown(f"**📅 {today_str}**")

# ══════════════════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ══════════════════════════════════════════════════════════════════
if page == "🏠 Dashboard":
    st.markdown('<div class="section-header">🏠 Dashboard — Your Growth Overview</div>', unsafe_allow_html=True)

    week_key = date.today().strftime("%Y-W%W")
    today_key = date.today().isoformat()
    weekly_log = d["weekly_log"].get(week_key, {})
    habits = d["weekly_habits"]

    # Stats row
    total_possible = len(habits) * 7
    completed_week = sum(len(v) for v in weekly_log.values())
    today_done = sum(1 for h in habits if today_key in weekly_log.get(h, []))
    challenge_done = len(d["challenge"]["completed_days"])

    pct = int(completed_week / total_possible * 100) if total_possible else 0
    avg_wheel = int(sum(d["wheel"].values()) / len(d["wheel"]))
    st.markdown(f'''
    <div class="stat-grid">
        <div class="stat-box"><div class="num">{today_done}/{len(habits)}</div><div class="lbl">Today's Habits</div></div>
        <div class="stat-box"><div class="num">{pct}%</div><div class="lbl">This Week</div></div>
        <div class="stat-box"><div class="num">{challenge_done}/30</div><div class="lbl">30-Day Challenge</div></div>
        <div class="stat-box"><div class="num">{avg_wheel}/10</div><div class="lbl">Growth Score</div></div>
    </div>
    ''', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Single column layout — stacks naturally on mobile
    st.markdown("### ✅ Today's Habits")
    for habit in habits:
        done = today_key in weekly_log.get(habit, [])
        icon = "✅" if done else "⬜"
        st.markdown(f'<div class="habit-row">{icon} {habit}</div>', unsafe_allow_html=True)

    st.markdown("### 🎯 Nearest Goals")
    if d["goals"]["1_week"]:
        st.markdown(f'<div class="card card-green">📅 <b>1 Week:</b> {d["goals"]["1_week"]}</div>', unsafe_allow_html=True)
    if d["goals"]["1_month"]:
        st.markdown(f'<div class="card card-orange">📅 <b>1 Month:</b> {d["goals"]["1_month"]}</div>', unsafe_allow_html=True)

    st.markdown("### 🔥 30-Day Challenge Progress")
    ch = d["challenge"]
    if ch["habit"]:
        st.markdown(f"**Habit:** {ch['habit']}")
        progress = len(ch["completed_days"]) / 30
        st.progress(progress)
        st.caption(f"{len(ch['completed_days'])} / 30 days completed")
    else:
        st.info("No challenge set yet. Go to 🔥 30-Day Challenge to start one!")

    st.markdown("### 💡 Today's Motivation")
    quotes = [
        "You don't have to be great to start. But you have to start to be great.",
        "Small steps every day lead to big changes over time.",
        "Don't break the chain. Show up for yourself today.",
        "Every habit you keep is a vote for the person you want to become.",
        "Progress, not perfection.",
    ]
    import hashlib
    idx = int(hashlib.md5(today_key.encode()).hexdigest(), 16) % len(quotes)
    st.markdown(f'<div class="card">💬 <i>"{quotes[idx]}"</i></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# PAGE: GOAL SETTING
# ══════════════════════════════════════════════════════════════════
elif page == "🎯 Goal Setting":
    st.markdown('<div class="section-header">🎯 Goal Setting — Know Where You\'re Going</div>', unsafe_allow_html=True)

    d["want_to_change"] = st.text_area("One thing I really want to change about myself:", value=d["want_to_change"], height=80)
    d["want_to_accomplish"] = st.text_area("What do I want to accomplish?", value=d["want_to_accomplish"], height=80)

    st.markdown("### 🗓️ My Goals by Timeframe")
    timeframes = [
        ("1_week", "📅 1 Week Goal"),
        ("1_month", "📅 1 Month Goal"),
        ("6_months", "📆 6 Months Goal"),
        ("1_year", "📆 1 Year Goal"),
        ("5_year", "🗓️ 5 Year Goal"),
        ("10_year", "🗓️ 10 Year Goal"),
    ]
    for key, label in timeframes:
        d["goals"][key] = st.text_input(label, value=d["goals"][key], key=f"goal_{key}")

    if st.button("💾 Save Goals", type="primary"):
        save_data(d)
        st.success("Goals saved! 🎉")

# ══════════════════════════════════════════════════════════════════
# PAGE: WEEKLY TRACKER
# ══════════════════════════════════════════════════════════════════
elif page == "✅ Weekly Tracker":
    st.markdown('<div class="section-header">✅ Weekly Habit Tracker — Don\'t Break the Chain!</div>', unsafe_allow_html=True)

    week_key = date.today().strftime("%Y-W%W")
    if week_key not in d["weekly_log"]:
        d["weekly_log"][week_key] = {}
    log = d["weekly_log"][week_key]

    # Get this week's dates (Mon–Sun)
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    week_dates = [monday + timedelta(days=i) for i in range(7)]
    day_labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    st.markdown("#### ✏️ Customize your habits")
    new_habits = []
    cols = st.columns(3)
    for i, habit in enumerate(d["weekly_habits"]):
        with cols[i % 3]:
            new_val = st.text_input(f"Habit {i+1}", value=habit, key=f"habit_name_{i}")
            new_habits.append(new_val)
    d["weekly_habits"] = new_habits

    st.markdown("---")
    st.markdown("#### 📅 This Week's Tracker")

    # Header row
    header = ["**Habit**"] + [f"**{d}**" for d in day_labels] + ["**Total**"]
    hcols = st.columns([3] + [1]*7 + [1])
    for col, h in zip(hcols, header):
        col.markdown(h)

    total_done = 0
    for habit in d["weekly_habits"]:
        if not habit:
            continue
        if habit not in log:
            log[habit] = []
        row_cols = st.columns([3] + [1]*7 + [1])
        row_cols[0].markdown(f"🔹 {habit}")
        habit_count = 0
        for j, (day_date, day_label) in enumerate(zip(week_dates, day_labels)):
            day_iso = day_date.isoformat()
            is_done = day_iso in log[habit]
            # Allow all days in the current week to be ticked (including future Sat/Sun)
            is_outside_week = day_date > (monday + timedelta(days=6))
            btn_label = "✅" if is_done else "⬜"
            if not is_outside_week:
                if row_cols[j+1].button(btn_label, key=f"btn_{habit}_{day_iso}", help=day_label):
                    if is_done:
                        log[habit].remove(day_iso)
                    else:
                        log[habit].append(day_iso)
                    save_data(d)
                    st.rerun()
            else:
                row_cols[j+1].markdown("—")
            if is_done:
                habit_count += 1
        row_cols[8].markdown(f"**{habit_count}/7**")
        total_done += habit_count

    st.markdown("---")
    total_possible = len([h for h in d["weekly_habits"] if h]) * 7
    pct = int(total_done / total_possible * 100) if total_possible else 0
    col1, col2 = st.columns(2)
    col1.metric("✅ Total Completed This Week", f"{total_done} / {total_possible}")
    col2.metric("📊 Weekly Completion Rate", f"{pct}%")
    st.progress(pct / 100)

    if st.button("💾 Save Tracker", type="primary"):
        save_data(d)
        st.success("Saved!")

# ══════════════════════════════════════════════════════════════════
# PAGE: 30-DAY CHALLENGE
# ══════════════════════════════════════════════════════════════════
elif page == "🔥 30-Day Challenge":
    st.markdown('<div class="section-header">🔥 30-Day Challenge — One Habit. 30 Days. Transform.</div>', unsafe_allow_html=True)

    ch = d["challenge"]

    col1, col2 = st.columns([2, 1])
    with col1:
        ch["habit"] = st.text_input("🎯 My 30-Day Habit Commitment:", value=ch["habit"],
                                     placeholder="e.g. Read 20 pages every day")
    with col2:
        if not ch["start_date"]:
            ch["start_date"] = date.today().isoformat()
        start = st.date_input("Start date:", value=date.fromisoformat(ch["start_date"]))
        ch["start_date"] = start.isoformat()

    if st.button("🔄 Reset Challenge", help="This will clear all completed days"):
        ch["completed_days"] = []
        save_data(d)
        st.success("Challenge reset!")
        st.rerun()

    st.markdown("---")
    st.markdown("### 📅 30-Day Streak Calendar")
    st.caption("Click a day to mark it complete. Keep the chain going!")

    start_dt = date.fromisoformat(ch["start_date"])
    today = date.today()

    # 3 rows of 10 days
    for row in range(3):
        cols = st.columns(10)
        for col_i in range(10):
            day_num = row * 10 + col_i + 1
            day_date = start_dt + timedelta(days=day_num - 1)
            day_iso = day_date.isoformat()
            is_done = day_iso in ch["completed_days"]
            is_future = day_date > today
            is_today = day_date == today

            with cols[col_i]:
                if is_done:
                    label = f"✅\n{day_num}"
                    btn_type = "primary"
                elif is_today:
                    label = f"🔆\n{day_num}"
                    btn_type = "secondary"
                elif is_future:
                    label = f"·\n{day_num}"
                    btn_type = "secondary"
                else:
                    label = f"⬜\n{day_num}"
                    btn_type = "secondary"

                if not is_future:
                    if st.button(label, key=f"day_{day_num}", use_container_width=True):
                        if is_done:
                            ch["completed_days"].remove(day_iso)
                        else:
                            ch["completed_days"].append(day_iso)
                        save_data(d)
                        st.rerun()
                else:
                    st.button(label, key=f"day_{day_num}", disabled=True, use_container_width=True)

    st.markdown("---")
    done_count = len(ch["completed_days"])
    col1, col2, col3 = st.columns(3)
    col1.metric("✅ Days Completed", f"{done_count} / 30")
    col2.metric("📊 Progress", f"{int(done_count/30*100)}%")

    # Current streak calculation
    streak = 0
    check = today
    while check.isoformat() in ch["completed_days"]:
        streak += 1
        check -= timedelta(days=1)
    col3.metric("🔥 Current Streak", f"{streak} days")

    st.progress(done_count / 30)

    st.markdown("---")
    st.markdown("### 📝 Daily Check-In")
    col_m, col_e = st.columns(2)
    with col_m:
        st.markdown("**🌅 Morning: Today I will focus on...**")
        morning = st.text_area("", height=100, key="morning_note", placeholder="Write your intention for today...")
    with col_e:
        st.markdown("**🌙 Evening: How did it go?**")
        evening = st.text_area("", height=100, key="evening_note", placeholder="Reflect on your day...")

    if st.button("💾 Save Challenge", type="primary"):
        save_data(d)
        st.success("Challenge saved! 🔥")

# ══════════════════════════════════════════════════════════════════
# PAGE: WHEEL OF GROWTH
# ══════════════════════════════════════════════════════════════════
elif page == "🌀 Wheel of Growth":
    st.markdown('<div class="section-header">🌀 Wheel of Self-Growth — Score Yourself Honestly</div>', unsafe_allow_html=True)

    areas = {
        "Study Habits": "Do I study regularly, focus well, and review my notes?",
        "Sleep & Health": "Do I sleep 7-9 hours, drink water, and eat reasonably well?",
        "Mindset & Focus": "Do I stay positive, avoid negative self-talk, and push through?",
        "Confidence": "Do I believe in myself and try new things even when scared?",
        "Time Management": "Do I finish tasks on time and avoid last-minute panic?",
        "Relationships": "Am I kind, supportive, and a good friend/family member?",
    }

    # Radar chart first — looks great on mobile
    st.markdown("### 🕸️ Your Growth Radar")
    categories = list(areas.keys())
    current_vals = [d["wheel"][a] for a in categories]
    goal_vals = [d["wheel_goals"][a] for a in categories]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=current_vals + [current_vals[0]],
        theta=categories + [categories[0]],
        fill='toself', name='Current',
        line=dict(color='#667eea', width=2),
        fillcolor='rgba(102,126,234,0.25)',
    ))
    fig.add_trace(go.Scatterpolar(
        r=goal_vals + [goal_vals[0]],
        theta=categories + [categories[0]],
        fill='toself', name='4-Week Goal',
        line=dict(color='#38b2ac', width=2, dash='dash'),
        fillcolor='rgba(56,178,172,0.1)',
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 10], tickfont=dict(size=10))),
        showlegend=True, height=350,
        margin=dict(t=20, b=20, l=20, r=20),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
    )
    st.plotly_chart(fig, use_container_width=True)

    avg_now = round(sum(current_vals) / len(current_vals), 1)
    avg_goal = round(sum(goal_vals) / len(goal_vals), 1)
    st.metric("Average Score Now", f"{avg_now} / 10", delta=f"Goal: {avg_goal}")

    st.markdown("### 🎚️ Rate Yourself (1-10)")
    for area, question in areas.items():
        st.caption(f"*{question}*")
        col_s, col_g = st.columns(2)
        with col_s:
            d["wheel"][area] = st.slider(f"{area} — Now", 1, 10, d["wheel"][area], key=f"wheel_{area}")
        with col_g:
            d["wheel_goals"][area] = st.slider(f"Goal (4wks)", 1, 10, d["wheel_goals"][area], key=f"goal_{area}")
        st.markdown("---")

    if st.button("💾 Save Scores", type="primary"):
        save_data(d)
        st.success("Scores saved! Keep growing 🌱")

# ══════════════════════════════════════════════════════════════════
# PAGE: DAILY TIMEBOX PLANNER
# ══════════════════════════════════════════════════════════════════
elif page == "⏱️ Daily Timebox":
    st.markdown('<div class="tb-header">⏱️ Daily Timebox Planner — Plan Your Day, Hour by Hour</div>', unsafe_allow_html=True)

    # Date picker — each date gets its own saved plan
    selected_date = st.date_input("📅 Select Date", value=date.today())
    date_key = selected_date.isoformat()

    if "timebox" not in d:
        d["timebox"] = {}
    if date_key not in d["timebox"]:
        d["timebox"][date_key] = {
            "priorities": ["", "", "", "", "", ""],
            "brain_dump": "",
            "slots": {}
        }

    tb = d["timebox"][date_key]

    st.markdown("---")
    col_left, col_right = st.columns([1, 2])

    # ── LEFT: Priorities + Brain Dump ─────────────────────────────
    with col_left:
        st.markdown("### 🎯 Top Priorities")
        st.caption("What MUST get done today?")
        for i in range(6):
            tb["priorities"][i] = st.text_input(
                f"Priority {i+1}",
                value=tb["priorities"][i],
                key=f"prio_{date_key}_{i}",
                placeholder=f"{'🔴' if i==0 else '🟠' if i==1 else '🟡'} Priority {i+1}..." if i < 3 else f"Priority {i+1}..."
            )

        st.markdown("### 🧠 Brain Dump")
        st.caption("Get everything out of your head")
        tb["brain_dump"] = st.text_area(
            "",
            value=tb["brain_dump"],
            height=200,
            key=f"brain_{date_key}",
            placeholder="Dump ALL your thoughts, tasks, worries, ideas here...\nYou can sort them later.",
            label_visibility="collapsed"
        )

    # ── RIGHT: Time Grid ──────────────────────────────────────────
    with col_right:
        st.markdown("### 🕐 Time Blocks")

        # Build time slots: 5:00 AM to 11:30 PM
        hours_am = list(range(5, 12))   # 5–11 AM
        hours_pm = list(range(12, 24))  # 12 PM – 11 PM (23)
        all_hours = hours_am + hours_pm

        def fmt_hour(h):
            if h == 0:   return "12:00 AM"
            if h < 12:   return f"{h}:00 AM"
            if h == 12:  return "12:00 PM"
            return f"{h-12}:00 PM"

        def fmt_half(h):
            if h == 0:   return "12:30 AM"
            if h < 12:   return f"{h}:30 AM"
            if h == 12:  return "12:30 PM"
            return f"{h-12}:30 PM"

        # Column headers
        hc1, hc2, hc3 = st.columns([1, 3, 3])
        hc1.markdown("**Time**")
        hc2.markdown("**:00**")
        hc3.markdown("**:30**")

        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

        for h in all_hours:
            slot_key_00 = f"{h:02d}:00"
            slot_key_30 = f"{h:02d}:30"

            if slot_key_00 not in tb["slots"]:
                tb["slots"][slot_key_00] = ""
            if slot_key_30 not in tb["slots"]:
                tb["slots"][slot_key_30] = ""

            c1, c2, c3 = st.columns([1, 3, 3])

            with c1:
                label = fmt_hour(h)
                # Highlight current hour
                now_h = datetime.now().hour
                if h == now_h and selected_date == date.today():
                    st.markdown(f"<div class='time-row-hour' style='border-left:3px solid #fda085'>🔆 {label}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='time-row-hour'>{label}</div>", unsafe_allow_html=True)

            with c2:
                tb["slots"][slot_key_00] = st.text_input(
                    f"_{slot_key_00}", value=tb["slots"][slot_key_00],
                    key=f"slot_{date_key}_{slot_key_00}",
                    placeholder="What are you doing?",
                    label_visibility="collapsed"
                )

            with c3:
                tb["slots"][slot_key_30] = st.text_input(
                    f"_{slot_key_30}", value=tb["slots"][slot_key_30],
                    key=f"slot_{date_key}_{slot_key_30}",
                    placeholder="",
                    label_visibility="collapsed"
                )

    st.markdown("---")

    # ── Summary stats ─────────────────────────────────────────────
    filled_slots = sum(1 for v in tb["slots"].values() if v.strip())
    total_slots = len(tb["slots"])
    priorities_set = sum(1 for p in tb["priorities"] if p.strip())

    c1, c2, c3 = st.columns(3)
    c1.metric("✅ Priorities Set", f"{priorities_set} / 6")
    c2.metric("⏱️ Time Slots Filled", f"{filled_slots} / {total_slots}")
    c3.metric("📅 Planning For", selected_date.strftime("%d %b %Y"))

    col_btn1, col_btn2, _ = st.columns([1, 1, 3])
    with col_btn1:
        if st.button("💾 Save Plan", type="primary"):
            save_data(d)
            st.success("Plan saved! 🗓️")

    with col_btn2:
        if st.button("🗑️ Clear This Day"):
            d["timebox"][date_key] = {
                "priorities": ["", "", "", "", "", ""],
                "brain_dump": "",
                "slots": {}
            }
            save_data(d)
            st.success("Cleared!")
            st.rerun()

    # ── Past plans browser ────────────────────────────────────────
    all_dates = sorted(d["timebox"].keys(), reverse=True)
    if len(all_dates) > 1:
        st.markdown("---")
        st.markdown("### 📚 Past Plans")
        st.caption("Your previously saved timebox plans")
        for past_date in all_dates[:5]:
            if past_date == date_key:
                continue
            past_tb = d["timebox"][past_date]
            prios = [p for p in past_tb["priorities"] if p.strip()]
            filled = sum(1 for v in past_tb["slots"].values() if v.strip())
            dt_label = date.fromisoformat(past_date).strftime("%A, %d %b %Y")
            with st.expander(f"📅 {dt_label} — {len(prios)} priorities, {filled} slots filled"):
                if prios:
                    st.markdown("**Top Priorities:**")
                    for p in prios:
                        st.markdown(f"• {p}")
                busy_slots = {k: v for k, v in past_tb["slots"].items() if v.strip()}
                if busy_slots:
                    st.markdown("**Scheduled:**")
                    for slot, task in sorted(busy_slots.items()):
                        h = int(slot.split(":")[0])
                        m = slot.split(":")[1]
                        ampm = "AM" if h < 12 else "PM"
                        h12 = h if h <= 12 else h - 12
                        h12 = 12 if h12 == 0 else h12
                        st.markdown(f"⏰ `{h12}:{m} {ampm}` — {task}")