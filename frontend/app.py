import streamlit as st
import requests
from datetime import datetime
import html as _html

# ── Config ─────────────────────────────────────────────────────────────────
BACKEND_URL = st.secrets.get("BACKEND_URL", "http://localhost:8000")

APPLIANCES = [
    "Washer", "Dryer", "Refrigerator", "Dishwasher",
    "Air conditioner", "Heater / furnace", "Oven / range",
    "Microwave", "Water heater", "Freezer", "Garbage disposal", "Other"
]

st.set_page_config(
    page_title="RepairGenie",
    page_icon="🧞",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Global CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
  --y50:#FFFDF0; --y100:#FFF8CC; --y200:#FFE566; --y400:#E6C800; --y600:#B39B00;
  --g50:#F8F8F6; --g100:#EFEFEC; --g200:#D3D1C7; --g400:#888780; --g600:#5F5E5A; --g800:#2C2C2A;
}

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif !important; }

/* ── Navbar ── */
.rg-navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--y100);
  border-bottom: 1px solid var(--y200);
  padding: .65rem 1rem;
  margin-bottom: 1.25rem;
  border-radius: 0 0 12px 12px;
  position: sticky;
  top: 0;
  z-index: 999;
}
.rg-navbar-brand {
  font-size: 16px; font-weight: 600; color: var(--g800);
  display: flex; align-items: center; gap: 7px; text-decoration: none;
}
.rg-navbar-brand .logo-icon {
  width: 28px; height: 28px; background: var(--y200);
  border-radius: 8px; border: 1px solid var(--y400);
  display: flex; align-items: center; justify-content: center; font-size: 14px;
}
.rg-navbar-actions { display: flex; align-items: center; gap: 6px; }
.rg-nav-btn {
  display: inline-flex; align-items: center; gap: 5px;
  font-size: 12px; font-weight: 500; color: var(--g600);
  background: white; border: 0.5px solid var(--g200);
  border-radius: 20px; padding: 5px 12px; cursor: pointer;
  transition: all .15s; white-space: nowrap;
}
.rg-nav-btn:hover { border-color: var(--y400); color: var(--g800); background: var(--y50); }
.rg-nav-btn.active { background: var(--y200); border-color: var(--y400); color: var(--g800); }

/* Hero band */
.hero-band {
  background: var(--y100); border-bottom: 1px solid var(--y200);
  border-radius: 0 0 20px 20px; padding: 1.75rem 1.25rem 2.5rem; margin-bottom: 0;
}
.hero-logo {
  width: 52px; height: 52px; background: var(--y200);
  border-radius: 16px; border: 1.5px solid var(--y400);
  display: flex; align-items: center; justify-content: center;
  font-size: 26px; margin-bottom: .85rem;
}
.hero-band h1 { font-size: 22px; font-weight: 500; color: var(--g800); margin-bottom: 4px; }
.hero-band p  { font-size: 13px; color: var(--g600); }

/* Welcome band */
.welcome-band {
  background: var(--y100); border: 1px solid var(--y200);
  border-radius: 12px; padding: 1.25rem; margin-bottom: 1rem;
}
.welcome-band h2 { font-size: 17px; font-weight: 500; color: var(--g800); margin-bottom: 4px; }
.welcome-band p  { font-size: 13px; color: var(--g600); }

/* Cards */
.rg-card {
  background: white; border: 0.5px solid #E5E5E0;
  border-radius: 12px; padding: 1.25rem; margin-bottom: .75rem;
}

/* Section label */
.section-label {
  font-size: 11px; font-weight: 500; text-transform: uppercase;
  letter-spacing: .6px; color: var(--g400); margin-bottom: .6rem;
}

/* Divider */
.rg-divider { height: 0.5px; background: var(--g100); margin: 1rem 0; }

/* Badges */
.badge-open { display:inline-block; font-size:11px; padding:2px 8px; border-radius:20px; background:var(--y100); color:var(--g800); border:1px solid var(--y200); }
.badge-done { display:inline-block; font-size:11px; padding:2px 8px; border-radius:20px; background:var(--g100); color:var(--g600); }
.badge-today { font-size:11px; padding:3px 8px; border-radius:20px; background:var(--y100); color:var(--g800); border:1px solid var(--y200); font-weight:500; }
.badge-tmr   { font-size:11px; padding:3px 8px; border-radius:20px; background:var(--g100); color:var(--g600); font-weight:500; }

/* Step bar */
.stepbar { display:flex; align-items:center; margin-bottom:1.25rem; }
.step-item { display:flex; align-items:center; gap:6px; font-size:12px; }
.step-line  { flex:1; height:1px; background:var(--g200); margin:0 6px; }
.step-done   .step-dot { background:var(--g800); color:#fff; }
.step-active .step-dot { background:var(--y400); color:var(--g800); box-shadow:0 0 0 4px var(--y100); }
.step-idle   .step-dot { background:var(--g100); color:var(--g400); border:0.5px solid var(--g200); }
.step-dot { width:24px; height:24px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:11px; font-weight:500; flex-shrink:0; }
.step-done   span { color:var(--g600); }
.step-active span { color:var(--g800); font-weight:500; }
.step-idle   span { color:var(--g400); }

/* Chat bubbles */
.bubble-ai {
  background:var(--y50); border:0.5px solid var(--y200);
  border-radius:0 12px 12px 12px;
  padding:12px 14px; margin-bottom:10px; font-size:14px; line-height:1.6; max-width:88%;
}
.bubble-user {
  background:var(--g100); border:0.5px solid var(--g200);
  border-radius:12px 0 12px 12px;
  padding:12px 14px; margin-bottom:10px; font-size:14px; line-height:1.6;
  max-width:88%; margin-left:auto;
}
.bubble-label { font-size:11px; font-weight:500; color:var(--g400); margin-bottom:4px; text-transform:uppercase; letter-spacing:.5px; }

/* Thinking animation */
.thinking-wrap {
  background:var(--y50); border:1px solid var(--y200);
  border-radius:0 12px 12px 12px;
  padding:14px 18px; display:inline-flex; align-items:center; gap:10px; margin-bottom:10px;
}
.thinking-avatar { width:32px; height:32px; border-radius:10px; background:var(--y200); border:1px solid var(--y400); display:flex; align-items:center; justify-content:center; font-size:16px; flex-shrink:0; }
.dots { display:flex; gap:5px; align-items:center; }
.dot { width:8px; height:8px; border-radius:50%; display:inline-block; }
.dot1{background:var(--y400);animation:blink 1.2s 0s infinite}
.dot2{background:var(--g400);animation:blink 1.2s .2s infinite}
.dot3{background:var(--g600);animation:blink 1.2s .4s infinite}
@keyframes blink{0%,80%,100%{transform:scale(1);opacity:.4}40%{transform:scale(1.3);opacity:1}}

/* Results */
.cause-row { display:flex; align-items:center; gap:10px; margin-bottom:10px; }
.prob-track { height:6px; background:var(--g100); border-radius:3px; flex:1; overflow:hidden; }
.prob-fill  { height:100%; background:var(--y400); border-radius:3px; }
.safety-row { display:flex; gap:10px; align-items:flex-start; margin-bottom:10px; font-size:14px; line-height:1.5; }
.step-row   { display:flex; gap:12px; align-items:flex-start; margin-bottom:12px; font-size:14px; line-height:1.5; }
.safety-num { width:24px; height:24px; border-radius:50%; background:var(--y100); border:1px solid var(--y200); color:var(--g800); font-size:11px; font-weight:500; display:flex; align-items:center; justify-content:center; flex-shrink:0; margin-top:1px; }
.step-circle{ width:28px; height:28px; border-radius:50%; border:1.5px solid var(--g400); color:var(--g800); font-size:12px; font-weight:500; display:flex; align-items:center; justify-content:center; flex-shrink:0; margin-top:1px; }

/* Contractor card */
.contractor-card { background:white; border:0.5px solid #E5E5E0; border-radius:12px; padding:1rem; margin-bottom:.75rem; }
.contractor-card:hover { border-color:var(--y400); }
.session-row { display:flex; justify-content:space-between; align-items:center; margin-bottom:8px; }

/* Streamlit button overrides */
div[data-testid="stButton"] button { border-radius: 8px !important; font-family:'DM Sans',sans-serif !important; }
div[data-testid="stButton"] button[kind="primary"] { background-color: var(--y400) !important; color: var(--g800) !important; border-color: var(--y400) !important; }
div[data-testid="stButton"] button[kind="primary"]:hover { background-color: var(--y600) !important; color: #fff !important; }
.stTextInput input, .stTextArea textarea, .stSelectbox select { border-radius: 8px !important; }
.stTextInput input:focus, .stTextArea textarea:focus { border-color: var(--y400) !important; box-shadow: 0 0 0 3px var(--y100) !important; }

/* Hide streamlit chrome */
#MainMenu{visibility:hidden}footer{visibility:hidden}
header[data-testid="stHeader"]{background:transparent}
.block-container{padding-top:0rem!important}
</style>
""", unsafe_allow_html=True)


# ── Session state ──────────────────────────────────────────────────────────
def init():
    for k, v in {
        "screen": "role", "chat": [], "session": None, "sessions": {}
    }.items():
        if k not in st.session_state:
            st.session_state[k] = v

init()


# ── API ────────────────────────────────────────────────────────────────────
def call_backend(messages):
    resp = requests.post(f"{BACKEND_URL}/diagnose", json={"messages": messages}, timeout=60)
    resp.raise_for_status()
    return resp.json()


# ── Helpers ────────────────────────────────────────────────────────────────
def sid():
    return f"s_{int(datetime.now().timestamp()*1000)}"

def save(s):
    st.session_state.sessions[s["id"]] = s

def go(screen):
    st.session_state.screen = screen
    st.rerun()

def stepbar(active):
    steps = ["Describe", "Diagnose", "Results"]
    items = []
    for i, lbl in enumerate(steps):
        n = i + 1
        cls = "step-done" if n < active else "step-active" if n == active else "step-idle"
        dot = "✓" if n < active else str(n)
        items.append(f'<div class="step-item {cls}"><div class="step-dot">{dot}</div><span>{lbl}</span></div>')
        if i < 2:
            items.append('<div class="step-line"></div>')
    st.markdown(f'<div class="stepbar">{"".join(items)}</div>', unsafe_allow_html=True)


# ── Navbar ─────────────────────────────────────────────────────────────────
# Screens where each nav button is relevant
# show_home: show "🏠 Home" button
# show_history: show "🕘 My Issues" button
# show_describe: show "← Describe" button (only on diagnose screen)
def navbar(show_home=True, show_history=True, show_describe=False):
    screen = st.session_state.screen
    session_count = len(st.session_state.sessions)

    # Build button labels with counts
    history_label = f"🕘 My Issues ({session_count})" if session_count > 0 else "🕘 My Issues"

    # Render HTML brand bar
    st.markdown(f"""
    <div class="rg-navbar">
      <div class="rg-navbar-brand">
        <div class="logo-icon">🧞</div>
        <span>RepairGenie</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Render nav buttons using Streamlit columns (so they're clickable)
    buttons = []
    if show_describe:
        buttons.append(("← Describe", "new-session"))
    if show_home:
        buttons.append(("🏠 Home", "home-main"))
    if show_history:
        buttons.append((history_label, "history"))
    buttons.append(("⇄ Change role", "role"))

    if buttons:
        cols = st.columns(len(buttons))
        for col, (label, target) in zip(cols, buttons):
            with col:
                is_active = screen == target
                btn_type = "primary" if is_active else "secondary"
                if st.button(label, use_container_width=True, key=f"nav_{target}_{screen}"):
                    go(target)


# ── Role screen ────────────────────────────────────────────────────────────
def screen_role():
    st.markdown("""
    <div class="hero-band">
      <div class="hero-logo">🧞</div>
      <h1>RepairGenie</h1>
      <p>AI-powered appliance diagnosis &amp; repair guidance</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""<div class="rg-card">
          <div style="font-size:24px;margin-bottom:.6rem">🏠</div>
          <h3 style="font-size:15px;font-weight:500;margin-bottom:4px">Homeowner</h3>
          <p style="font-size:12px;color:var(--g400);line-height:1.4">Diagnose an issue and get a step-by-step repair guide</p>
        </div>""", unsafe_allow_html=True)
        if st.button("I'm a Homeowner", type="primary", use_container_width=True):
            go("home-main")
    with col2:
        st.markdown("""<div class="rg-card">
          <div style="font-size:24px;margin-bottom:.6rem">🔧</div>
          <h3 style="font-size:15px;font-weight:500;margin-bottom:4px">Contractor</h3>
          <p style="font-size:12px;color:var(--g400);line-height:1.4">View and accept job requests near you</p>
        </div>""", unsafe_allow_html=True)
        if st.button("I'm a Contractor", use_container_width=True):
            go("contractor-portal")


# ── Home main ──────────────────────────────────────────────────────────────
def screen_home_main():
    navbar(show_home=False, show_history=True, show_describe=False)

    st.markdown("""<div class="welcome-band">
      <h2>What needs fixing today?</h2>
      <p>Describe your appliance issue — the Genie will diagnose it and guide you through the fix.</p>
    </div>""", unsafe_allow_html=True)

    if st.button("＋ New diagnosis", type="primary", use_container_width=True):
        st.session_state.chat = []
        st.session_state.session = None
        go("new-session")

    if st.session_state.sessions:
        recent = list(reversed(list(st.session_state.sessions.values())))[:3]
        for s in recent:
            badge = f'<span class="badge-open">Open</span>' if not s.get("resolved") else f'<span class="badge-done">Resolved</span>'
            st.markdown(f'<div class="rg-card"><div class="session-row"><div><p style="font-size:14px;font-weight:500">{s["form"].get("appliance","")} · {s["form"].get("brand","")}</p><p style="font-size:12px;color:var(--g400)">{s["form"].get("problem","")[:70]}...</p></div>{badge}</div></div>', unsafe_allow_html=True)
            if st.button("Open →", key=f"r_{s['id']}"):
                st.session_state.session = s
                st.session_state.chat = s.get("chat", [])
                go("load-session")


# ── New session form ───────────────────────────────────────────────────────
def screen_new_session():
    navbar(show_home=True, show_history=True, show_describe=False)
    stepbar(1)

    st.markdown("**Tell the Genie about your appliance**")
    st.markdown("")

    appliance_type = st.selectbox(
        "Appliance type *",
        [""] + APPLIANCES,
        format_func=lambda x: "Select appliance..." if x == "" else x,
    )

    other_appliance = ""
    if appliance_type == "Other":
        other_appliance = st.text_input("Specify appliance *", placeholder="e.g. Wine cooler, pool pump, ice maker...")

    brand   = st.text_input("Brand *", placeholder="e.g. Whirlpool, Samsung, LG")
    model   = st.text_input("Model number *", placeholder="e.g. WED5000DW")
    problem = st.text_area("Describe the problem *", placeholder="What's happening? Any sounds, smells, error codes? When did it start?", height=110)
    files   = st.file_uploader("Photos or videos (optional)", accept_multiple_files=True, type=["jpg","jpeg","png","mp4","mov"])

    if st.button("Ask the Genie ✨", type="primary", use_container_width=True):
        final_appliance = other_appliance.strip() if appliance_type == "Other" else appliance_type
        errors = []
        if not appliance_type:
            errors.append("Please select an appliance type.")
        if appliance_type == "Other" and not other_appliance.strip():
            errors.append("Please specify the appliance.")
        if not brand.strip():
            errors.append("Please enter the brand.")
        if not model.strip():
            errors.append("Please enter the model number.")
        if not problem.strip():
            errors.append("Please describe the problem.")

        if errors:
            for e in errors:
                st.error(e)
        else:
            file_names = [f.name for f in files] if files else []
            form = {
                "appliance": final_appliance, "brand": brand.strip(),
                "model": model.strip(), "problem": problem.strip(), "files": file_names
            }
            sess = {
                "id": sid(), "form": form, "chat": [], "result": None,
                "resolved": False, "createdAt": datetime.now().isoformat()
            }
            st.session_state.session = sess
            user_msg = (
                f"Appliance: {final_appliance}\n"
                f"Brand: {brand.strip()}\n"
                f"Model: {model.strip()}\n\n"
                f"Problem: {problem.strip()}"
            )
            if file_names:
                user_msg += f"\n\nAttachments: {', '.join(file_names)}"
            st.session_state.chat = [{"role": "user", "content": user_msg}]
            go("followup")


# ── Follow-up / chat ───────────────────────────────────────────────────────
def screen_followup():
    # show_describe=True so user can go back and edit their problem
    navbar(show_home=True, show_history=True, show_describe=True)
    stepbar(2)

    # Build chat HTML as a single self-contained block — never split open/close divs
    def clean_msg(content):
        c = content.split("REPAIR_RESULT:")[0].strip()
        if c.strip().startswith("{") and '"causes"' in c:
            return ""
        return c

    chat_html = '<div class="rg-card">'
    chat_html += '<div style="display:flex;align-items:center;gap:8px;margin-bottom:1rem"><div style="width:32px;height:32px;border-radius:10px;background:var(--y100);border:1px solid var(--y200);display:flex;align-items:center;justify-content:center;font-size:16px">🧞</div><span style="font-size:14px;font-weight:500">Genie is on the case</span></div>'

    for msg in st.session_state.chat:
        if msg["role"] == "assistant":
            clean = clean_msg(msg["content"])
            if clean:
                chat_html += f'<div class="bubble-ai"><div class="bubble-label">Repair Genie</div>{_html.escape(clean)}</div>'
        else:
            chat_html += f'<div class="bubble-user"><div class="bubble-label">You</div>{_html.escape(msg["content"])}</div>'

    is_waiting = st.session_state.chat and st.session_state.chat[-1]["role"] == "user"

    if is_waiting:
        chat_html += '<div class="thinking-wrap"><div class="thinking-avatar">🧞</div><div><p style="font-size:13px;font-weight:500;color:var(--g800);margin-bottom:6px">Genie is thinking...</p><div class="dots"><span class="dot dot1"></span><span class="dot dot2"></span><span class="dot dot3"></span></div></div></div>'

    chat_html += '</div>'
    st.markdown(chat_html, unsafe_allow_html=True)

    if is_waiting:
        try:
            data = call_backend(st.session_state.chat)
            reply = data["reply"]
            st.session_state.chat.append({"role": "assistant", "content": reply})
            if data["is_result"] and data.get("result"):
                sess = st.session_state.session
                sess["result"] = data["result"]
                sess["chat"] = st.session_state.chat
                save(sess)
                go("results")
            else:
                st.rerun()
        except Exception as e:
            st.error(f"Could not reach the Genie: {e}")
        return

    with st.form("fu_form", clear_on_submit=True):
        user_input = st.text_input("Answer the Genie's question...", label_visibility="collapsed")
        if st.form_submit_button("Send →", type="primary", use_container_width=True):
            if user_input.strip():
                st.session_state.chat.append({"role": "user", "content": user_input.strip()})
                st.rerun()


# ── Results ────────────────────────────────────────────────────────────────
def screen_results():
    navbar(show_home=True, show_history=True, show_describe=True)
    stepbar(3)

    sess = st.session_state.session
    res  = sess.get("result") if sess else None
    if not res:
        st.warning("No diagnosis found.")
        return

    form = sess.get("form", {})
    appliance_label = f"{form.get('appliance','')} · {form.get('brand','')} {form.get('model','')}"

    st.markdown(f"""<div class="rg-card">
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:1rem">
        <div style="width:42px;height:42px;border-radius:12px;background:var(--y100);border:1px solid var(--y200);display:flex;align-items:center;justify-content:center;font-size:20px">🧞</div>
        <div>
          <p style="font-size:15px;font-weight:500">Genie's diagnosis</p>
          <p style="font-size:12px;color:var(--g400)">{appliance_label}</p>
        </div>
      </div>
      <div class="rg-divider"></div>
      <div class="section-label">Possible root causes</div>
      {"".join(f'''<div class="cause-row">
        <span style="flex:1;font-size:14px">{_html.escape(c["label"])}</span>
        <div class="prob-track"><div class="prob-fill" style="width:{c["probability"]}%"></div></div>
        <span style="font-size:13px;font-weight:500;color:var(--g800);min-width:34px;text-align:right">{c["probability"]}%</span>
      </div>''' for c in res.get("causes",[]))}
      <div class="rg-divider"></div>
      <div class="section-label">⚠️ Safety checks — do these first</div>
      {"".join(f'<div class="safety-row"><div class="safety-num">{i+1}</div><span>{_html.escape(s)}</span></div>' for i,s in enumerate(res.get("safety",[])))}
    </div>""", unsafe_allow_html=True)

    diy_possible = res.get("diy_possible", True)
    if diy_possible and res.get("diy_steps"):
        st.markdown(f"""<div class="rg-card">
          <div class="section-label">🔧 DIY fix — step by step</div>
          {"".join(f'<div class="step-row"><div class="step-circle">{i+1}</div><span>{_html.escape(s)}</span></div>' for i,s in enumerate(res.get("diy_steps",[])))}
          {f'<p style="font-size:13px;color:var(--g600);margin-top:.5rem">💡 {_html.escape(res["diy_note"])}</p>' if res.get("diy_note") else ""}
        </div>""", unsafe_allow_html=True)
    else:
        st.warning(f"🚫 **This fix is not safe to DIY.** {res.get('diy_note','This repair requires a professional technician.')}")

    needs_contractor = res.get("needs_contractor", False) or not diy_possible
    contractor_reason = res.get("contractor_reason", "")

    if needs_contractor:
        if contractor_reason:
            st.markdown(f'<div class="rg-card"><div class="section-label">👷 You need a contractor</div><p style="font-size:14px;color:var(--g600);margin-bottom:.75rem">{contractor_reason}</p></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="rg-card"><div class="section-label">👷 You need a contractor</div></div>', unsafe_allow_html=True)
        if st.button("🔍 Find contractors near me →", type="primary", use_container_width=True):
            go("find-contractor")
    else:
        st.markdown('<div class="rg-card"><div class="section-label">Still not fixed?</div><p style="font-size:13px;color:var(--g600);margin-bottom:.5rem">If the steps didn\'t help, a technician can take it from here.</p></div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if not sess.get("resolved"):
                if st.button("✓ Mark as resolved", use_container_width=True):
                    sess["resolved"] = True
                    save(sess)
                    st.rerun()
            else:
                st.success("✓ Resolved")
        with col2:
            if st.button("Find a contractor →", use_container_width=True):
                go("find-contractor")


# ── Find contractor ────────────────────────────────────────────────────────
def screen_find_contractor():
    navbar(show_home=True, show_history=True, show_describe=True)

    sess = st.session_state.session
    res  = sess.get("result") if sess else None

    st.markdown("""<div class="welcome-band">
      <h2>👷 Find a contractor near you</h2>
      <p>Your full diagnosis will be shared with the contractor you choose.</p>
    </div>""", unsafe_allow_html=True)

    if res and res.get("contractor_reason"):
        st.info(f"**What you need:** {res['contractor_reason']}")

    address = st.text_input("Your address or zip code", placeholder="e.g. 07302 or 123 Main St, Jersey City NJ")

    if address.strip():
        st.markdown("")
        st.markdown('<div class="section-label">3 contractors found nearby</div>', unsafe_allow_html=True)
        st.caption("*In the full app, these would be real verified contractors from our network.*")

        contractors = [
            {"name":"ProFix Appliance Repair","rating":4.8,"reviews":312,"dist":"0.8 mi","spec":"Washers, Dryers, Dishwashers","phone":"(201) 555-0101","avail":"Today","avail_cls":"badge-today"},
            {"name":"A1 Appliance Experts","rating":4.9,"reviews":427,"dist":"2.1 mi","spec":"Samsung, LG, Whirlpool specialists","phone":"(201) 555-0144","avail":"Today","avail_cls":"badge-today"},
            {"name":"QuickFix Home Services","rating":4.6,"reviews":198,"dist":"1.4 mi","spec":"All major appliances","phone":"(201) 555-0188","avail":"Tomorrow","avail_cls":"badge-tmr"},
        ]

        for c in contractors:
            st.markdown(f"""<div class="contractor-card">
              <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px">
                <div>
                  <p style="font-size:14px;font-weight:500">{c['name']}</p>
                  <p style="font-size:12px;color:var(--g400)">⭐ {c['rating']} · {c['reviews']} reviews · 📍 {c['dist']}</p>
                  <p style="font-size:12px;color:var(--g400);margin-top:2px">{c['spec']}</p>
                </div>
                <span class="{c['avail_cls']}">{c['avail']}</span>
              </div>
              <p style="font-size:13px;color:var(--y600);font-weight:500">{c['phone']}</p>
            </div>""", unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📋 Send my diagnosis", key=f"send_{c['name']}", use_container_width=True):
                    st.success(f"✓ Diagnosis sent to {c['name']}! They'll contact you shortly.")
            with col2:
                if st.button("📞 Call now", key=f"call_{c['name']}", use_container_width=True):
                    st.info(f"Call {c['name']} at {c['phone']}")
            st.markdown("")
    else:
        st.markdown('<p style="font-size:14px;color:var(--g400)">Enter your address above to see contractors near you.</p>', unsafe_allow_html=True)


# ── History ────────────────────────────────────────────────────────────────
def screen_history():
    navbar(show_home=True, show_history=False, show_describe=False)

    st.markdown("### My sessions")
    if not st.session_state.sessions:
        st.info("No sessions yet. Start a new diagnosis!")
    else:
        for s in reversed(list(st.session_state.sessions.values())):
            badge = "Open" if not s.get("resolved") else "Resolved"
            col1, col2 = st.columns([5, 1])
            with col1:
                st.markdown(f"**{s['form'].get('appliance','')} · {s['form'].get('brand','')}** — `{badge}`")
                st.caption(s["form"].get("problem","")[:90])
            with col2:
                if st.button("Open", key=f"h_{s['id']}"):
                    st.session_state.session = s
                    st.session_state.chat = s.get("chat", [])
                    go("load-session")
            st.divider()

    if st.button("＋ New diagnosis", type="primary"):
        st.session_state.chat = []
        st.session_state.session = None
        go("new-session")


# ── Load session ───────────────────────────────────────────────────────────
def screen_load_session():
    navbar(show_home=True, show_history=True, show_describe=False)

    sess = st.session_state.session
    if not sess:
        return

    badge = "Open" if not sess.get("resolved") else "Resolved"
    st.markdown(f"### {sess['form'].get('appliance','')} · {sess['form'].get('brand','')} — `{badge}`")
    st.caption(datetime.fromisoformat(sess["createdAt"]).strftime("%b %d, %Y"))
    st.divider()

    with st.form("edit_session"):
        appliance = st.text_input("Appliance", value=sess["form"].get("appliance",""))
        brand     = st.text_input("Brand",     value=sess["form"].get("brand",""))
        model     = st.text_input("Model",     value=sess["form"].get("model",""))
        problem   = st.text_area("Problem",    value=sess["form"].get("problem",""), height=100)
        c1, c2, c3 = st.columns(3)
        with c1: view       = st.form_submit_button("View diagnosis",   use_container_width=True)
        with c2: reask      = st.form_submit_button("Re-ask Genie ✨",  type="primary", use_container_width=True)
        with c3: contractor = st.form_submit_button("Find contractor →", use_container_width=True)

    if view and sess.get("result"):
        go("results")
    if reask:
        sess["form"].update({"appliance":appliance,"brand":brand,"model":model,"problem":problem})
        user_msg = f"Appliance: {appliance}\nBrand: {brand}\nModel: {model}\n\nProblem: {problem}"
        st.session_state.chat = [{"role":"user","content":user_msg}]
        st.session_state.session = sess
        go("followup")
    if contractor:
        go("find-contractor")


# ── Contractor portal ──────────────────────────────────────────────────────
def screen_contractor_portal():
    navbar(show_home=False, show_history=False, show_describe=False)

    st.markdown("""<div style="text-align:center;padding:3rem 1rem">
      <div style="font-size:40px;margin-bottom:1rem">🔧</div>
      <h2 style="font-size:18px;font-weight:500;margin-bottom:.5rem">Contractor portal</h2>
      <p style="font-size:14px;color:var(--g400);line-height:1.6">Coming soon — create your profile and start receiving job requests from homeowners near you.</p>
    </div>""", unsafe_allow_html=True)


# ── Router ─────────────────────────────────────────────────────────────────
{
    "role":              screen_role,
    "home-main":         screen_home_main,
    "new-session":       screen_new_session,
    "followup":          screen_followup,
    "results":           screen_results,
    "find-contractor":   screen_find_contractor,
    "history":           screen_history,
    "load-session":      screen_load_session,
    "contractor-portal": screen_contractor_portal,
}.get(st.session_state.screen, screen_role)()
