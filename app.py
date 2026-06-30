import streamlit as st
import sys
import asyncio

st.set_page_config(
    page_title="FaceAttend",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)


st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Base ── */
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

/* ── Hide Streamlit default sidebar nav items (MPA pages list) ── */
[data-testid="stSidebarNav"] { display: none !important; }

/* ── Hide sidebar entirely on login/home screens ── */
.hide-sidebar [data-testid="stSidebar"] { display: none !important; }
.hide-sidebar [data-testid="collapsedControl"] { display: none !important; }

/* ── Sidebar styling ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0a2e30 0%, #01696f 100%) !important;
    min-width: 230px !important;
    max-width: 260px !important;
}
[data-testid="stSidebar"] * { color: #e8f4f4 !important; }
[data-testid="stSidebar"] .stButton > button {
    background: rgba(255,255,255,0.08) !important;
    color: #e8f4f4 !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 8px !important;
    text-align: left !important;
    font-size: 14px !important;
    padding: 10px 14px !important;
    margin-bottom: 2px !important;
    width: 100% !important;
    transition: background 0.2s !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,255,255,0.18) !important;
}

/* ── Main content ── */
.block-container { padding: 1.5rem 1.5rem 3rem !important; max-width: 1100px !important; }

/* ── Metric cards ── */
[data-testid="metric-container"] {
    background: #f0f9f9;
    border: 1px solid #cedcd8;
    border-radius: 12px;
    padding: 14px 16px;
    box-shadow: 0 2px 8px rgba(1,105,111,0.07);
}
[data-testid="metric-container"] label { color: #01696f !important; font-weight: 600 !important; font-size: 13px !important; }
[data-testid="metric-container"] [data-testid="stMetricValue"] { font-size: 1.8rem !important; font-weight: 700 !important; color: #0a2e30 !important; }

/* ── Primary buttons ── */
.stButton > button {
    background: #01696f !important;
    color: white !important;
    border: none !important;
    border-radius: 9px !important;
    font-weight: 500 !important;
    font-size: 14px !important;
    padding: 10px 20px !important;
    transition: background 0.2s, transform 0.1s !important;
}
.stButton > button:hover { background: #0c4e54 !important; transform: translateY(-1px) !important; }
.stButton > button:active { transform: translateY(0) !important; }

/* ── Form inputs ── */
.stTextInput > div > div > input, .stSelectbox > div > div {
    border-radius: 8px !important;
    border: 1.5px solid #d4d1ca !important;
    font-size: 14px !important;
    transition: border-color 0.2s !important;
}
.stTextInput > div > div > input:focus { border-color: #01696f !important; box-shadow: 0 0 0 3px rgba(1,105,111,0.12) !important; }

/* ── Login card ── */
.login-card {
    background: white;
    border-radius: 18px;
    padding: 40px 36px;
    box-shadow: 0 8px 40px rgba(1,105,111,0.13);
    border: 1px solid #e8f4f4;
    max-width: 420px;
    margin: 0 auto;
}

/* ── Section cards ── */
.att-card {
    background: #f8fffe;
    border: 1px solid #cedcd8;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 12px;
    transition: box-shadow 0.2s;
}
.att-card:hover { box-shadow: 0 4px 16px rgba(1,105,111,0.10); }

/* ── Status badges ── */
.badge-present { background:#d4dfcc; color:#1e3f0a; border-radius:20px; padding:3px 12px; font-size:12px; font-weight:600; }
.badge-absent  { background:#e0ced7; color:#561740; border-radius:20px; padding:3px 12px; font-size:12px; font-weight:600; }
.badge-manual  { background:#e9e0c6; color:#7a5c00; border-radius:20px; padding:3px 12px; font-size:12px; font-weight:600; }

/* ── Home feature cards ── */
.feature-card {
    background: white;
    border: 1px solid #e0f0f0;
    border-radius: 16px;
    padding: 28px 22px;
    text-align: center;
    box-shadow: 0 2px 12px rgba(1,105,111,0.07);
    height: 100%;
    transition: transform 0.2s, box-shadow 0.2s;
}
.feature-card:hover { transform: translateY(-3px); box-shadow: 0 8px 28px rgba(1,105,111,0.13); }

/* ── Tables ── */
.dataframe thead th {
    background: #01696f !important;
    color: white !important;
    font-weight: 600 !important;
    font-size: 13px !important;
}
.dataframe tbody tr:nth-child(even) { background: #f5fcfc !important; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] { gap: 4px; background: #f0f9f9; border-radius: 10px; padding: 4px; }
.stTabs [data-baseweb="tab"] { border-radius: 8px !important; font-size: 13px !important; padding: 8px 16px !important; }
.stTabs [aria-selected="true"] { background: #01696f !important; color: white !important; }

/* ── Mobile responsive ── */
@media (max-width: 768px) {
    .block-container { padding: 1rem 0.75rem 2rem !important; }
    [data-testid="stSidebar"] { min-width: 200px !important; }
    .login-card { padding: 24px 18px !important; margin: 0 8px !important; }
    [data-testid="metric-container"] [data-testid="stMetricValue"] { font-size: 1.4rem !important; }
    .stButton > button { font-size: 15px !important; padding: 12px !important; }
}
@media (max-width: 480px) {
    .block-container { padding: 0.75rem 0.5rem 2rem !important; }
}

/* ── Dividers ── */
hr { border-color: #e0eeee !important; margin: 1rem 0 !important; }

/* ── Expander ── */
.streamlit-expanderHeader { font-weight: 500 !important; color: #01696f !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #f0f9f9; }
::-webkit-scrollbar-thumb { background: #01696f; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)


defaults = {
    "teacher_logged_in": False,
    "teacher_data": None,
    "school_data": None,
    "teacher_name_input": "",
    "admin_logged_in": False,
    "page": "home",
    "selected_class": None,
    "attendance_session": {},
    "liveness_passed": {},
    "blink_counts": {},
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


page = st.session_state["page"]
no_sidebar_pages = {"home", "teacher_login", "admin_login"}
if page in no_sidebar_pages:
    st.markdown('<style>[data-testid="stSidebar"]{display:none!important}[data-testid="collapsedControl"]{display:none!important}</style>', unsafe_allow_html=True)


def show_home():
    st.markdown("""
    <div style="text-align:center;padding:48px 20px 28px">
        <div style="font-size:72px;margin-bottom:8px">🎓</div>
        <h1 style="color:#01696f;font-size:clamp(1.8rem,5vw,2.6rem);margin:0 0 10px;font-weight:700">FaceAttend</h1>
        <p style="color:#5a7a7a;font-size:clamp(14px,2.5vw,18px);margin:0 auto;max-width:480px">
            AI-powered school attendance using face recognition.<br>Works on any device — mobile, tablet, or laptop.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Changed from 3 columns to 2 columns
    col1, col2 = st.columns(2, gap="medium") 
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div style="font-size:44px;margin-bottom:12px">👩‍🏫</div>
            <h3 style="color:#01696f;margin:0 0 8px;font-size:1.1rem">Teacher Portal</h3>
            <p style="color:#7a7974;font-size:13px;margin:0 0 16px;line-height:1.6">
                Mark attendance using your phone or laptop camera with live face recognition.
            </p>
        </div>""", unsafe_allow_html=True)
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        if st.button("Teacher Login →", key="btn_teacher", width="stretch"):
            st.session_state["page"] = "teacher_login"; st.rerun()

    with col2:
        st.markdown("""
        <div class="feature-card">
            <div style="font-size:44px;margin-bottom:12px">🛡️</div>
            <h3 style="color:#01696f;margin:0 0 8px;font-size:1.1rem">Admin Panel</h3>
            <p style="color:#7a7974;font-size:13px;margin:0 0 16px;line-height:1.6">
                Manage schools, classes, students and teachers. View all reports and promote students.
            </p>
        </div>""", unsafe_allow_html=True)
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        if st.button("Admin Login →", key="btn_admin", width="stretch"):
            st.session_state["page"] = "admin_login"; st.rerun()


if page == "home":
    show_home()
elif page == "teacher_login":
    from views.teacher_login import show; show()
elif page == "teacher_dashboard":
    from views.teacher_dashboard import show; show()
elif page == "take_attendance":
    from views.take_attendance import show; show()
elif page == "teacher_reports":
    from views.teacher_reports import show; show()
elif page == "admin_login":
    from views.admin_login import show; show()
elif page == "admin_dashboard":
    from views.admin_dashboard import show; show()
elif page == "admin_schools":
    from views.admin_schools import show; show()
elif page == "admin_students":
    from views.admin_students import show; show()
elif page == "admin_teachers":
    from views.admin_teachers import show; show()
elif page == "admin_classes":
    from views.admin_classes import show; show()
elif page == "admin_reports":
    from views.admin_reports import show; show()
elif page == "admin_promote":
    from views.admin_promote import show; show()
else:
    st.session_state["page"] = "home"; st.rerun()
