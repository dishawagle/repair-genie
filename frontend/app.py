import streamlit as st
import requests
import json
from datetime import datetime

# ── Config ─────────────────────────────────────────────────────────────────
BACKEND_URL = st.secrets.get("BACKEND_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Repair Genie",
    page_icon="🧞",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Styles ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&display=swap');

    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

    .rg-header { display:flex; align-items:center; gap:12px; margin-bottom:1.5rem; padding-bottom:1rem; border-bottom:1px solid #eee; }
    .rg-logo { background:#C85A1A; border-radius:10px; width:40px; height:40px; display:flex; align-items:center; justify-content:center; font-size:20px; }
    .rg-title { font-size:22px; font-weight:600; }
    .rg-title span { color:#C85A1A; }

    .rg-card { background:white; border:1px solid #eee; border-radius:12px; padding:1.25rem; margin-bottom:1rem; }

    .chat-ai { background:#FAECE7; border-left:3px solid #C85A1A; border-radius:8px; padding:12px 14px; margin-bottom:10px; }
    .chat-user { background:#f5f5f5; border-left:3px solid #ddd; border-radius:8px; padding:12px 14px; margin-bottom:10px; }
    .chat-label { font-size:11px; font-weight:600; color:#888; text-transform:uppercase; letter-spacing:.5px; margin-bottom:4px; }

    .cause-row { display:flex; align-items:center; gap:10px; margin-bottom:8px; }
    .prob-bar-bg { height:6px; background:#f0f0f0; border-radius:3px; flex:1; overflow:hidden; }
    .prob-bar { height:100%; background:#C85A1A; border-radius:3px; }

    .step-num { width:26px; height:26px; border-radius:50%; border:1.5px solid #C85A1A; color:#C85A1A; font-size:12px; font-weight:600; display:inline-flex; align-items:center; justify-content:center; margin-right:10px; flex-shrink:0; }
    .check-num { width:22px; height:22px; border-radius:50%; background:#FAECE7; color:#C85A1A; font-size:12px; font-weight:600; display:inline-flex; align-items:center; justify-content:center; margin-right:10px; flex-shrink:0; }

    .badge-open { background:#EAF3DE; color:#3B6D11; padding:2px 10px; border-radius:20px; font-size:12px; }
    .badge-done { background:#f0f0f0; color:#888; padding:2px 10px; border-radius:20px; font-size:12px; }

    div[data-testid="stButton"] button {
        border-radius: 8px !important;
        font-weight: 500 !important;
    }
    div[data-testid="stButton"] button[kind="primary"] {
        background-color: #C85A1A !important;
        border-color: #C85A1A !important;
    }
    .stTextInput input, .stTextArea textarea {
        border-radius: 8px !important;
    }
</style>
""", unsafe_allow_html=True)


# ── Session state init ─────────────────────────────────────────────────────
def init_state():
    defaults = {
        "screen": "role",
        "chat": [],
        "session": None,
        "sessions": {},
        "loading": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()


# ── API call ───────────────────────────────────────────────────────────────
def call_backend(messages: list[dict]) -> dict:
    resp = requests.post(
        f"{BACKEND_URL}/diagnose",
        json={"messages": messages},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


# ── Helpers ────────────────────────────────────────────────────────────────
def new_session_id():
    return f"s_{int(datetime.now().timestamp() * 1000)}"

def save_session(s: dict):
    st.session_state.sessions[s["id"]] = s

def format_prob_bar(label: str, prob: int) -> str:
    return f"""
    <div class="cause-row">
        <span style="flex:1;font-size:14px">{label}</span>
        <div class="prob-bar-bg" style="width:120px">
            <div class="prob-bar" style="width:{prob}%"></div>
        </div>
        <span style="font-size:13px;font-weight:600;color:#C85A1A;min-width:36px;text-align:right">{prob}%</span>
    </div>"""


# ── Header ─────────────────────────────────────────────────────────────────
def render_header(show_back=False, back_label="← Back", back_screen="home-main"):
    col1, col2 = st.columns([1, 6])
    with col1:
        st.markdown('<div style="font-size:32px;margin-top:4px">🧞</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<span style="font-size:22px;font-weight:600">Repair<span style="color:#C85A1A">Genie</span></span>', unsafe_allow_html=True)

    if show_back:
        if st.button(back_label, key="back_btn"):
            st.session_state.screen = back_screen
            st.rerun()

    st.divider()


# ── Screens ────────────────────────────────────────────────────────────────
def screen_role():
    render_header()
    st.markdown("## What brings you here?")
    st.markdown("Tell us who you are and we'll tailor your experience.")
    st.markdown("")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**🏠 Homeowner**")
        st.caption("Diagnose an appliance problem and get a step-by-step repair guide.")
        if st.button("I'm a Homeowner", use_container_width=True, type="primary"):
            st.session_state.screen = "home-main"
            st.rerun()
    with col2:
        st.markdown("**🔧 Contractor**")
        st.caption("View job requests from homeowners in your area.")
        if st.button("I'm a Contractor", use_container_width=True):
            st.session_state.screen = "contractor"
            st.rerun()


def screen_contractor():
    render_header(show_back=True, back_screen="role")
    st.markdown("## 🔧 Contractor portal")
    st.info("Coming soon — contractors will be able to create profiles and receive job requests from homeowners in their area.")


def screen_home_main():
    render_header(show_back=True, back_label="← Change role", back_screen="role")
    st.markdown("### 👋 Welcome, homeowner")
    st.markdown("Describe your appliance issue and the Genie will diagnose it, walk you through safety checks, and guide you to a fix — or connect you with a local contractor if needed.")
    st.markdown("")

    col1, col2 = st.columns([2, 3])
    with col1:
        if st.button("+ New diagnosis", type="primary", use_container_width=True):
            st.session_state.chat = []
            st.session_state.session = None
            st.session_state.screen = "new-session"
            st.rerun()
    with col2:
        if st.session_state.sessions:
            if st.button(f"My sessions ({len(st.session_state.sessions)})", use_container_width=True):
                st.session_state.screen = "history"
                st.rerun()

    # Recent sessions
    if st.session_state.sessions:
        st.markdown("")
        st.markdown("**Recent sessions**")
        recent = list(reversed(list(st.session_state.sessions.values())))[:3]
        for s in recent:
            badge = "badge-open" if not s.get("resolved") else "badge-done"
            badge_txt = "Open" if not s.get("resolved") else "Resolved"
            st.markdown(f"""
            <div class="rg-card" style="cursor:pointer">
                <strong>{s['form'].get('appliance','Appliance')}</strong>
                <span class="{badge}">{badge_txt}</span><br/>
                <small style="color:#888">{s['form'].get('problem','')[:90]}...</small>
            </div>""", unsafe_allow_html=True)
            if st.button(f"Open →", key=f"open_{s['id']}"):
                st.session_state.session = s
                st.session_state.chat = s.get("chat", [])
                st.session_state.screen = "load-session"
                st.rerun()


def screen_new_session():
    render_header(show_back=True, back_screen="home-main")
    st.markdown("**Step 1 of 3 — Describe**")
    st.progress(0.33)
    st.markdown("")
    st.markdown("### Tell the Genie about your appliance")

    with st.form("diagnosis_form"):
        appliance = st.text_input("Appliance name *", placeholder="e.g. Samsung washing machine")
        model = st.text_input("Model number", placeholder="e.g. WF45R6100AW")
        problem = st.text_area("Describe the problem *", placeholder="What's happening? Any sounds, smells, error codes? When did it start?", height=120)
        files = st.file_uploader("Photos or videos (optional)", accept_multiple_files=True, type=["jpg","jpeg","png","mp4","mov"])
        submitted = st.form_submit_button("Ask the Genie ✨", type="primary", use_container_width=True)

    if submitted:
        if not appliance.strip() or not problem.strip():
            st.error("Please fill in the appliance name and problem description.")
        else:
            file_names = [f.name for f in files] if files else []
            form = {"appliance": appliance, "model": model, "problem": problem, "files": file_names}
            sess = {"id": new_session_id(), "form": form, "chat": [], "result": None, "resolved": False, "createdAt": datetime.now().isoformat()}
            st.session_state.session = sess

            user_msg = f"Appliance: {appliance}"
            if model:
                user_msg += f"\nModel: {model}"
            user_msg += f"\n\nProblem: {problem}"
            if file_names:
                user_msg += f"\n\nAttachments: {', '.join(file_names)}"

            st.session_state.chat = [{"role": "user", "content": user_msg}]
            st.session_state.screen = "followup"
            st.rerun()


def screen_followup():
    render_header(show_back=True, back_screen="home-main")
    st.markdown("**Step 2 of 3 — Diagnose**")
    st.progress(0.66)
    st.markdown("")
    st.markdown("### 🧞 Genie is on the case")

    # Render chat history
    for msg in st.session_state.chat:
        if msg["role"] == "assistant":
            clean = msg["content"].split("REPAIR_RESULT:")[0].strip()
            st.markdown(f"""<div class="chat-ai"><div class="chat-label">Repair Genie</div>{clean}</div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""<div class="chat-user"><div class="chat-label">You</div>{msg["content"]}</div>""", unsafe_allow_html=True)

    # If last message is from user, call the backend
    if st.session_state.chat and st.session_state.chat[-1]["role"] == "user":
        with st.spinner("Genie is thinking..."):
            try:
                data = call_backend(st.session_state.chat)
                reply = data["reply"]
                st.session_state.chat.append({"role": "assistant", "content": reply})

                if data["is_result"] and data.get("result"):
                    sess = st.session_state.session
                    sess["result"] = data["result"]
                    sess["chat"] = st.session_state.chat
                    save_session(sess)
                    st.session_state.screen = "results"

                st.rerun()
            except Exception as e:
                st.error(f"Could not reach the Genie: {e}")
        return

    # Input for follow-up
    st.markdown("")
    with st.form("followup_form", clear_on_submit=True):
        user_input = st.text_input("Answer the Genie's question...", label_visibility="collapsed")
        send = st.form_submit_button("Send →", type="primary", use_container_width=True)

    if send and user_input.strip():
        st.session_state.chat.append({"role": "user", "content": user_input.strip()})
        st.rerun()


def screen_results():
    render_header(show_back=True, back_screen="home-main")
    st.markdown("**Step 3 of 3 — Results**")
    st.progress(1.0)
    st.markdown("")

    sess = st.session_state.session
    res = sess.get("result") if sess else None
    if not res:
        st.warning("No diagnosis found.")
        return

    st.markdown(f"### 🧞 Genie's diagnosis")
    st.caption(f"{sess['form'].get('appliance','')} {' · ' + sess['form'].get('model','') if sess['form'].get('model') else ''}")
    st.divider()

    # Root causes
    st.markdown("**POSSIBLE ROOT CAUSES**")
    for c in res.get("causes", []):
        st.markdown(format_prob_bar(c["label"], c["probability"]), unsafe_allow_html=True)

    st.divider()

    # Safety checks
    st.markdown("**⚠️ SAFETY CHECKS FIRST**")
    for i, s in enumerate(res.get("safety", []), 1):
        st.markdown(f"""<div style="display:flex;align-items:flex-start;gap:10px;margin-bottom:8px;font-size:14px">
            <span class="check-num">{i}</span><span>{s}</span></div>""", unsafe_allow_html=True)

    st.divider()

    # Steps
    st.markdown("**🔧 STEP-BY-STEP FIX**")
    for i, s in enumerate(res.get("steps", []), 1):
        st.markdown(f"""<div style="display:flex;align-items:flex-start;gap:12px;margin-bottom:12px;font-size:14px">
            <span class="step-num">{i}</span><span>{s}</span></div>""", unsafe_allow_html=True)

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        if not sess.get("resolved"):
            if st.button("✓ Mark as resolved", use_container_width=True):
                sess["resolved"] = True
                save_session(sess)
                st.rerun()
        else:
            st.success("✓ Resolved")
    with col2:
        if st.button("Find a contractor →", type="primary", use_container_width=True):
            st.info("Contractor matching coming soon! Your diagnosis details will be shared with vetted local contractors.")


def screen_history():
    render_header(show_back=True, back_screen="home-main")
    st.markdown("### My sessions")

    if not st.session_state.sessions:
        st.info("No sessions yet. Start a new diagnosis!")
    else:
        for s in reversed(list(st.session_state.sessions.values())):
            badge = "Open" if not s.get("resolved") else "Resolved"
            col1, col2 = st.columns([5, 1])
            with col1:
                st.markdown(f"**{s['form'].get('appliance','Appliance')}** — `{badge}`")
                st.caption(s["form"].get("problem", "")[:100])
            with col2:
                if st.button("Open", key=f"hist_{s['id']}"):
                    st.session_state.session = s
                    st.session_state.chat = s.get("chat", [])
                    st.session_state.screen = "load-session"
                    st.rerun()
            st.divider()

    if st.button("+ New diagnosis", type="primary"):
        st.session_state.chat = []
        st.session_state.session = None
        st.session_state.screen = "new-session"
        st.rerun()


def screen_load_session():
    render_header(show_back=True, back_screen="history")
    sess = st.session_state.session
    if not sess:
        return

    badge = "Open" if not sess.get("resolved") else "Resolved"
    st.markdown(f"### {sess['form'].get('appliance','Appliance')} — `{badge}`")
    st.caption(datetime.fromisoformat(sess["createdAt"]).strftime("%b %d, %Y"))
    st.divider()

    with st.form("edit_session"):
        appliance = st.text_input("Appliance", value=sess["form"].get("appliance",""))
        model = st.text_input("Model number", value=sess["form"].get("model",""))
        problem = st.text_area("Problem description", value=sess["form"].get("problem",""), height=100)
        col1, col2, col3 = st.columns(3)
        with col1:
            view = st.form_submit_button("View diagnosis", use_container_width=True)
        with col2:
            reask = st.form_submit_button("Re-ask Genie ✨", type="primary", use_container_width=True)
        with col3:
            contractor = st.form_submit_button("Find contractor →", use_container_width=True)

    if view and sess.get("result"):
        st.session_state.screen = "results"
        st.rerun()
    if reask:
        sess["form"]["appliance"] = appliance
        sess["form"]["model"] = model
        sess["form"]["problem"] = problem
        user_msg = f"Appliance: {appliance}"
        if model:
            user_msg += f"\nModel: {model}"
        user_msg += f"\n\nProblem: {problem}"
        st.session_state.chat = [{"role": "user", "content": user_msg}]
        st.session_state.session = sess
        st.session_state.screen = "followup"
        st.rerun()
    if contractor:
        st.info("Contractor matching coming soon!")


# ── Router ─────────────────────────────────────────────────────────────────
screen_map = {
    "role": screen_role,
    "contractor": screen_contractor,
    "home-main": screen_home_main,
    "new-session": screen_new_session,
    "followup": screen_followup,
    "results": screen_results,
    "history": screen_history,
    "load-session": screen_load_session,
}

screen_map.get(st.session_state.screen, screen_role)()
