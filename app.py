import streamlit as st
from datetime import datetime
import random
import time

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SmartSort",
    page_icon="♻️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Data ───────────────────────────────────────────────────────────────────────
RECYCLABLE_MAP = {
    "Plastic Bottle":  {"bin": "Plastic",      "category": "Hard Plastic",     "recyclable": True,  "tip": "Rinse before recycling. Remove cap if possible."},
    "Glass Jar":       {"bin": "Glass",         "category": "Glass",            "recyclable": True,  "tip": "Remove lid and rinse. Labels are fine to leave on."},
    "Cardboard Box":   {"bin": "Paper",         "category": "Paper / Cardboard","recyclable": True,  "tip": "Flatten to save space. Remove tape if possible."},
    "Food Waste":      {"bin": "General Waste", "category": "Organic",          "recyclable": False, "tip": "Consider composting! Not suitable for recycling bins."},
    "Aluminium Can":   {"bin": "Metal",         "category": "Metal",            "recyclable": True,  "tip": "Rinse cans. Crush them to save space."},
    "Plastic Bag":     {"bin": "General Waste", "category": "Soft Plastic",     "recyclable": False, "tip": "Some supermarkets accept soft plastics. Never put in kerbside bins."},
}

BIN_COLORS = {
    "Plastic":      "#F5C518",
    "Paper":        "#2196F3",
    "Glass":        "#4CAF50",
    "Metal":        "#FF9800",
    "General Waste":"#9E9E9E",
}

BIN_ICONS = {
    "Plastic":      "🟡",
    "Paper":        "🔵",
    "Glass":        "🟢",
    "Metal":        "🟠",
    "General Waste":"⚫",
}

DEMO_HISTORY = [
    {"item": "Plastic Bottle", "date": "Today, 09:14",      "recyclable": True,  "bin": "Plastic"},
    {"item": "Cardboard Box",  "date": "Today, 08:52",      "recyclable": True,  "bin": "Paper"},
    {"item": "Food Waste",     "date": "Yesterday, 19:30",  "recyclable": False, "bin": "General Waste"},
    {"item": "Aluminium Can",  "date": "Yesterday, 13:11",  "recyclable": True,  "bin": "Metal"},
    {"item": "Glass Jar",      "date": "Mon, 10:05",        "recyclable": True,  "bin": "Glass"},
    {"item": "Plastic Bag",    "date": "Mon, 09:47",        "recyclable": False, "bin": "General Waste"},
]

# ── Session state defaults ─────────────────────────────────────────────────────
if "page"        not in st.session_state: st.session_state.page        = "camera"
if "result"      not in st.session_state: st.session_state.result      = None
if "logged_in"   not in st.session_state: st.session_state.logged_in   = True
if "history"     not in st.session_state: st.session_state.history     = list(DEMO_HISTORY)
if "uploaded_img"not in st.session_state: st.session_state.uploaded_img= None

# ── Global CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=Space+Mono:wght@400;700&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif !important;
    background-color: #0f0f0f !important;
    color: #ffffff;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }
[data-testid="stToolbar"] { display: none; }
[data-testid="stDecoration"] { display: none; }
[data-testid="stSidebar"] { display: none; }
.block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; max-width: 480px !important; }

/* Buttons */
.stButton > button {
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    border-radius: 14px !important;
    border: none !important;
    transition: all 0.2s ease !important;
    width: 100% !important;
}
.stButton > button:hover { transform: translateY(-1px); filter: brightness(1.1); }

/* File uploader */
[data-testid="stFileUploader"] {
    background: rgba(255,255,255,0.04) !important;
    border: 2px dashed rgba(126,217,87,0.3) !important;
    border-radius: 16px !important;
    padding: 8px !important;
}
[data-testid="stFileUploaderDropzone"] { background: transparent !important; }

/* Remove red underlines / default borders */
.stTextInput > div > div { border-color: rgba(255,255,255,0.1) !important; background: rgba(255,255,255,0.05) !important; }

/* Divider */
hr { border-color: rgba(255,255,255,0.07) !important; }
</style>
""", unsafe_allow_html=True)

# ── Helper: card HTML ──────────────────────────────────────────────────────────
def card(content: str, bg="rgba(255,255,255,0.04)", border="rgba(255,255,255,0.08)", radius=20, padding="20px"):
    return f"""
    <div style="background:{bg};border:1px solid {border};border-radius:{radius}px;padding:{padding};margin-bottom:12px;">
        {content}
    </div>"""

def label(text):
    return f'<div style="color:rgba(255,255,255,0.4);font-size:11px;font-family:Space Mono,monospace;letter-spacing:2px;margin-bottom:10px;">{text}</div>'

def nav_bar():
    """Bottom navigation bar with three tabs."""
    pages = [("← Result", "result"), ("📷 Camera", "camera"), ("Profile →", "profile")]
    cols = st.columns(3)
    for col, (title, key) in zip(cols, pages):
        active = st.session_state.page == key
        bg     = "#7ED957" if active else "rgba(255,255,255,0.07)"
        color  = "#000"    if active else "rgba(255,255,255,0.5)"
        with col:
            if st.button(title, key=f"nav_{key}",
                         help=f"Go to {key}",
                         use_container_width=True):
                st.session_state.page = key
                st.rerun()
    # Inline style override for active button colour via markdown
    st.markdown(f"""
    <style>
    [data-testid="stButton"] button {{ background: rgba(255,255,255,0.07); color: rgba(255,255,255,0.5); font-size:13px; padding:8px 4px; }}
    </style>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: CAMERA
# ══════════════════════════════════════════════════════════════════════════════
def page_camera():
    # Header
    st.markdown("""
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;">
        <div>
            <div style="color:#7ED957;font-family:'Space Mono',monospace;font-size:11px;letter-spacing:2px;">SMART SORT</div>
            <div style="font-size:24px;font-weight:700;color:#fff;">Classify Item</div>
        </div>
        <div style="font-size:28px;">♻️</div>
    </div>
    """, unsafe_allow_html=True)

    # Upload zone
    st.markdown(label("UPLOAD OR TAKE A PHOTO"), unsafe_allow_html=True)
    uploaded = st.file_uploader(
        "Drop an image here or click to browse",
        type=["jpg", "jpeg", "png", "webp"],
        label_visibility="collapsed",
    )

    if uploaded:
        st.session_state.uploaded_img = uploaded
        st.image(uploaded, use_container_width=True,
                 caption="",
                 output_format="auto")
        st.markdown('<div style="text-align:center;color:rgba(255,255,255,0.4);font-size:12px;margin-top:4px;margin-bottom:12px;">Image ready to classify</div>', unsafe_allow_html=True)

    else:
        # Placeholder viewfinder
        st.markdown("""
        <div style="
            background:linear-gradient(160deg,#0a120a,#111a0f);
            border:2px dashed rgba(126,217,87,0.25);
            border-radius:20px;
            height:220px;
            display:flex;
            flex-direction:column;
            align-items:center;
            justify-content:center;
            gap:12px;
            margin-bottom:12px;
        ">
            <div style="font-size:52px;opacity:0.6;">📷</div>
            <div style="color:rgba(255,255,255,0.35);font-size:13px;">Upload a photo to classify</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Classify button
    btn_disabled = uploaded is None
    if st.button("♻️  Classify Item", disabled=btn_disabled,
                 use_container_width=True, type="primary"):
        with st.spinner("Analysing…"):
            time.sleep(1.5)  # Simulated model inference delay

        # ── Simulated classification (swap this for your YOLO model) ──────────
        item_name = random.choice(list(RECYCLABLE_MAP.keys()))
        result = {"item": item_name, **RECYCLABLE_MAP[item_name]}
        st.session_state.result = result

        # Append to history
        st.session_state.history.insert(0, {
            "item": item_name,
            "date": datetime.now().strftime("Today, %H:%M"),
            "recyclable": result["recyclable"],
            "bin": result["bin"],
        })

        st.session_state.page = "result"
        st.rerun()

    if btn_disabled:
        st.markdown('<div style="text-align:center;color:rgba(255,255,255,0.3);font-size:12px;margin-top:6px;">Upload an image first</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(label("HOW IT WORKS"), unsafe_allow_html=True)
    st.markdown(card("""
        <div style="display:flex;gap:16px;align-items:flex-start;">
            <div style="font-size:22px;">1️⃣</div>
            <div><div style="color:#fff;font-weight:600;font-size:14px;">Upload a photo</div>
            <div style="color:rgba(255,255,255,0.5);font-size:12px;margin-top:2px;">Take a picture of any item you're unsure about</div></div>
        </div>"""), unsafe_allow_html=True)
    st.markdown(card("""
        <div style="display:flex;gap:16px;align-items:flex-start;">
            <div style="font-size:22px;">2️⃣</div>
            <div><div style="color:#fff;font-weight:600;font-size:14px;">AI classifies it</div>
            <div style="color:rgba(255,255,255,0.5);font-size:12px;margin-top:2px;">YOLOv8 identifies the material type instantly</div></div>
        </div>"""), unsafe_allow_html=True)
    st.markdown(card("""
        <div style="display:flex;gap:16px;align-items:flex-start;">
            <div style="font-size:22px;">3️⃣</div>
            <div><div style="color:#fff;font-weight:600;font-size:14px;">Get your answer</div>
            <div style="color:rgba(255,255,255,0.5);font-size:12px;margin-top:2px;">See which bin to use and recycling tips</div></div>
        </div>"""), unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: RESULT
# ══════════════════════════════════════════════════════════════════════════════
def page_result():
    if st.session_state.result is None:
        st.markdown("""
        <div style="text-align:center;padding:60px 20px;">
            <div style="font-size:52px;margin-bottom:16px;">📸</div>
            <div style="color:rgba(255,255,255,0.4);font-size:14px;line-height:1.8;">
                No result yet.<br>Go to the Camera tab and classify an item first.
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Go to Camera →", use_container_width=True):
            st.session_state.page = "camera"
            st.rerun()
        return

    r = st.session_state.result
    bin_color  = BIN_COLORS.get(r["bin"], "#7ED957")
    bin_icon   = BIN_ICONS.get(r["bin"], "🗑️")
    is_rec     = r["recyclable"]
    verdict_bg = "rgba(126,217,87,0.12)" if is_rec else "rgba(255,80,80,0.12)"
    verdict_border = "rgba(126,217,87,0.3)" if is_rec else "rgba(255,80,80,0.3)"
    verdict_color  = "#7ED957" if is_rec else "#FF5050"
    verdict_icon   = "♻️" if is_rec else "🚫"
    verdict_text   = "Recyclable!" if is_rec else "Not Recyclable"

    # Header
    st.markdown(f"""
    <div style="margin-bottom:20px;">
        <div style="color:rgba(255,255,255,0.4);font-family:'Space Mono',monospace;font-size:11px;letter-spacing:2px;margin-bottom:6px;">CLASSIFICATION RESULT</div>
        <div style="font-size:24px;font-weight:700;color:#fff;">{r['item']}</div>
        <div style="color:rgba(255,255,255,0.4);font-size:13px;">{r['category']}</div>
    </div>
    """, unsafe_allow_html=True)

    # Show uploaded image if available
    if st.session_state.uploaded_img:
        st.image(st.session_state.uploaded_img, use_container_width=True)
        st.markdown("<div style='margin-bottom:12px;'></div>", unsafe_allow_html=True)

    # Verdict card
    st.markdown(card(f"""
        <div style="display:flex;align-items:center;gap:18px;">
            <div style="width:56px;height:56px;border-radius:28px;background:{verdict_color};display:flex;align-items:center;justify-content:center;font-size:26px;flex-shrink:0;">{verdict_icon}</div>
            <div>
                <div style="color:{verdict_color};font-size:20px;font-weight:700;margin-bottom:4px;">{verdict_text}</div>
                <div style="color:rgba(255,255,255,0.5);font-size:13px;">{r['category']}</div>
            </div>
        </div>
    """, bg=verdict_bg, border=verdict_border), unsafe_allow_html=True)

    # Bin instruction
    st.markdown(label("WHERE TO THROW IT"), unsafe_allow_html=True)
    st.markdown(card(f"""
        <div style="display:flex;align-items:center;gap:14px;">
            <div style="width:48px;height:48px;border-radius:12px;background:{bin_color};display:flex;align-items:center;justify-content:center;font-size:24px;flex-shrink:0;">{bin_icon}</div>
            <div>
                <div style="color:#fff;font-weight:600;font-size:16px;">{r['bin']} Bin</div>
                <div style="color:{bin_color};font-size:12px;margin-top:2px;">Tap to see bin locations nearby</div>
            </div>
        </div>
    """, border=f"{bin_color}30"), unsafe_allow_html=True)

    # Tip
    st.markdown(label("💡 TIP"), unsafe_allow_html=True)
    st.markdown(card(f"""
        <div style="color:rgba(255,255,255,0.75);font-size:13px;line-height:1.7;">{r['tip']}</div>
    """), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("📷  Scan Another Item", use_container_width=True):
        st.session_state.uploaded_img = None
        st.session_state.page = "camera"
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: PROFILE
# ══════════════════════════════════════════════════════════════════════════════
def page_profile():
    logged_in = st.session_state.logged_in
    history   = st.session_state.history

    # Header
    st.markdown(f"""
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;padding-bottom:16px;border-bottom:1px solid rgba(255,255,255,0.07);">
        <div>
            <div style="color:rgba(255,255,255,0.4);font-family:'Space Mono',monospace;font-size:11px;letter-spacing:2px;margin-bottom:4px;">PROFILE</div>
            <div style="color:#fff;font-size:22px;font-weight:700;">{"Gergely K." if logged_in else "Guest"}</div>
            {"<div style='color:rgba(255,255,255,0.4);font-size:12px;margin-top:2px;'>✅ Syncing across devices</div>" if logged_in else ""}
        </div>
        <div style="width:52px;height:52px;border-radius:26px;background:{'linear-gradient(135deg,#7ED957,#4CAF50)' if logged_in else 'rgba(255,255,255,0.1)'};display:flex;align-items:center;justify-content:center;font-size:24px;">
            {"👤" if logged_in else "👻"}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Stats ─────────────────────────────────────────────────────────────────
    total     = len(history)
    rec_count = sum(1 for h in history if h["recyclable"])
    non_rec   = total - rec_count
    pct       = round(rec_count / total * 100) if total else 0

    bin_counts: dict = {}
    for h in history:
        bin_counts[h["bin"]] = bin_counts.get(h["bin"], 0) + 1

    st.markdown(label("THIS MONTH"), unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(card(f"""
            <div style="color:#7ED957;font-size:30px;font-weight:700;font-family:'Space Mono',monospace;">{pct}%</div>
            <div style="color:rgba(255,255,255,0.5);font-size:11px;margin-top:4px;">Recycled correctly</div>
        """, bg="rgba(126,217,87,0.1)", border="rgba(126,217,87,0.2)"), unsafe_allow_html=True)
    with col2:
        st.markdown(card(f"""
            <div style="color:#fff;font-size:30px;font-weight:700;font-family:'Space Mono',monospace;">{total}</div>
            <div style="color:rgba(255,255,255,0.5);font-size:11px;margin-top:4px;">Items scanned</div>
        """), unsafe_allow_html=True)

    # Progress bar
    bar_fill = f"width:{pct}%;height:8px;background:linear-gradient(90deg,#7ED957,#4CAF50);border-radius:4px;"
    st.markdown(f"""
    <div style="margin-bottom:16px;">
        <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
            <span style="color:rgba(255,255,255,0.5);font-size:12px;">Recycling rate</span>
            <span style="color:#7ED957;font-size:12px;font-family:'Space Mono',monospace;">{rec_count}/{total}</span>
        </div>
        <div style="height:8px;background:rgba(255,255,255,0.08);border-radius:4px;">
            <div style="{bar_fill}"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Per-bin breakdown
    st.markdown(label("BY BIN"), unsafe_allow_html=True)
    for bin_name, count in bin_counts.items():
        color   = BIN_COLORS.get(bin_name, "#fff")
        bar_w   = int((count / total) * 120) if total else 0
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
            <div style="width:10px;height:10px;border-radius:5px;background:{color};flex-shrink:0;"></div>
            <div style="color:rgba(255,255,255,0.6);font-size:12px;flex:1;">{bin_name}</div>
            <div style="color:#fff;font-size:12px;font-family:'Space Mono',monospace;">{count}</div>
            <div style="height:4px;width:{bar_w}px;background:{color};border-radius:2px;opacity:0.7;"></div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Recent scans ─────────────────────────────────────────────────────────
    st.markdown(label("RECENT SCANS"), unsafe_allow_html=True)

    for entry in history[:10]:
        color      = BIN_COLORS.get(entry["bin"], "#fff")
        rec_icon   = "♻️" if entry["recyclable"] else "🚫"
        rec_bg     = "rgba(126,217,87,0.12)" if entry["recyclable"] else "rgba(255,80,80,0.12)"
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:12px;padding:12px 0;border-bottom:1px solid rgba(255,255,255,0.05);">
            <div style="width:36px;height:36px;border-radius:10px;background:{rec_bg};display:flex;align-items:center;justify-content:center;font-size:16px;flex-shrink:0;">{rec_icon}</div>
            <div style="flex:1;min-width:0;">
                <div style="color:#fff;font-size:13px;font-weight:500;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{entry['item']}</div>
                <div style="color:rgba(255,255,255,0.35);font-size:11px;">{entry['date']}</div>
            </div>
            <div style="padding:3px 10px;border-radius:6px;background:{color}20;border:1px solid {color}40;color:{color};font-size:10px;font-family:'Space Mono',monospace;white-space:nowrap;">{entry['bin']}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Sign in / out ─────────────────────────────────────────────────────────
    if logged_in:
        if st.button("Sign Out", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()
        st.markdown('<div style="text-align:center;color:rgba(255,255,255,0.25);font-size:11px;margin-top:6px;">Signed in as gergely@student.buas.nl</div>', unsafe_allow_html=True)
    else:
        st.markdown(label("ACCOUNT"), unsafe_allow_html=True)
        email    = st.text_input("Email",    placeholder="you@example.com",  label_visibility="collapsed")
        password = st.text_input("Password", placeholder="Password", type="password", label_visibility="collapsed")
        if st.button("Sign In / Create Account", use_container_width=True, type="primary"):
            if email and password:
                st.session_state.logged_in = True
                st.success("Signed in!")
                time.sleep(0.8)
                st.rerun()
            else:
                st.warning("Please enter your email and password.")


# ══════════════════════════════════════════════════════════════════════════════
# Router
# ══════════════════════════════════════════════════════════════════════════════
nav_bar()
st.markdown("<hr style='margin:0 0 16px 0;'>", unsafe_allow_html=True)

if   st.session_state.page == "camera":  page_camera()
elif st.session_state.page == "result":  page_result()
elif st.session_state.page == "profile": page_profile()
