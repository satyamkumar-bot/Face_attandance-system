import streamlit as st
from utils.auth import teacher_logout, admin_logout

def teacher_sidebar():
    teacher = st.session_state.get("teacher_data", {})
    school = st.session_state.get("school_data", {})
    with st.sidebar:
        st.markdown(f"""
        <div style="padding:16px 8px 12px;border-bottom:1px solid rgba(255,255,255,0.15);margin-bottom:8px">
            <div style="font-size:22px;font-weight:700;color:#e8f4f4">🎓 FaceAttend</div>
            <div style="font-size:12px;color:#a8d4d4;margin-top:4px">{school.get('name','School')[:28]}</div>
        </div>
        <div style="padding:10px 8px;background:rgba(255,255,255,0.08);border-radius:8px;margin-bottom:12px">
            <div style="font-size:13px;font-weight:600;color:#e8f4f4">👩‍🏫 {teacher.get('name','Teacher')}</div>
            <div style="font-size:11px;color:#a8d4d4">ID: {teacher.get('teacher_id','')}</div>
        </div>
        """, unsafe_allow_html=True)

        nav_items = [
            ("📋 Dashboard", "teacher_dashboard"),
            ("📸 Take Attendance", "take_attendance"),
            ("📊 Reports", "teacher_reports"),
        ]
        current = st.session_state.get("page", "")
        for label, pg in nav_items:
            active = "background:rgba(255,255,255,0.22)!important;" if current == pg else ""
            if st.button(label, key=f"tnav_{pg}", width="stretch"):
                st.session_state["page"] = pg; st.rerun()

        st.markdown("<div style='flex:1'></div>", unsafe_allow_html=True)
        st.markdown("<div style='margin-top:20px'>", unsafe_allow_html=True)
        if st.button("🚪 Logout", key="teacher_logout_btn", width="stretch"):
            teacher_logout()
            st.session_state["page"] = "home"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

def admin_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="padding:16px 8px 12px;border-bottom:1px solid rgba(255,255,255,0.15);margin-bottom:8px">
            <div style="font-size:22px;font-weight:700;color:#e8f4f4">🛡️ Admin Panel</div>
            <div style="font-size:12px;color:#a8d4d4;margin-top:4px">Full system access</div>
        </div>
        """, unsafe_allow_html=True)

        nav_items = [
            ("🏠 Dashboard", "admin_dashboard"),
            ("🏫 Schools", "admin_schools"),
            ("📚 Classes", "admin_classes"),
            ("👨‍🎓 Students", "admin_students"),
            ("👩‍🏫 Teachers", "admin_teachers"),
            ("📊 Reports", "admin_reports"),
            ("⬆️ Promote Students", "admin_promote"),
        ]
        current = st.session_state.get("page", "")
        for label, pg in nav_items:
            if st.button(label, key=f"anav_{pg}", width="stretch"):
                st.session_state["page"] = pg; st.rerun()

        st.markdown("<div style='margin-top:20px'>", unsafe_allow_html=True)
        if st.button("🚪 Logout", key="admin_logout_btn", width="stretch"):
            admin_logout()
            st.session_state["page"] = "home"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
