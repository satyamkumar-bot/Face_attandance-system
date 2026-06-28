import streamlit as st
from utils.auth import verify_admin_login

def show():
    if st.button("← Back to Home", key="al_back"):
        st.session_state["page"] = "home"; st.rerun()

    st.markdown("""
    <div style="text-align:center;padding:28px 0 20px">
        <div style="font-size:52px">🛡️</div>
        <h2 style="color:#01696f;margin:8px 0 4px;font-size:clamp(1.4rem,4vw,1.8rem)">Admin Login</h2>
        <p style="color:#7a7974;font-size:14px;margin:0">Full system access for administrators</p>
    </div>
    """, unsafe_allow_html=True)

    col_l, col_m, col_r = st.columns([1, 2, 1])
    with col_m:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        with st.form("admin_login_form", clear_on_submit=False):
            username = st.text_input("👤 Username", placeholder="admin")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter admin password")
            st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
            submitted = st.form_submit_button("Login as Admin →", width="stretch", type="primary")
        st.markdown('</div>', unsafe_allow_html=True)

        if submitted:
            if not username.strip() or not password:
                st.error("Please fill all fields.")
            else:
                with st.spinner("Authenticating..."):
                    ok = verify_admin_login(username.strip(), password)
                if ok:
                    st.session_state["admin_logged_in"] = True
                    st.session_state["page"] = "admin_dashboard"
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password.")

        st.markdown("""
        <div style="background:#fff8e8;border:1px solid #e9e0c6;border-radius:8px;padding:12px 14px;margin-top:16px">
            <p style="color:#7a5c00;font-size:12px;margin:0">
                🔑 Default credentials: <code>admin</code> / <code>admin@123</code><br>
                Change these after first login in Supabase → admins table.
            </p>
        </div>
        """, unsafe_allow_html=True)
