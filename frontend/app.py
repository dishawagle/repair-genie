import streamlit as st
import requests
import json
import os
import html as _html
from datetime import datetime
import store
import qrcode
import io
import base64
from PIL import Image

# ── Config ─────────────────────────────────────────────────────────────────
BACKEND_URL = st.secrets.get("BACKEND_URL", "http://localhost:8000")

APPLIANCES = [
    "Washer", "Dryer", "Refrigerator", "Dishwasher",
    "Air conditioner", "Heater / furnace", "Oven / range",
    "Microwave", "Water heater", "Freezer", "Garbage disposal", "Other"
]

SPECIALTY_OPTIONS = [
    "Washer", "Dryer", "Refrigerator", "Dishwasher",
    "Air conditioner", "Heater / furnace", "Oven / range",
    "Microwave", "Water heater", "Freezer", "Garbage disposal",
]

st.set_page_config(page_title="RepairGenie", page_icon="🧞",
                   layout="centered", initial_sidebar_state="collapsed")

# ── CSS ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&display=swap');
:root {
  --y50:#FFFDF0;--y100:#FFF8CC;--y200:#FFE566;--y400:#E6C800;--y600:#B39B00;
  --g50:#F8F8F6;--g100:#EFEFEC;--g200:#D3D1C7;--g400:#888780;--g600:#5F5E5A;--g800:#2C2C2A;
}
html,body,[class*="css"]{font-family:'DM Sans',sans-serif!important}
.hero-band{background:var(--y100);border-bottom:1px solid var(--y200);border-radius:0 0 20px 20px;padding:1.75rem 1.25rem 2.5rem;margin-bottom:0}
.hero-logo{width:52px;height:52px;background:var(--y200);border-radius:16px;border:1.5px solid var(--y400);display:flex;align-items:center;justify-content:center;font-size:26px;margin-bottom:.85rem}
.hero-band h1{font-size:22px;font-weight:500;color:var(--g800);margin-bottom:4px}
.hero-band p{font-size:13px;color:var(--g600)}
.welcome-band{background:var(--y100);border:1px solid var(--y200);border-radius:12px;padding:1.25rem;margin-bottom:1rem}
.welcome-band h2{font-size:17px;font-weight:500;color:var(--g800);margin-bottom:4px}
.welcome-band p{font-size:13px;color:var(--g600)}
.rg-card{background:white;border:0.5px solid #E5E5E0;border-radius:12px;padding:1.25rem;margin-bottom:.75rem}
.rg-navbar{display:flex;align-items:center;justify-content:space-between;background:var(--y100);border-bottom:1px solid var(--y200);padding:.65rem 1rem;margin-bottom:1.25rem;border-radius:0 0 12px 12px;position:sticky;top:0;z-index:999}
.rg-navbar-brand{font-size:16px;font-weight:600;color:var(--g800);display:flex;align-items:center;gap:7px}
.logo-icon{width:28px;height:28px;background:var(--y200);border-radius:8px;border:1px solid var(--y400);display:flex;align-items:center;justify-content:center;font-size:14px}
.section-label{font-size:11px;font-weight:500;text-transform:uppercase;letter-spacing:.6px;color:var(--g400);margin-bottom:.6rem}
.rg-divider{height:0.5px;background:var(--g100);margin:1rem 0}
.badge-open{display:inline-block;font-size:11px;padding:2px 8px;border-radius:20px;background:var(--y100);color:var(--g800);border:1px solid var(--y200)}
.badge-done{display:inline-block;font-size:11px;padding:2px 8px;border-radius:20px;background:var(--g100);color:var(--g600)}
.badge-today{font-size:11px;padding:3px 8px;border-radius:20px;background:var(--y100);color:var(--g800);border:1px solid var(--y200);font-weight:500}
.badge-tmr{font-size:11px;padding:3px 8px;border-radius:20px;background:var(--g100);color:var(--g600);font-weight:500}
.badge-accepted{font-size:11px;padding:3px 8px;border-radius:20px;background:#EAF3DE;color:#27500A;font-weight:500}
.badge-declined{font-size:11px;padding:3px 8px;border-radius:20px;background:var(--g100);color:var(--g600);font-weight:500}
.stepbar{display:flex;align-items:center;margin-bottom:1.25rem}
.step-item{display:flex;align-items:center;gap:6px;font-size:12px}
.step-line{flex:1;height:1px;background:var(--g200);margin:0 6px}
.step-done .step-dot{background:var(--g800);color:#fff}
.step-active .step-dot{background:var(--y400);color:var(--g800);box-shadow:0 0 0 4px var(--y100)}
.step-idle .step-dot{background:var(--g100);color:var(--g400);border:0.5px solid var(--g200)}
.step-dot{width:24px;height:24px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:500;flex-shrink:0}
.step-done span{color:var(--g600)}.step-active span{color:var(--g800);font-weight:500}.step-idle span{color:var(--g400)}
.bubble-ai{background:var(--y50);border:0.5px solid var(--y200);border-radius:0 12px 12px 12px;padding:12px 14px;margin-bottom:10px;font-size:14px;line-height:1.6;max-width:88%}
.bubble-user{background:var(--g100);border:0.5px solid var(--g200);border-radius:12px 0 12px 12px;padding:12px 14px;margin-bottom:10px;font-size:14px;line-height:1.6;max-width:88%;margin-left:auto}
.bubble-label{font-size:11px;font-weight:500;color:var(--g400);margin-bottom:4px;text-transform:uppercase;letter-spacing:.5px}
.thinking-wrap{background:var(--y50);border:1px solid var(--y200);border-radius:0 12px 12px 12px;padding:14px 18px;display:inline-flex;align-items:center;gap:10px;margin-bottom:10px}
.thinking-avatar{width:32px;height:32px;border-radius:10px;background:var(--y200);border:1px solid var(--y400);display:flex;align-items:center;justify-content:center;font-size:16px;flex-shrink:0}
.dots{display:flex;gap:5px;align-items:center}
.dot{width:8px;height:8px;border-radius:50%;display:inline-block}
.dot1{background:var(--y400);animation:blink 1.2s 0s infinite}
.dot2{background:var(--g400);animation:blink 1.2s .2s infinite}
.dot3{background:var(--g600);animation:blink 1.2s .4s infinite}
@keyframes blink{0%,80%,100%{transform:scale(1);opacity:.4}40%{transform:scale(1.3);opacity:1}}
.cause-row{display:flex;align-items:center;gap:10px;margin-bottom:10px}
.prob-track{height:6px;background:var(--g100);border-radius:3px;flex:1;overflow:hidden}
.prob-fill{height:100%;background:var(--y400);border-radius:3px}
.safety-row{display:flex;gap:10px;align-items:flex-start;margin-bottom:10px;font-size:14px;line-height:1.5}
.step-row{display:flex;gap:12px;align-items:flex-start;margin-bottom:12px;font-size:14px;line-height:1.5}
.safety-num{width:24px;height:24px;border-radius:50%;background:var(--y100);border:1px solid var(--y200);color:var(--g800);font-size:11px;font-weight:500;display:flex;align-items:center;justify-content:center;flex-shrink:0;margin-top:1px}
.step-circle{width:28px;height:28px;border-radius:50%;border:1.5px solid var(--g400);color:var(--g800);font-size:12px;font-weight:500;display:flex;align-items:center;justify-content:center;flex-shrink:0;margin-top:1px}
.contractor-card{background:white;border:0.5px solid #E5E5E0;border-radius:12px;padding:1rem;margin-bottom:.75rem}
.session-row{display:flex;justify-content:space-between;align-items:center;margin-bottom:8px}
div[data-testid="stButton"] button{border-radius:8px!important;font-family:'DM Sans',sans-serif!important}
div[data-testid="stButton"] button[kind="primary"]{background-color:var(--y400)!important;color:var(--g800)!important;border-color:var(--y400)!important}
div[data-testid="stButton"] button[kind="primary"]:hover{background-color:var(--y600)!important;color:#fff!important}
.stTextInput input,.stTextArea textarea,.stSelectbox select{border-radius:8px!important}
#MainMenu{visibility:hidden}footer{visibility:hidden}
header[data-testid="stHeader"]{background:transparent}
.block-container{padding-top:0!important}
</style>
""", unsafe_allow_html=True)


# ── Session state ──────────────────────────────────────────────────────────
def init():
    defaults = {
        "screen": "role",
        "chat": [],
        "session": None,
        "sessions": {},
        "homeowner_profile_id": None,
        "contractor_profile_id": None,
        "active_job_id": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init()


# ── Helpers ────────────────────────────────────────────────────────────────
def new_id(prefix=""):
    return f"{prefix}{int(datetime.now().timestamp()*1000)}"

def go(screen):
    st.session_state.screen = screen
    st.rerun()

def now_str():
    return datetime.now().strftime("%I:%M %p")

def generate_qr(job_id: str, contractor_name: str) -> Image.Image:
    """Generate a QR code containing job verification data."""
    verify_text = f"REPAIRGENIE-VERIFY|{job_id}|{contractor_name}"
    qr = qrcode.QRCode(version=1, box_size=8, border=3,
                        error_correction=qrcode.constants.ERROR_CORRECT_M)
    qr.add_data(verify_text)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#2C2C2A", back_color="#FFF8CC")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf


def call_backend(messages):
    resp = requests.post(f"{BACKEND_URL}/diagnose",
                         json={"messages": messages}, timeout=60)
    resp.raise_for_status()
    return resp.json()

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

def match_contractors(address: str, appliance: str) -> list:
    addr_lower = address.lower()
    appl_lower = appliance.lower()
    results = []
    for c in store.get_contractor_profiles():
        area_words = [w.strip() for w in c.get("service_area", "").lower().replace(",", " ").split()]
        area_match = any(w in addr_lower for w in area_words if len(w) > 2)
        spec_match = any(appl_lower in s.lower() or s.lower() in appl_lower
                         for s in c.get("specialties", []))
        if area_match and spec_match:
            results.append(c)
    return results


# ── Navbars ────────────────────────────────────────────────────────────────
def homeowner_navbar(show_describe=False):
    st.markdown("""<div class="rg-navbar">
      <div class="rg-navbar-brand"><div class="logo-icon">🧞</div><span>RepairGenie</span></div>
    </div>""", unsafe_allow_html=True)
    buttons = []
    if show_describe:
        buttons.append(("← Describe", "new-session"))
    buttons += [("🏠 Home", "home-main"), ("🕘 My Issues", "history"),
                ("💬 Messages", "homeowner-messages"), ("👤 My Profile", "homeowner-profile"),
                ("⇄ Role", "role")]
    cols = st.columns(len(buttons))
    for col, (lbl, target) in zip(cols, buttons):
        with col:
            if st.button(lbl, use_container_width=True, key=f"hnav_{target}_{st.session_state.screen}",
                         type="primary" if st.session_state.screen == target else "secondary"):
                go(target)

def contractor_navbar():
    st.markdown("""<div class="rg-navbar">
      <div class="rg-navbar-brand"><div class="logo-icon">🧞</div>
      <span>RepairGenie <span style="font-size:11px;font-weight:400;color:var(--g400)">· Contractor</span></span></div>
    </div>""", unsafe_allow_html=True)
    buttons = [("📋 Jobs", "contractor-jobs"), ("👤 Profile", "contractor-profile"), ("⇄ Role", "role")]
    cols = st.columns(len(buttons))
    for col, (lbl, target) in zip(cols, buttons):
        with col:
            if st.button(lbl, use_container_width=True, key=f"cnav_{target}_{st.session_state.screen}",
                         type="primary" if st.session_state.screen == target else "secondary"):
                go(target)


# ══════════════════════════════════════════════════════════════════════════
# ROLE PICKER
# ══════════════════════════════════════════════════════════════════════════
def screen_role():
    st.markdown("""<div class="hero-band">
      <div class="hero-logo">🧞</div>
      <h1>RepairGenie</h1>
      <p>AI-powered appliance diagnosis &amp; repair guidance</p>
    </div>""", unsafe_allow_html=True)
    st.markdown("")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""<div class="rg-card"><div style="font-size:24px;margin-bottom:.6rem">🏠</div>
          <h3 style="font-size:15px;font-weight:500;margin-bottom:4px">Homeowner</h3>
          <p style="font-size:12px;color:var(--g400);line-height:1.4">Diagnose an issue and get a step-by-step repair guide</p>
        </div>""", unsafe_allow_html=True)
        if st.button("I'm a Homeowner", type="primary", use_container_width=True):
            go("home-main")
    with col2:
        st.markdown("""<div class="rg-card"><div style="font-size:24px;margin-bottom:.6rem">🔧</div>
          <h3 style="font-size:15px;font-weight:500;margin-bottom:4px">Contractor</h3>
          <p style="font-size:12px;color:var(--g400);line-height:1.4">View job requests from homeowners near you</p>
        </div>""", unsafe_allow_html=True)
        if st.button("I'm a Contractor", use_container_width=True):
            go("contractor-portal")


# ══════════════════════════════════════════════════════════════════════════
# HOMEOWNER PROFILE
# ══════════════════════════════════════════════════════════════════════════
def screen_homeowner_profile():
    homeowner_navbar()
    st.markdown("""<div class="welcome-band"><h2>👤 My Profile</h2>
      <p>Contractors will use this to contact you when they accept a job.</p>
    </div>""", unsafe_allow_html=True)

    pid = st.session_state.homeowner_profile_id
    existing = store.get_homeowner_profile(pid) if pid else {}

    with st.form("hw_profile_form"):
        name    = st.text_input("Full name *",    value=existing.get("name", ""),    placeholder="e.g. Sarah Miller")
        phone   = st.text_input("Phone number *", value=existing.get("phone", ""),   placeholder="e.g. (201) 555-0123")
        address = st.text_input("Address *",      value=existing.get("address", ""), placeholder="e.g. 123 Main St, Jersey City NJ")
        saved   = st.form_submit_button("Save profile", type="primary", use_container_width=True)

    if saved:
        errors = []
        if not name.strip():    errors.append("Please enter your name.")
        if not phone.strip():   errors.append("Please enter your phone number.")
        if not address.strip(): errors.append("Please enter your address.")
        if errors:
            for e in errors: st.error(e)
        else:
            profile = {
                "id": pid or new_id("hw_"),
                "name": name.strip(), "phone": phone.strip(),
                "address": address.strip(), "saved": True,
            }
            store.save_homeowner_profile(profile)
            st.session_state.homeowner_profile_id = profile["id"]
            st.success("✓ Profile saved!")

    if existing.get("saved"):
        st.markdown(f"""<div class="rg-card">
          <div class="section-label">Your profile</div>
          <p style="font-size:15px;font-weight:500">{_html.escape(existing.get('name',''))}</p>
          <p style="font-size:13px;color:var(--g400)">📞 {_html.escape(existing.get('phone',''))}</p>
          <p style="font-size:13px;color:var(--g400)">📍 {_html.escape(existing.get('address',''))}</p>
        </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════
# HOMEOWNER MAIN
# ══════════════════════════════════════════════════════════════════════════
def screen_home_main():
    homeowner_navbar()
    st.markdown("""<div class="welcome-band"><h2>What needs fixing today?</h2>
      <p>Describe your appliance issue — the Genie will diagnose it and guide you through the fix.</p>
    </div>""", unsafe_allow_html=True)

    col1, col2 = st.columns([2, 3])
    with col1:
        if st.button("＋ New diagnosis", type="primary", use_container_width=True):
            st.session_state.chat = []
            st.session_state.session = None
            go("new-session")
    with col2:
        if st.session_state.sessions:
            if st.button(f"My sessions ({len(st.session_state.sessions)})", use_container_width=True):
                go("history")

    # Check for messages from contractors
    pid = st.session_state.homeowner_profile_id
    if pid:
        all_data = store.get()
        notifs = []
        for job_id, msgs in all_data["job_messages"].items():
            job = all_data["job_requests"].get(job_id, {})
            if job.get("homeowner_id") == pid:
                contractor_msgs = [m for m in msgs if m["sender"] == "contractor"]
                if contractor_msgs:
                    latest = contractor_msgs[-1]
                    notifs.append((job, latest))
        if notifs:
            st.markdown("")
            for job, msg in notifs[:3]:
                st.info(f"💬 **{_html.escape(msg['sender_name'])}** replied to your **{_html.escape(job.get('appliance',''))}** request: *\"{_html.escape(msg['text'][:60])}...\"*")
                if st.button("View conversation →", key=f"notif_{job['id']}"):
                    st.session_state.active_job_id = job["id"]
                    go("homeowner-chat")

    if st.session_state.sessions:
        st.markdown("")
        st.markdown('<p style="font-size:13px;color:var(--g600);font-weight:500">Recent sessions</p>', unsafe_allow_html=True)
        for s in list(reversed(list(st.session_state.sessions.values())))[:3]:
            badge = '<span class="badge-open">Open</span>' if not s.get("resolved") else '<span class="badge-done">Resolved</span>'
            st.markdown(f"""<div class="rg-card"><div class="session-row">
              <div><p style="font-size:14px;font-weight:500">{_html.escape(s['form'].get('appliance',''))} · {_html.escape(s['form'].get('brand',''))}</p>
              <p style="font-size:12px;color:var(--g400)">{_html.escape(s['form'].get('problem','')[:70])}...</p></div>
              {badge}</div></div>""", unsafe_allow_html=True)
            if st.button("Open →", key=f"r_{s['id']}"):
                st.session_state.session = s
                st.session_state.chat = s.get("chat", [])
                go("load-session")


# ══════════════════════════════════════════════════════════════════════════
# NEW SESSION FORM
# ══════════════════════════════════════════════════════════════════════════
def screen_new_session():
    homeowner_navbar()
    stepbar(1)
    st.markdown("**Tell the Genie about your appliance**")
    st.markdown("")

    appliance_type = st.selectbox("Appliance type *", [""] + APPLIANCES,
                                  format_func=lambda x: "Select appliance..." if x == "" else x)
    other_appliance = ""
    if appliance_type == "Other":
        other_appliance = st.text_input("Specify appliance *", placeholder="e.g. Wine cooler, pool pump...")

    brand   = st.text_input("Brand *",          placeholder="e.g. Whirlpool, Samsung, LG")
    model   = st.text_input("Model number *",    placeholder="e.g. WED5000DW")
    problem = st.text_area("Describe the problem *",
                            placeholder="What's happening? Any sounds, smells, error codes? When did it start?", height=110)
    files   = st.file_uploader("Photos or videos (optional)", accept_multiple_files=True,
                                type=["jpg","jpeg","png","mp4","mov"])

    if st.button("Ask the Genie ✨", type="primary", use_container_width=True):
        final_appliance = other_appliance.strip() if appliance_type == "Other" else appliance_type
        errors = []
        if not appliance_type:                                    errors.append("Please select an appliance type.")
        if appliance_type == "Other" and not other_appliance.strip(): errors.append("Please specify the appliance.")
        if not brand.strip():   errors.append("Please enter the brand.")
        if not model.strip():   errors.append("Please enter the model number.")
        if not problem.strip(): errors.append("Please describe the problem.")
        if errors:
            for e in errors: st.error(e)
            return

        file_names = [f.name for f in files] if files else []
        form = {"appliance": final_appliance, "brand": brand.strip(),
                "model": model.strip(), "problem": problem.strip(), "files": file_names}
        sess = {"id": new_id("sess_"), "form": form, "chat": [], "result": None,
                "resolved": False, "createdAt": datetime.now().isoformat()}
        st.session_state.session = sess
        user_msg = (f"Appliance: {final_appliance}\nBrand: {brand.strip()}\n"
                    f"Model: {model.strip()}\n\nProblem: {problem.strip()}")
        if file_names:
            user_msg += f"\n\nAttachments: {', '.join(file_names)}"
        st.session_state.chat = [{"role": "user", "content": user_msg}]
        go("followup")


# ══════════════════════════════════════════════════════════════════════════
# FOLLOWUP / CHAT
# ══════════════════════════════════════════════════════════════════════════
def screen_followup():
    homeowner_navbar(show_describe=True)
    stepbar(2)

    def clean_msg(content):
        c = content.split("REPAIR_RESULT:")[0].strip()
        return "" if (c.startswith("{") and '"causes"' in c) else c

    chat_html = '<div class="rg-card"><div style="display:flex;align-items:center;gap:8px;margin-bottom:1rem"><div style="width:32px;height:32px;border-radius:10px;background:var(--y100);border:1px solid var(--y200);display:flex;align-items:center;justify-content:center;font-size:16px">🧞</div><span style="font-size:14px;font-weight:500">Genie is on the case</span></div>'
    for msg in st.session_state.chat:
        if msg["role"] == "assistant":
            clean = clean_msg(msg["content"])
            if clean:
                chat_html += f'<div class="bubble-ai"><div class="bubble-label">Repair Genie</div>{_html.escape(clean)}</div>'
        else:
            chat_html += f'<div class="bubble-user"><div class="bubble-label">You</div>{_html.escape(msg["content"])}</div>'

    is_waiting = bool(st.session_state.chat and st.session_state.chat[-1]["role"] == "user")
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
                st.session_state.sessions[sess["id"]] = sess
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


# ══════════════════════════════════════════════════════════════════════════
# RESULTS
# ══════════════════════════════════════════════════════════════════════════
def screen_results():
    homeowner_navbar(show_describe=True)
    stepbar(3)

    sess = st.session_state.session
    res  = sess.get("result") if sess else None
    if not res:
        st.warning("No diagnosis found.")
        return

    form = sess.get("form", {})
    appliance_label = f"{_html.escape(form.get('appliance',''))} · {_html.escape(form.get('brand',''))} {_html.escape(form.get('model',''))}"

    causes_html = "".join(
        f'<div class="cause-row"><span style="flex:1;font-size:14px">{_html.escape(c["label"])}</span>'
        f'<div class="prob-track"><div class="prob-fill" style="width:{c["probability"]}%"></div></div>'
        f'<span style="font-size:13px;font-weight:500;color:var(--g800);min-width:34px;text-align:right">{c["probability"]}%</span></div>'
        for c in res.get("causes", [])
    )
    safety_html = "".join(
        f'<div class="safety-row"><div class="safety-num">{i+1}</div><span>{_html.escape(str(s))}</span></div>'
        for i, s in enumerate(res.get("safety", []))
    )
    st.markdown(f'<div class="rg-card"><div style="display:flex;align-items:center;gap:10px;margin-bottom:1rem"><div style="width:42px;height:42px;border-radius:12px;background:var(--y100);border:1px solid var(--y200);display:flex;align-items:center;justify-content:center;font-size:20px">🧞</div><div><p style="font-size:15px;font-weight:500">Genie\'s diagnosis</p><p style="font-size:12px;color:var(--g400)">{appliance_label}</p></div></div><div class="rg-divider"></div><div class="section-label">Possible root causes</div>{causes_html}<div class="rg-divider"></div><div class="section-label">⚠️ Safety checks — do these first</div>{safety_html}</div>', unsafe_allow_html=True)

    diy_possible = res.get("diy_possible", True)
    if diy_possible and res.get("diy_steps"):
        steps_html = "".join(
            f'<div class="step-row"><div class="step-circle">{i+1}</div><span>{_html.escape(str(s))}</span></div>'
            for i, s in enumerate(res.get("diy_steps", []))
        )
        note_html = f'<p style="font-size:13px;color:var(--g600);margin-top:.5rem">💡 {_html.escape(str(res["diy_note"]))}</p>' if res.get("diy_note") else ""
        st.markdown(f'<div class="rg-card"><div class="section-label">🔧 DIY fix — step by step</div>{steps_html}{note_html}</div>', unsafe_allow_html=True)
    else:
        st.warning(f"🚫 **This fix is not safe to DIY.** {_html.escape(str(res.get('diy_note','This repair requires a professional technician.')))}")

    needs_contractor = res.get("needs_contractor", False) or not diy_possible
    contractor_reason = res.get("contractor_reason", "")

    if needs_contractor:
        reason_html = f'<p style="font-size:14px;color:var(--g600);margin-bottom:.75rem">{_html.escape(contractor_reason)}</p>' if contractor_reason else ""
        st.markdown(f'<div class="rg-card"><div class="section-label">👷 You need a contractor</div>{reason_html}</div>', unsafe_allow_html=True)
        if st.button("🔍 Find contractors near me →", type="primary", use_container_width=True):
            go("find-contractor")
    else:
        st.markdown('<div class="rg-card"><div class="section-label">Still not fixed?</div><p style="font-size:13px;color:var(--g600);margin-bottom:.5rem">If the steps didn\'t help, a technician can take it from here.</p></div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if not sess.get("resolved"):
                if st.button("✓ Mark as resolved", use_container_width=True):
                    sess["resolved"] = True
                    st.session_state.sessions[sess["id"]] = sess
                    st.rerun()
            else:
                st.success("✓ Resolved")
        with col2:
            if st.button("Find a contractor →", use_container_width=True):
                go("find-contractor")


# ══════════════════════════════════════════════════════════════════════════
# FIND CONTRACTOR
# ══════════════════════════════════════════════════════════════════════════
def screen_find_contractor():
    homeowner_navbar(show_describe=True)

    sess     = st.session_state.session
    form     = sess.get("form", {}) if sess else {}
    appliance = form.get("appliance", "")

    pid = st.session_state.homeowner_profile_id
    hw_profile = store.get_homeowner_profile(pid) if pid else {}

    st.markdown("""<div class="welcome-band"><h2>👷 Find a contractor near you</h2>
      <p>Filtered by your location and appliance type. Only problem details are shared — no AI diagnosis.</p>
    </div>""", unsafe_allow_html=True)

    if not hw_profile.get("saved"):
        st.warning("⚠️ Please create a homeowner profile first so contractors know how to reach you.")
        if st.button("Create profile →", type="primary"):
            go("homeowner-profile")
        return

    if appliance:
        st.markdown(f'<p style="font-size:13px;color:var(--g600);margin-bottom:.75rem">Looking for contractors who specialise in <strong>{_html.escape(appliance)}</strong> repairs.</p>', unsafe_allow_html=True)

    # Pre-fill address from homeowner profile
    default_address = hw_profile.get("address", "")
    address = st.text_input("Your address", value=default_address,
                             placeholder="e.g. Jersey City NJ or 07302")

    if not address.strip():
        st.markdown('<p style="font-size:14px;color:var(--g400)">Enter your address above to see matching contractors.</p>', unsafe_allow_html=True)
        return

    matched = match_contractors(address.strip(), appliance)

    if not matched:
        st.warning(f"No contractors found in **{_html.escape(address.strip())}** who specialise in **{_html.escape(appliance)}** repairs.")
        st.caption("Try a nearby city, or ask a contractor to update their service area and specialties.")
        return

    st.markdown(f'<div class="section-label">{len(matched)} contractor{"s" if len(matched)!=1 else ""} found</div>', unsafe_allow_html=True)

    for c in matched:
        specs_str = ", ".join(c.get("specialties", [])[:4])
        avail_cls = "badge-today"
        st.markdown(f"""<div class="contractor-card">
          <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px">
            <div>
              <p style="font-size:14px;font-weight:500">{_html.escape(c.get('name',''))}</p>
              <p style="font-size:12px;color:var(--g400)">📍 {_html.escape(c.get('service_area',''))} · {c.get('years_exp',1)} yrs exp</p>
              <p style="font-size:12px;color:var(--g400);margin-top:2px">🔧 {_html.escape(specs_str)}</p>
            </div>
            <span class="{avail_cls}">Available</span>
          </div>
          <p style="font-size:13px;color:var(--y600);font-weight:500">📞 {_html.escape(c.get('phone',''))}</p>
        </div>""", unsafe_allow_html=True)

        if st.button(f"📋 Send job request to {c.get('name','')}", key=f"send_{c['id']}", use_container_width=True, type="primary"):
            job_id = new_id("job_")
            job = {
                "id": job_id,
                "homeowner_id": pid,
                "homeowner_name": hw_profile.get("name", "Homeowner"),
                "homeowner_phone": hw_profile.get("phone", ""),
                "homeowner_address": hw_profile.get("address", ""),
                "contractor_id": c["id"],
                "appliance": appliance,
                "brand": form.get("brand", ""),
                "model": form.get("model", ""),
                "problem": form.get("problem", ""),
                "files": form.get("files", []),
                "sent_to": [c["id"]],
                "sent_at": now_str(),
                "created_at": datetime.now().isoformat(),
            }
            store.save_job_request(job)
            # Seed opening message from homeowner
            store.add_message(job_id, {
                "sender": "homeowner",
                "sender_name": hw_profile.get("name", "Homeowner"),
                "text": f"Hi! I need help with my {appliance}. {form.get('problem', '')}",
                "ts": now_str(),
            })
            st.success(f"✓ Job request sent to {c['name']}! They'll see your problem details and contact you.")
        st.markdown("")


# ══════════════════════════════════════════════════════════════════════════
# HOMEOWNER CHAT (view messages from contractor)
# ══════════════════════════════════════════════════════════════════════════
def screen_homeowner_chat():
    homeowner_navbar()

    job_id = st.session_state.active_job_id
    if not job_id:
        go("home-main")
        return

    job = store.get_job(job_id)
    if not job:
        st.error("Job not found.")
        go("home-main")
        return

    # Get contractor name
    contractor_profiles = store.get_contractor_profiles()
    contractor = next((c for c in contractor_profiles if c["id"] == job.get("contractor_id")), {})
    contractor_name = contractor.get("name", "Contractor")

    st.markdown(f"""<div class="rg-card">
      <p style="font-size:15px;font-weight:500;margin-bottom:4px">💬 {_html.escape(job.get('appliance',''))} · {_html.escape(job.get('brand',''))}</p>
      <p style="font-size:12px;color:var(--g400)">Conversation with {_html.escape(contractor_name)}</p>
      <div class="rg-divider"></div>
      <div class="section-label">Job summary</div>
      <p style="font-size:14px;color:var(--g600);line-height:1.5">{_html.escape(job.get('problem',''))}</p>
    </div>""", unsafe_allow_html=True)

    pid = st.session_state.homeowner_profile_id
    hw_profile = store.get_homeowner_profile(pid) if pid else {}
    hw_name = hw_profile.get("name", "You")

    _render_chat_thread(job_id, "homeowner", hw_name, contractor_name)


# ══════════════════════════════════════════════════════════════════════════
# HISTORY
# ══════════════════════════════════════════════════════════════════════════
def screen_history():
    homeowner_navbar()
    st.markdown("### My sessions")
    if not st.session_state.sessions:
        st.info("No sessions yet.")
    else:
        for s in reversed(list(st.session_state.sessions.values())):
            badge = "Open" if not s.get("resolved") else "Resolved"
            col1, col2 = st.columns([5, 1])
            with col1:
                st.markdown(f"**{_html.escape(s['form'].get('appliance',''))} · {_html.escape(s['form'].get('brand',''))}** — `{badge}`")
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


# ══════════════════════════════════════════════════════════════════════════
# LOAD SESSION
# ══════════════════════════════════════════════════════════════════════════
def screen_load_session():
    homeowner_navbar()
    sess = st.session_state.session
    if not sess:
        return
    badge = "Open" if not sess.get("resolved") else "Resolved"
    st.markdown(f"### {_html.escape(sess['form'].get('appliance',''))} · {_html.escape(sess['form'].get('brand',''))} — `{badge}`")
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


# ══════════════════════════════════════════════════════════════════════════
# CONTRACTOR PORTAL ENTRY
# ══════════════════════════════════════════════════════════════════════════
def screen_contractor_portal():
    pid = st.session_state.contractor_profile_id
    if pid:
        profiles = {c["id"]: c for c in store.get_contractor_profiles()}
        if profiles.get(pid, {}).get("saved"):
            go("contractor-jobs")
            return
    go("contractor-profile")


# ══════════════════════════════════════════════════════════════════════════
# CONTRACTOR PROFILE
# ══════════════════════════════════════════════════════════════════════════
def screen_contractor_profile():
    contractor_navbar()
    st.markdown("""<div class="welcome-band"><h2>👤 My Profile</h2>
      <p>Homeowners will find you based on your service area and specialties.</p>
    </div>""", unsafe_allow_html=True)

    pid = st.session_state.contractor_profile_id
    existing = {}
    if pid:
        all_profiles = {c["id"]: c for c in store.get_contractor_profiles()}
        existing = all_profiles.get(pid, {})

    with st.form("contractor_profile_form"):
        name     = st.text_input("Full name *",           value=existing.get("name",""),         placeholder="e.g. John Smith")
        phone    = st.text_input("Phone number *",        value=existing.get("phone",""),        placeholder="e.g. (201) 555-0101")
        bio      = st.text_area("Bio",                    value=existing.get("bio",""),          placeholder="Tell homeowners about your experience...", height=90)
        years    = st.number_input("Years of experience *", min_value=1, max_value=50,           value=max(existing.get("years_exp",1), 1))
        area     = st.text_input("Service area *",        value=existing.get("service_area",""), placeholder="e.g. Jersey City, Hoboken, Newark NJ")
        specs    = st.multiselect("Specialties *",        SPECIALTY_OPTIONS,                     default=existing.get("specialties",[]))
        saved    = st.form_submit_button("Save profile",  type="primary", use_container_width=True)

    if saved:
        errors = []
        if not name.strip():  errors.append("Please enter your full name.")
        if not phone.strip(): errors.append("Please enter your phone number.")
        if not area.strip():  errors.append("Please enter your service area.")
        if not specs:         errors.append("Please select at least one specialty.")
        if errors:
            for e in errors: st.error(e)
        else:
            profile = {
                "id": pid or new_id("ct_"),
                "name": name.strip(), "phone": phone.strip(), "bio": bio.strip(),
                "years_exp": int(years), "service_area": area.strip(),
                "specialties": specs, "saved": True,
            }
            store.save_contractor_profile(profile)
            st.session_state.contractor_profile_id = profile["id"]
            st.success("✓ Profile saved! Homeowners can now find you.")

    if existing.get("saved"):
        specs_str = ", ".join(existing.get("specialties", []))
        st.markdown(f"""<div class="rg-card">
          <div class="section-label">Profile preview</div>
          <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:.6rem">
            <div>
              <p style="font-size:15px;font-weight:500">{_html.escape(existing.get('name',''))}</p>
              <p style="font-size:12px;color:var(--g400)">📍 {_html.escape(existing.get('service_area',''))} · {existing.get('years_exp',1)} yrs exp</p>
            </div>
            <span class="badge-today">Active</span>
          </div>
          <p style="font-size:13px;color:var(--g600);margin-bottom:.5rem">{_html.escape(existing.get('bio',''))}</p>
          <p style="font-size:12px;color:var(--g400)">🔧 {_html.escape(specs_str)}</p>
          <p style="font-size:12px;color:var(--y600);font-weight:500;margin-top:6px">📞 {_html.escape(existing.get('phone',''))}</p>
        </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════
# CONTRACTOR JOBS
# ══════════════════════════════════════════════════════════════════════════
def screen_contractor_jobs():
    contractor_navbar()

    pid = st.session_state.contractor_profile_id
    if not pid:
        st.warning("Please complete your profile first.")
        if st.button("Go to profile →", type="primary"):
            go("contractor-profile")
        return

    st.markdown("""<div class="welcome-band"><h2>📋 Job Requests</h2>
      <p>Homeowners who sent you a request are waiting for your response.</p>
    </div>""", unsafe_allow_html=True)

    jobs = store.get_jobs_for_contractor(pid)
    if not jobs:
        st.info("No job requests yet. Make sure your profile specialties and service area match homeowner needs.")
        return

    for job in reversed(jobs):
        job_id = job["id"]
        status = store.get_job_status(job_id)
        status_badge = {
            "pending":  '<span class="badge-open">Pending</span>',
            "accepted": '<span class="badge-accepted">Accepted</span>',
            "declined": '<span class="badge-declined">Declined</span>',
        }.get(status, '<span class="badge-open">Pending</span>')

        files_str = ", ".join(job.get("files", [])) or "None"
        st.markdown(f"""<div class="rg-card">
          <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:.6rem">
            <div>
              <p style="font-size:15px;font-weight:500">{_html.escape(job.get('appliance',''))} · {_html.escape(job.get('brand',''))}</p>
              <p style="font-size:12px;color:var(--g400)">👤 {_html.escape(job.get('homeowner_name',''))} · 📍 {_html.escape(job.get('homeowner_address',''))} · 🕐 {job.get('sent_at','')}</p>
            </div>
            {status_badge}
          </div>
          <p style="font-size:14px;color:var(--g600);margin-bottom:.5rem;line-height:1.5">{_html.escape(job.get('problem',''))}</p>
          <p style="font-size:12px;color:var(--g400)">📎 {_html.escape(files_str)}</p>
        </div>""", unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("✓ Accept", key=f"acc_{job_id}", use_container_width=True,
                         disabled=status != "pending", type="primary"):
                store.set_job_status(job_id, "accepted")
                st.rerun()
        with col2:
            if st.button("✗ Decline", key=f"dec_{job_id}", use_container_width=True,
                         disabled=status != "pending"):
                store.set_job_status(job_id, "declined")
                st.rerun()
        with col3:
            if st.button("💬 Message", key=f"msg_{job_id}", use_container_width=True,
                         disabled=status == "declined"):
                st.session_state.active_job_id = job_id
                go("contractor-chat")

        # QR + resolve inline (only when accepted)
        if status == "accepted":
            with st.expander("🪪 Show identity QR code & mark complete", expanded=False):
                qr_buf = generate_qr(job_id, my_name)
                col_l, col_m, col_r = st.columns([1,2,1])
                with col_m:
                    st.image(qr_buf, caption=f"Job ref: {job_id[-8:].upper()}", use_column_width=True)
                st.markdown(f"""<div style="background:var(--y50);border:1px solid var(--y200);border-radius:8px;padding:10px 14px;margin-bottom:10px">
                  <div style="display:flex;justify-content:space-between;margin-bottom:6px"><span style="font-size:12px;color:var(--g400)">Contractor</span><span style="font-size:13px;font-weight:600">{_html.escape(my_name)}</span></div>
                  <div style="display:flex;justify-content:space-between"><span style="font-size:12px;color:var(--g400)">Job ref</span><span style="font-size:13px;font-weight:600;font-family:monospace">{job_id[-8:].upper()}</span></div>
                </div>""", unsafe_allow_html=True)
                refreshed_job = store.get_job(job_id)
                if store.is_fully_resolved(refreshed_job):
                    st.success("🎉 Job fully resolved and confirmed by both parties!")
                elif refreshed_job.get("contractor_complete"):
                    st.info("⏳ Waiting for homeowner to confirm resolution.")
                else:
                    if st.button("✅ Mark work as complete", key=f"done_{job_id}",
                                 type="primary", use_container_width=True):
                        store.set_contractor_complete(job_id)
                        st.success("✓ Marked complete — homeowner will be asked to confirm.")
                        st.rerun()
        st.markdown("")


# ══════════════════════════════════════════════════════════════════════════
# SHARED CHAT RENDERER
# ══════════════════════════════════════════════════════════════════════════
def _render_chat_thread(job_id: str, my_role: str, my_name: str, other_name: str):
    """Renders a two-way chat thread for both homeowner and contractor views."""
    messages = store.get_messages(job_id)
    status   = store.get_job_status(job_id)

    if not messages:
        st.info("No messages yet. Send the first message below.")
    else:
        chat_html = '<div style="margin-bottom:1rem">'
        for m in messages:
            is_me = m["sender"] == my_role
            name  = _html.escape(m.get("sender_name", my_name if is_me else other_name))
            text  = _html.escape(m.get("text", ""))
            ts    = _html.escape(m.get("ts", ""))
            media_keys = m.get("media_keys", [])
            media_html = ""
            if media_keys:
                media_html = "<div style='margin-top:6px;display:flex;flex-wrap:wrap;gap:6px'>"
                for key in media_keys:
                    mdata = store.get_media(key)
                    fname = mdata.get("filename", key)
                    media_html += f'<span style="font-size:12px;background:rgba(0,0,0,.06);padding:3px 8px;border-radius:20px">📎 {_html.escape(fname)}</span>'
                media_html += "</div>"
            if is_me:
                chat_html += f'''<div style="display:flex;justify-content:flex-end;margin-bottom:10px">
                  <div style="max-width:80%;margin-left:auto">
                    <div style="font-size:11px;font-weight:500;color:var(--g400);text-align:right;margin-bottom:3px;text-transform:uppercase;letter-spacing:.4px">{name}</div>
                    <div style="background:var(--y200);border:1px solid var(--y400);border-radius:12px 0 12px 12px;padding:10px 14px;font-size:14px;line-height:1.5">{text}{media_html}</div>
                    <div style="font-size:11px;color:var(--g400);text-align:right;margin-top:3px">{ts}</div>
                  </div>
                </div>'''
            else:
                chat_html += f'''<div style="display:flex;justify-content:flex-start;margin-bottom:10px">
                  <div style="max-width:80%">
                    <div style="font-size:11px;font-weight:500;color:var(--g400);margin-bottom:3px;text-transform:uppercase;letter-spacing:.4px">{name}</div>
                    <div style="background:var(--g100);border:1px solid var(--g200);border-radius:0 12px 12px 12px;padding:10px 14px;font-size:14px;line-height:1.5">{text}{media_html}</div>
                    <div style="font-size:11px;color:var(--g400);margin-top:3px">{ts}</div>
                  </div>
                </div>'''
        chat_html += '</div>'
        st.markdown(chat_html, unsafe_allow_html=True)

    # Render actual images below chat (st.image needed for real display)
    for m in messages:
        for key in m.get("media_keys", []):
            mdata = store.get_media(key)
            if not mdata:
                continue
            fname    = mdata.get("filename", "")
            b64_data = mdata.get("data", "")
            is_image = any(fname.lower().endswith(ext) for ext in [".jpg",".jpeg",".png",".gif",".webp"])
            sender_label = f"{m.get('sender_name','Unknown')} sent:"
            st.caption(f"📎 {sender_label} **{fname}**")
            if is_image and b64_data:
                img_bytes = base64.b64decode(b64_data)
                st.image(img_bytes, caption=fname, use_column_width=True)
            elif b64_data:
                dl_b64 = b64_data
                href = f'<a href="data:application/octet-stream;base64,{dl_b64}" download="{_html.escape(fname)}" style="font-size:13px;color:var(--y600);font-weight:500">⬇ Download {_html.escape(fname)}</a>'
                st.markdown(href, unsafe_allow_html=True)

    if status == "declined":
        st.warning("This job was declined. Messaging is disabled.")
        return

    # Message input with optional media upload
    with st.form(f"chat_{job_id}_{my_role}", clear_on_submit=True):
        msg_input = st.text_input("Type a message...", label_visibility="collapsed",
                                   placeholder=f"Message {'the contractor' if my_role=='homeowner' else 'the homeowner'}...")
        uploaded = st.file_uploader("Attach photos or videos (optional)",
                                     accept_multiple_files=True,
                                     type=["jpg","jpeg","png","mp4","mov"],
                                     label_visibility="collapsed")
        col1, col2 = st.columns([4, 1])
        with col1:
            st.caption("📎 Attach photos or videos (optional)")
        with col2:
            send = st.form_submit_button("Send →", type="primary", use_container_width=True)

    if send and (msg_input.strip() or uploaded):
        msg_id = new_id("msg_")
        media_keys = []
        if uploaded:
            for f in uploaded:
                key = f"{msg_id}_{f.name}"
                b64 = base64.b64encode(f.read()).decode()
                store.save_media(key, f.name, b64)
                media_keys.append(key)
        store.add_message(job_id, {
            "sender": my_role,
            "sender_name": my_name,
            "text": msg_input.strip() if msg_input.strip() else "📎 Sent attachment(s)",
            "media_keys": media_keys,
            "ts": now_str(),
        })
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════
# CONTRACTOR CHAT
# ══════════════════════════════════════════════════════════════════════════
def screen_contractor_chat():
    contractor_navbar()

    job_id = st.session_state.active_job_id
    if not job_id:
        go("contractor-jobs")
        return

    job = store.get_job(job_id)
    if not job:
        st.error("Job not found.")
        go("contractor-jobs")
        return

    pid = st.session_state.contractor_profile_id
    all_profiles = {c["id"]: c for c in store.get_contractor_profiles()}
    my_profile   = all_profiles.get(pid, {})
    my_name      = my_profile.get("name", "Contractor")

    st.markdown(f"""<div class="rg-card">
      <p style="font-size:15px;font-weight:500;margin-bottom:4px">💬 {_html.escape(job.get('appliance',''))} · {_html.escape(job.get('brand',''))}</p>
      <p style="font-size:12px;color:var(--g400)">Conversation with {_html.escape(job.get('homeowner_name','Homeowner'))}</p>
      <div class="rg-divider"></div>
      <div class="section-label">Job details</div>
      <p style="font-size:14px;color:var(--g600);line-height:1.5;margin-bottom:.4rem">{_html.escape(job.get('problem',''))}</p>
      <p style="font-size:12px;color:var(--g400)">Model: {_html.escape(job.get('model',''))} · 📍 {_html.escape(job.get('homeowner_address',''))}</p>
      <p style="font-size:12px;color:var(--y600);font-weight:500;margin-top:4px">📞 {_html.escape(job.get('homeowner_phone',''))}</p>
    </div>""", unsafe_allow_html=True)

    _render_chat_thread(job_id, "contractor", my_name, job.get("homeowner_name", "Homeowner"))


# ══════════════════════════════════════════════════════════════════════════
# HOMEOWNER MESSAGES
# ══════════════════════════════════════════════════════════════════════════
def screen_homeowner_messages():
    homeowner_navbar()
    st.markdown("""<div class="welcome-band"><h2>💬 My Messages</h2>
      <p>Conversations with contractors about your job requests.</p>
    </div>""", unsafe_allow_html=True)

    pid = st.session_state.homeowner_profile_id
    if not pid:
        st.info("Create a homeowner profile and send a job request to start messaging contractors.")
        if st.button("Create profile →", type="primary"):
            go("homeowner-profile")
        return

    all_data = store.get()
    my_jobs = [j for j in all_data["job_requests"].values() if j.get("homeowner_id") == pid]

    if not my_jobs:
        st.info("No job requests sent yet. Get a diagnosis and send a job request to a contractor.")
        if st.button("＋ New diagnosis", type="primary"):
            go("new-session")
        return

    # Get contractor profiles for name lookup
    contractor_map = {c["id"]: c for c in store.get_contractor_profiles()}

    found_any = False
    for job in reversed(my_jobs):
        job_id      = job["id"]
        messages    = store.get_messages(job_id)
        status      = store.get_job_status(job_id)
        contractor  = contractor_map.get(job.get("contractor_id",""), {})
        c_name      = contractor.get("name", "Contractor")

        # Count unread contractor messages
        contractor_msgs = [m for m in messages if m["sender"] == "contractor"]
        last_msg = contractor_msgs[-1] if contractor_msgs else None

        status_badge = {
            "pending":  '<span class="badge-open">Pending</span>',
            "accepted": '<span class="badge-accepted" style="background:#EAF3DE;color:#27500A;font-size:11px;padding:2px 8px;border-radius:20px">Accepted</span>',
            "declined": '<span class="badge-done">Declined</span>',
        }.get(status, '<span class="badge-open">Pending</span>')

        preview = f'"{_html.escape(last_msg["text"][:60])}..."' if last_msg else "No messages from contractor yet"
        found_any = True

        st.markdown(f"""<div class="rg-card">
          <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:6px">
            <div>
              <p style="font-size:14px;font-weight:500">{_html.escape(job.get('appliance',''))} · {_html.escape(job.get('brand',''))}</p>
              <p style="font-size:12px;color:var(--g400)">🔧 {_html.escape(c_name)} · 🕐 {job.get('sent_at','')}</p>
            </div>
            {status_badge}
          </div>
          <p style="font-size:13px;color:var(--g600);font-style:italic">{preview}</p>
        </div>""", unsafe_allow_html=True)

        if st.button("💬 Open conversation →", key=f"open_conv_{job_id}", use_container_width=True):
            st.session_state.active_job_id = job_id
            go("homeowner-chat")

        # QR verify + resolution inline
        refreshed_job = store.get_job(job_id)
        if status in ("accepted", "resolved") or refreshed_job.get("contractor_complete"):
            label = "🪪 Verify contractor & resolve issue"
            if store.is_fully_resolved(refreshed_job):
                label = "✅ Issue resolved"
            with st.expander(label, expanded=refreshed_job.get("contractor_complete", False) and not store.is_fully_resolved(refreshed_job)):
                # QR for matching
                c_name_verify = contractor_map.get(job.get("contractor_id",""), {}).get("name", "Contractor")
                qr_buf = generate_qr(job_id, c_name_verify)
                col_l, col_m, col_r = st.columns([1,2,1])
                with col_m:
                    st.image(qr_buf, caption="Match this with contractor's QR", use_column_width=True)
                st.markdown(f"""<div style="background:var(--y50);border:1px solid var(--y200);border-radius:8px;padding:10px 14px;margin-bottom:10px">
                  <div style="display:flex;justify-content:space-between;margin-bottom:6px"><span style="font-size:12px;color:var(--g400)">Contractor</span><span style="font-size:13px;font-weight:600">{_html.escape(c_name_verify)}</span></div>
                  <div style="display:flex;justify-content:space-between"><span style="font-size:12px;color:var(--g400)">Job ref</span><span style="font-size:13px;font-weight:600;font-family:monospace">{job_id[-8:].upper()}</span></div>
                </div>""", unsafe_allow_html=True)
                if store.is_fully_resolved(refreshed_job):
                    st.success("🎉 Issue fully resolved and confirmed by both parties!")
                elif refreshed_job.get("contractor_complete"):
                    st.markdown("**Contractor marked the work as complete. Was the issue resolved?**")
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("✅ Yes, resolved!", key=f"confirm_{job_id}",
                                     type="primary", use_container_width=True):
                            store.set_homeowner_confirmed(job_id)
                            for sess in st.session_state.sessions.values():
                                if sess["form"].get("appliance") == job.get("appliance"):
                                    sess["resolved"] = True
                            st.balloons()
                            st.success("🎉 Issue marked as resolved!")
                            st.rerun()
                    with c2:
                        if st.button("❌ Not yet fixed", key=f"notfixed_{job_id}",
                                     use_container_width=True):
                            st.warning("Message the contractor to discuss next steps.")
                else:
                    st.info("⏳ Waiting for contractor to mark work as complete.")
        st.markdown("")

    if not found_any:
        st.info("No conversations yet.")


# ══════════════════════════════════════════════════════════════════════════
# CONTRACTOR VERIFY SCREEN (contractor shows QR to homeowner)
# ══════════════════════════════════════════════════════════════════════════
def screen_contractor_verify():
    contractor_navbar()

    job_id = st.session_state.active_job_id
    if not job_id:
        go("contractor-jobs")
        return

    job = store.get_job(job_id)
    if not job:
        go("contractor-jobs")
        return

    pid = st.session_state.contractor_profile_id
    all_profiles = {c["id"]: c for c in store.get_contractor_profiles()}
    my_profile   = all_profiles.get(pid, {})
    my_name      = my_profile.get("name", "Contractor")

    st.markdown(f"""<div class="rg-card">
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:.75rem">
        <span style="font-size:28px">🪪</span>
        <div>
          <p style="font-size:15px;font-weight:500">Identity Verification</p>
          <p style="font-size:12px;color:var(--g400)">{_html.escape(job.get('appliance',''))} · {_html.escape(job.get('homeowner_name',''))}</p>
        </div>
      </div>
      <div class="rg-divider"></div>
      <p style="font-size:14px;color:var(--g600);line-height:1.6;margin-bottom:.5rem">
        Show this QR code to the homeowner. They will scan or match it in their app to verify your identity before letting you in.
      </p>
    </div>""", unsafe_allow_html=True)

    # Generate and display QR code
    qr_buf = generate_qr(job_id, my_name)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(qr_buf, caption=f"Job ID: {job_id[-8:].upper()}", use_column_width=True)

    # Verification details card
    st.markdown(f"""<div class="rg-card">
      <div class="section-label">Verification details</div>
      <div style="display:flex;justify-content:space-between;margin-bottom:8px">
        <span style="font-size:13px;color:var(--g400)">Contractor</span>
        <span style="font-size:13px;font-weight:500">{_html.escape(my_name)}</span>
      </div>
      <div style="display:flex;justify-content:space-between;margin-bottom:8px">
        <span style="font-size:13px;color:var(--g400)">Job reference</span>
        <span style="font-size:13px;font-weight:500;font-family:monospace">{job_id[-8:].upper()}</span>
      </div>
      <div style="display:flex;justify-content:space-between;margin-bottom:8px">
        <span style="font-size:13px;color:var(--g400)">Appliance</span>
        <span style="font-size:13px;font-weight:500">{_html.escape(job.get('appliance',''))} · {_html.escape(job.get('brand',''))}</span>
      </div>
      <div style="display:flex;justify-content:space-between">
        <span style="font-size:13px;color:var(--g400)">Homeowner</span>
        <span style="font-size:13px;font-weight:500">{_html.escape(job.get('homeowner_name',''))}</span>
      </div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="rg-divider"></div>', unsafe_allow_html=True)
    st.markdown("**Once the job is done:**")
    if not job.get("contractor_complete"):
        if st.button("✅ Mark work as complete", type="primary", use_container_width=True):
            store.set_contractor_complete(job_id)
            st.success("✓ Marked as complete. Waiting for homeowner to confirm.")
            st.rerun()
    else:
        st.success("✓ You marked this job as complete.")
        if store.is_fully_resolved(job):
            st.balloons()
            st.success("🎉 Homeowner confirmed! This job is fully resolved.")
        else:
            st.info("⏳ Waiting for homeowner to confirm resolution.")


# ══════════════════════════════════════════════════════════════════════════
# HOMEOWNER VERIFY SCREEN (homeowner matches QR shown by contractor)
# ══════════════════════════════════════════════════════════════════════════
def screen_homeowner_verify():
    homeowner_navbar()

    job_id = st.session_state.active_job_id
    if not job_id:
        go("homeowner-messages")
        return

    job = store.get_job(job_id)
    if not job:
        go("homeowner-messages")
        return

    contractor_map = {c["id"]: c for c in store.get_contractor_profiles()}
    contractor     = contractor_map.get(job.get("contractor_id",""), {})
    c_name         = contractor.get("name", "Contractor")

    st.markdown(f"""<div class="rg-card">
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:.75rem">
        <span style="font-size:28px">🪪</span>
        <div>
          <p style="font-size:15px;font-weight:500">Verify Contractor Identity</p>
          <p style="font-size:12px;color:var(--g400)">{_html.escape(job.get('appliance',''))} repair</p>
        </div>
      </div>
      <div class="rg-divider"></div>
      <p style="font-size:14px;color:var(--g600);line-height:1.6">
        Ask the contractor to show their QR code. Match the <strong>Job Reference</strong> and <strong>Contractor Name</strong> below to verify their identity before letting them in.
      </p>
    </div>""", unsafe_allow_html=True)

    # Show expected QR for comparison
    qr_buf = generate_qr(job_id, c_name)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(qr_buf, caption="Expected QR code", use_column_width=True)

    # Match checklist
    st.markdown(f"""<div class="rg-card">
      <div class="section-label">✅ Match these details with the contractor's QR code</div>
      <div style="display:flex;justify-content:space-between;margin-bottom:10px;padding:8px 12px;background:var(--y50);border:1px solid var(--y200);border-radius:8px">
        <span style="font-size:13px;color:var(--g600)">Contractor name</span>
        <span style="font-size:14px;font-weight:600;color:var(--g800)">{_html.escape(c_name)}</span>
      </div>
      <div style="display:flex;justify-content:space-between;margin-bottom:10px;padding:8px 12px;background:var(--y50);border:1px solid var(--y200);border-radius:8px">
        <span style="font-size:13px;color:var(--g600)">Job reference</span>
        <span style="font-size:14px;font-weight:600;font-family:monospace;color:var(--g800)">{job_id[-8:].upper()}</span>
      </div>
      <div style="display:flex;justify-content:space-between;padding:8px 12px;background:var(--y50);border:1px solid var(--y200);border-radius:8px">
        <span style="font-size:13px;color:var(--g600)">Appliance</span>
        <span style="font-size:14px;font-weight:600;color:var(--g800)">{_html.escape(job.get('appliance',''))} · {_html.escape(job.get('brand',''))}</span>
      </div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="rg-divider"></div>', unsafe_allow_html=True)

    # Resolution confirmation
    if store.is_fully_resolved(job):
        st.balloons()
        st.success("🎉 Issue fully resolved and confirmed by both parties!")
    elif job.get("contractor_complete") and not job.get("homeowner_confirmed"):
        st.info("🔧 The contractor has marked the work as complete.")
        st.markdown("**Was the issue resolved to your satisfaction?**")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Yes, issue is resolved", type="primary", use_container_width=True):
                store.set_homeowner_confirmed(job_id)
                # Also mark in local session if exists
                for sess in st.session_state.sessions.values():
                    if sess["form"].get("appliance") == job.get("appliance"):
                        sess["resolved"] = True
                st.balloons()
                st.success("🎉 Issue marked as fully resolved! Thank you.")
                st.rerun()
        with col2:
            if st.button("❌ No, still not fixed", use_container_width=True):
                st.warning("Please message the contractor to discuss next steps.")
    elif not job.get("contractor_complete"):
        st.info("⏳ Waiting for the contractor to mark work as complete.")


# ══════════════════════════════════════════════════════════════════════════
# ROUTER
# ══════════════════════════════════════════════════════════════════════════
{
    "role":              screen_role,
    "homeowner-profile": screen_homeowner_profile,
    "home-main":         screen_home_main,
    "new-session":       screen_new_session,
    "followup":          screen_followup,
    "results":           screen_results,
    "find-contractor":   screen_find_contractor,
    "homeowner-chat":    screen_homeowner_chat,
    "homeowner-messages":screen_homeowner_messages,
    "homeowner-verify":  screen_homeowner_verify,
    "history":           screen_history,
    "load-session":      screen_load_session,
    "contractor-portal": screen_contractor_portal,
    "contractor-profile":screen_contractor_profile,
    "contractor-jobs":   screen_contractor_jobs,
    "contractor-chat":   screen_contractor_chat,
    "contractor-verify": screen_contractor_verify,
}.get(st.session_state.screen, screen_role)()
