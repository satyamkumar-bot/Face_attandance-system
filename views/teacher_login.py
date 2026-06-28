import streamlit as st
from utils.auth import verify_teacher_login

def show():
    # Back button
    if st.button("← Back to Home", key="tl_back"):
        st.session_state["page"] = "home"; st.rerun()

    st.markdown("""
    <div style="text-align:center;padding:28px 0 20px">
        <div style="font-size:52px">👩‍🏫</div>
        <h2 style="color:#01696f;margin:8px 0 4px;font-size:clamp(1.4rem,4vw,1.8rem)">Teacher Login</h2>
        <p style="color:#7a7974;font-size:14px;margin:0">Sign in with your school credentials</p>
    </div>
    """, unsafe_allow_html=True)

    col_l, col_m, col_r = st.columns([1, 2, 1])
    with col_m:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        with st.form("teacher_login_form", clear_on_submit=False):
            school_id = st.text_input("🏫 School ID", placeholder="e.g. SCH001")
            teacher_id = st.text_input("👤 Teacher ID", placeholder="e.g. TCH001")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
            st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
            submitted = st.form_submit_button("Login →", width="stretch", type="primary")
        st.markdown('</div>', unsafe_allow_html=True)

        if submitted:
            if not school_id.strip() or not teacher_id.strip() or not password:
                st.error("Please fill all fields.")
            else:
                with st.spinner("Verifying credentials..."):
                    result = verify_teacher_login(school_id.strip(), teacher_id.strip(), password)
                if result:
                    st.session_state["teacher_logged_in"] = True
                    st.session_state["teacher_data"] = result["teacher"]
                    st.session_state["school_data"] = result["school"]
                    st.session_state["page"] = "teacher_dashboard"
                    st.rerun()
                else:
                    st.error("❌ Invalid School ID, Teacher ID, or Password.")

        st.markdown("""
        <p style="text-align:center;color:#9a9994;font-size:12px;margin-top:16px">
            Contact your school admin if you forgot your credentials.
        </p>
        """, unsafe_allow_html=True)
