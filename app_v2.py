import streamlit as st
from datetime import datetime
import random
import time

st.set_page_config(page_title="SmartSort", page_icon="♻️", layout="centered", initial_sidebar_state="collapsed")

RECYCLABLE_MAP = {
    "Plastic Bottle":  {"bin": "Plastic",      "category": "Hard Plastic",      "recyclable": True,  "tip": "Rinse before recycling. Remove cap if possible."},
    "Glass Jar":       {"bin": "Glass",         "category": "Glass",             "recyclable": True,  "tip": "Remove lid and rinse. Labels are fine to leave on."},
    "Cardboard Box":   {"bin": "Paper",         "category": "Paper / Cardboard", "recyclable": True,  "tip": "Flatten to save space. Remove tape if possible."},
    "Food Waste":      {"bin": "General Waste", "category": "Organic",           "recyclable": False, "tip": "Consider composting! Not suitable for recycling bins."},
    "Aluminium Can":   {"bin": "Metal",         "category": "Metal",             "recyclable": True,  "tip": "Rinse cans. Crush them to save space."},
    "Plastic Bag":     {"bin": "General Waste", "category": "Soft Plastic",      "recyclable": False, "tip": "Some supermarkets accept soft plastics. Never put in kerbside bins."},
}
BIN_COLORS = {"Plastic":"#F5C518","Paper":"#2196F3","Glass":"#4CAF50","Metal":"#FF9800","General Waste":"#9E9E9E"}
BIN_ICONS  = {"Plastic":"🟡","Paper":"🔵","Glass":"🟢","Metal":"🟠","General Waste":"⚫"}
DEMO_HISTORY = [
    {"item":"Plastic Bottle","date":"Today, 09:14",    "recyclable":True, "bin":"Plastic"},
    {"item":"Cardboard Box", "date":"Today, 08:52",    "recyclable":True, "bin":"Paper"},
    {"item":"Food Waste",    "date":"Yesterday, 19:30","recyclable":False,"bin":"General Waste"},
    {"item":"Aluminium Can", "date":"Yesterday, 13:11","recyclable":True, "bin":"Metal"},
    {"item":"Glass Jar",     "date":"Mon, 10:05",      "recyclable":True, "bin":"Glass"},
    {"item":"Plastic Bag",   "date":"Mon, 09:47",      "recyclable":False,"bin":"General Waste"},
]

if "page"         not in st.session_state: st.session_state.page         = "camera"
if "result"       not in st.session_state: st.session_state.result       = None
if "logged_in"    not in st.session_state: st.session_state.logged_in    = True
if "history"      not in st.session_state: st.session_state.history      = list(DEMO_HISTORY)
if "uploaded_img" not in st.session_state: st.session_state.uploaded_img = None
if "dark_mode"    not in st.session_state: st.session_state.dark_mode    = True

# ── Theme variables ────────────────────────────────────────────────────────────
dark = st.session_state.dark_mode
BG        = "#0f0f0f"  if dark else "#f5f5f0"
BG2       = "#111"     if dark else "#ffffff"
TEXT      = "#ffffff"  if dark else "#111111"
TEXT_MUT  = "rgba(255,255,255,0.4)" if dark else "rgba(0,0,0,0.45)"
TEXT_SUB  = "rgba(255,255,255,0.5)" if dark else "rgba(0,0,0,0.5)"
CARD_BG   = "rgba(255,255,255,0.04)" if dark else "rgba(0,0,0,0.04)"
CARD_BD   = "rgba(255,255,255,0.08)" if dark else "rgba(0,0,0,0.10)"
HR        = "rgba(255,255,255,0.07)" if dark else "rgba(0,0,0,0.10)"
INPUT_BG  = "rgba(255,255,255,0.05)" if dark else "rgba(0,0,0,0.05)"
INPUT_BD  = "rgba(255,255,255,0.1)"  if dark else "rgba(0,0,0,0.15)"
UPLOAD_BD = "rgba(126,217,87,0.3)"
VIEW_BG   = "linear-gradient(160deg,#0a120a,#111a0f)" if dark else "linear-gradient(160deg,#e8f5e2,#f0f8eb)"
VIEW_TX   = "rgba(255,255,255,0.35)" if dark else "rgba(0,0,0,0.35)"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=Space+Mono:wght@400;700&display=swap');
html,body,[class*="css"]{{font-family:'DM Sans',sans-serif!important;background-color:{BG}!important;color:{TEXT};}}
#MainMenu,footer,header{{visibility:hidden;}}
.stDeployButton,[data-testid="stToolbar"],[data-testid="stDecoration"],[data-testid="stSidebar"]{{display:none;}}
.block-container{{padding-top:1rem!important;padding-bottom:1rem!important;max-width:480px!important;}}
.stButton>button{{font-family:'DM Sans',sans-serif!important;font-weight:600!important;border-radius:14px!important;border:none!important;transition:all .2s ease!important;width:100%!important;}}
.stButton>button:hover{{transform:translateY(-1px);filter:brightness(1.1);}}
[data-testid="stFileUploader"]{{background:{CARD_BG}!important;border:2px dashed {UPLOAD_BD}!important;border-radius:16px!important;padding:8px!important;}}
[data-testid="stFileUploaderDropzone"]{{background:transparent!important;}}
.stTextInput>div>div{{border-color:{INPUT_BD}!important;background:{INPUT_BG}!important;color:{TEXT}!important;}}
hr{{border-color:{HR}!important;}}
</style>
""", unsafe_allow_html=True)

def h(content):
    st.markdown(content, unsafe_allow_html=True)

def card(content, bg=None, border=None):
    bg     = bg     or CARD_BG
    border = border or CARD_BD
    h(f'<div style="background:{bg};border:1px solid {border};border-radius:16px;padding:16px 20px;margin-bottom:12px;">{content}</div>')

def slabel(text):
    h(f'<div style="color:{TEXT_MUT};font-size:11px;font-family:Space Mono,monospace;letter-spacing:2px;margin-bottom:10px;margin-top:4px;">{text}</div>')

def nav_bar():
    c1,c2,c3 = st.columns(3)
    with c1:
        if st.button("← Result",   key="nav_result",  use_container_width=True): st.session_state.page="result";  st.rerun()
    with c2:
        if st.button("📷 Camera",  key="nav_camera",  use_container_width=True): st.session_state.page="camera";  st.rerun()
    with c3:
        if st.button("Profile →",  key="nav_profile", use_container_width=True): st.session_state.page="profile"; st.rerun()

def page_camera():
    h(f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;"><div><div style="color:#7ED957;font-family:Space Mono,monospace;font-size:11px;letter-spacing:2px;">SMART SORT</div><div style="font-size:24px;font-weight:700;color:{TEXT};">Classify Item</div></div><div style="font-size:28px;">♻️</div></div>')
    slabel("UPLOAD OR TAKE A PHOTO")
    uploaded = st.file_uploader("Upload image", type=["jpg","jpeg","png","webp"], label_visibility="collapsed")
    if uploaded:
        st.session_state.uploaded_img = uploaded
        st.image(uploaded, use_container_width=True)
        h(f'<div style="text-align:center;color:{TEXT_MUT};font-size:12px;margin-top:4px;margin-bottom:8px;">Image ready to classify</div>')
    else:
        h(f'<div style="background:{VIEW_BG};border:2px dashed rgba(126,217,87,0.25);border-radius:20px;height:200px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:12px;margin-bottom:12px;"><div style="font-size:48px;opacity:0.6;">📷</div><div style="color:{VIEW_TX};font-size:13px;">Upload a photo to classify</div></div>')

    st.markdown(" ")
    disabled = uploaded is None
    if st.button("♻️  Classify Item", disabled=disabled, use_container_width=True, type="primary"):
        with st.spinner("Analysing…"):
            time.sleep(1.5)
        item_name = random.choice(list(RECYCLABLE_MAP.keys()))
        result = {"item": item_name, **RECYCLABLE_MAP[item_name]}
        st.session_state.result = result
        st.session_state.history.insert(0, {"item":item_name,"date":datetime.now().strftime("Today, %H:%M"),"recyclable":result["recyclable"],"bin":result["bin"]})
        st.session_state.page = "result"
        st.rerun()
    if disabled:
        h(f'<div style="text-align:center;color:{TEXT_MUT};font-size:12px;margin-top:6px;">Upload an image first</div>')

    st.markdown("---")
    slabel("HOW IT WORKS")
    for icon, title, desc in [
        ("1️⃣","Upload a photo",   "Take a picture of any item you're unsure about"),
        ("2️⃣","AI classifies it", "YOLOv8 identifies the material type instantly"),
        ("3️⃣","Get your answer",  "See which bin to use and recycling tips"),
    ]:
        card(f'<div style="display:flex;gap:16px;align-items:flex-start;"><div style="font-size:22px;">{icon}</div><div><div style="color:{TEXT};font-weight:600;font-size:14px;">{title}</div><div style="color:{TEXT_SUB};font-size:12px;margin-top:3px;">{desc}</div></div></div>')

def page_result():
    if st.session_state.result is None:
        h(f'<div style="text-align:center;padding:60px 20px;"><div style="font-size:52px;margin-bottom:16px;">📸</div><div style="color:{TEXT_MUT};font-size:14px;line-height:1.8;">No result yet.<br>Go to the Camera tab and classify an item first.</div></div>')
        if st.button("Go to Camera →", use_container_width=True):
            st.session_state.page="camera"; st.rerun()
        return

    r = st.session_state.result
    bc  = BIN_COLORS.get(r["bin"],"#7ED957")
    bi  = BIN_ICONS.get(r["bin"],"🗑️")
    rec = r["recyclable"]
    vbg = "rgba(126,217,87,0.12)" if rec else "rgba(255,80,80,0.12)"
    vbd = "rgba(126,217,87,0.3)"  if rec else "rgba(255,80,80,0.3)"
    vc  = "#7ED957"               if rec else "#FF5050"
    vi  = "♻️"                    if rec else "🚫"
    vt  = "Recyclable!"           if rec else "Not Recyclable"

    h(f'<div style="margin-bottom:16px;"><div style="color:{TEXT_MUT};font-family:Space Mono,monospace;font-size:11px;letter-spacing:2px;margin-bottom:6px;">CLASSIFICATION RESULT</div><div style="font-size:24px;font-weight:700;color:{TEXT};">{r["item"]}</div><div style="color:{TEXT_MUT};font-size:13px;">{r["category"]}</div></div>')
    if st.session_state.uploaded_img:
        st.image(st.session_state.uploaded_img, use_container_width=True)
        st.markdown(" ")

    card(f'<div style="display:flex;align-items:center;gap:18px;"><div style="width:56px;height:56px;border-radius:28px;background:{vc};display:flex;align-items:center;justify-content:center;font-size:26px;flex-shrink:0;">{vi}</div><div><div style="color:{vc};font-size:20px;font-weight:700;margin-bottom:4px;">{vt}</div><div style="color:{TEXT_SUB};font-size:13px;">{r["category"]}</div></div></div>', bg=vbg, border=vbd)

    slabel("WHERE TO THROW IT")
    card(f'<div style="display:flex;align-items:center;gap:14px;"><div style="width:48px;height:48px;border-radius:12px;background:{bc};display:flex;align-items:center;justify-content:center;font-size:24px;flex-shrink:0;">{bi}</div><div><div style="color:{TEXT};font-weight:600;font-size:16px;">{r["bin"]} Bin</div><div style="color:{bc};font-size:12px;margin-top:2px;">Check your local bin colour</div></div></div>', border=f"{bc}40")

    slabel("💡 TIP")
    card(f'<div style="color:{TEXT_SUB};font-size:13px;line-height:1.7;">{r["tip"]}</div>')

    st.markdown(" ")
    if st.button("📷  Scan Another Item", use_container_width=True):
        st.session_state.uploaded_img=None; st.session_state.page="camera"; st.rerun()

def page_profile():
    logged_in = st.session_state.logged_in
    history   = st.session_state.history

    # Header
    sync      = f"<div style='color:{TEXT_MUT};font-size:12px;margin-top:2px;'>✅ Syncing across devices</div>" if logged_in else ""
    avatar_bg = "linear-gradient(135deg,#7ED957,#4CAF50)" if logged_in else CARD_BG
    avatar_ic = "👤" if logged_in else "👻"
    name      = "Gergely K." if logged_in else "Guest"
    h(f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;padding-bottom:16px;border-bottom:1px solid {HR};"><div><div style="color:{TEXT_MUT};font-family:Space Mono,monospace;font-size:11px;letter-spacing:2px;margin-bottom:4px;">PROFILE</div><div style="color:{TEXT};font-size:22px;font-weight:700;">{name}</div>{sync}</div><div style="width:52px;height:52px;border-radius:26px;font-size:24px;display:flex;align-items:center;justify-content:center;background:{avatar_bg};">{avatar_ic}</div></div>')

    # ── Theme toggle ──────────────────────────────────────────────────────────
    slabel("APPEARANCE")
    theme_label = "🌙 Switch to Light Mode" if dark else "☀️ Switch to Dark Mode"
    if st.button(theme_label, use_container_width=True):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

    st.markdown("---")

    # ── Stats ─────────────────────────────────────────────────────────────────
    total     = len(history)
    rec_count = sum(1 for h2 in history if h2["recyclable"])
    pct       = round(rec_count/total*100) if total else 0
    bin_counts: dict = {}
    for h2 in history:
        bin_counts[h2["bin"]] = bin_counts.get(h2["bin"],0)+1

    slabel("THIS MONTH")
    c1,c2 = st.columns(2)
    with c1: card(f'<div style="color:#7ED957;font-size:30px;font-weight:700;font-family:Space Mono,monospace;">{pct}%</div><div style="color:{TEXT_SUB};font-size:11px;margin-top:4px;">Recycled correctly</div>', bg="rgba(126,217,87,0.1)", border="rgba(126,217,87,0.2)")
    with c2: card(f'<div style="color:{TEXT};font-size:30px;font-weight:700;font-family:Space Mono,monospace;">{total}</div><div style="color:{TEXT_SUB};font-size:11px;margin-top:4px;">Items scanned</div>')

    h(f'<div style="margin-bottom:16px;"><div style="display:flex;justify-content:space-between;margin-bottom:6px;"><span style="color:{TEXT_SUB};font-size:12px;">Recycling rate</span><span style="color:#7ED957;font-size:12px;font-family:Space Mono,monospace;">{rec_count}/{total}</span></div><div style="height:8px;background:{CARD_BG};border-radius:4px;border:1px solid {CARD_BD};"><div style="width:{pct}%;height:8px;background:linear-gradient(90deg,#7ED957,#4CAF50);border-radius:4px;"></div></div></div>')

    slabel("BY BIN")
    for bn, cnt in bin_counts.items():
        col = BIN_COLORS.get(bn,"#888")
        bw  = int((cnt/total)*120) if total else 0
        h(f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;"><div style="width:10px;height:10px;border-radius:5px;background:{col};flex-shrink:0;"></div><div style="color:{TEXT_SUB};font-size:12px;flex:1;">{bn}</div><div style="color:{TEXT};font-size:12px;font-family:Space Mono,monospace;">{cnt}</div><div style="height:4px;width:{bw}px;background:{col};border-radius:2px;opacity:0.7;"></div></div>')

    st.markdown("---")
    slabel("RECENT SCANS")
    for entry in history[:10]:
        col  = BIN_COLORS.get(entry["bin"],"#888")
        icon = "♻️" if entry["recyclable"] else "🚫"
        rbg  = "rgba(126,217,87,0.12)" if entry["recyclable"] else "rgba(255,80,80,0.12)"
        h(f'<div style="display:flex;align-items:center;gap:12px;padding:12px 0;border-bottom:1px solid {HR};"><div style="width:36px;height:36px;border-radius:10px;background:{rbg};display:flex;align-items:center;justify-content:center;font-size:16px;flex-shrink:0;">{icon}</div><div style="flex:1;min-width:0;"><div style="color:{TEXT};font-size:13px;font-weight:500;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{entry["item"]}</div><div style="color:{TEXT_MUT};font-size:11px;">{entry["date"]}</div></div><div style="padding:3px 10px;border-radius:6px;background:{col}20;border:1px solid {col}40;color:{col};font-size:10px;font-family:Space Mono,monospace;white-space:nowrap;">{entry["bin"]}</div></div>')

    st.markdown(" ")

    # ── Sign in / out ─────────────────────────────────────────────────────────
    if logged_in:
        if st.button("Sign Out", use_container_width=True):
            st.session_state.logged_in   = False
            st.session_state.history     = []
            st.session_state.result      = None
            st.session_state.uploaded_img= None
            st.rerun()
        h(f'<div style="text-align:center;color:{TEXT_MUT};font-size:11px;margin-top:6px;">Signed in as gergely@student.buas.nl</div>')
    else:
        slabel("ACCOUNT")
        email    = st.text_input("Email",    placeholder="you@example.com", label_visibility="collapsed")
        password = st.text_input("Password", placeholder="Password",        label_visibility="collapsed", type="password")
        if st.button("Sign In / Create Account", use_container_width=True, type="primary"):
            if email and password:
                st.session_state.logged_in = True
                st.session_state.history   = list(DEMO_HISTORY)
                st.success("Signed in!")
                time.sleep(0.6)
                st.rerun()
            else:
                st.warning("Please enter your email and password.")

nav_bar()
st.markdown("---")
if   st.session_state.page == "camera":  page_camera()
elif st.session_state.page == "result":  page_result()
elif st.session_state.page == "profile": page_profile()
