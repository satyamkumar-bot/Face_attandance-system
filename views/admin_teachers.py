import streamlit as st
from views._sidebar import admin_sidebar as _adm_sb
from utils.auth import admin_logout, hash_password
from utils.db import get_db

def require_admin():
    if not st.session_state.get("admin_logged_in"):
        st.session_state["page"] = "admin_login"; st.rerun()

def admin_sidebar():
    with st.sidebar:
        st.markdown("### 🛡️ Admin Panel")
        st.markdown("---")
        pages = [("🏠 Dashboard","admin_dashboard"),("🏫 Schools","admin_schools"),("📚 Classes","admin_classes"),("👨‍🎓 Students","admin_students"),("👩‍🏫 Teachers","admin_teachers"),("📊 Reports","admin_reports"),("⬆️ Promote Students","admin_promote")]
        for label, page in pages:
            if st.button(label, width="stretch", key=f"adm_nav_{page}"): st.session_state["page"] = page; st.rerun()
        st.markdown("---")
        if st.button("🚪 Logout", width="stretch"): admin_logout(); st.session_state["page"] = "home"; st.rerun()

def show():
    require_admin()
    admin_sidebar()
    db = get_db()
    st.markdown("<h2 style='color:#01696f'>👩‍🏫 Manage Teachers</h2>", unsafe_allow_html=True)

    schools = db.table("schools").select("id,name,school_id").eq("is_active", True).execute()
    school_map = {f"{s['name']} ({s['school_id']})": s for s in (schools.data or [])}
    if not school_map:
        st.warning("Add a school first."); return

    tab1, tab2 = st.tabs(["📋 All Teachers", "➕ Add Teacher"])

    with tab1:
        school_filter = st.selectbox("Filter by School", ["All"] + list(school_map.keys()), key="tch_filter")
        query = db.table("teachers").select("*, schools(name)").eq("is_active", True)
        if school_filter != "All":
            query = query.eq("school_id", school_map[school_filter]["id"])
        teachers = query.order("name").execute()
        if teachers.data:
            import pandas as pd
            rows = [{"Teacher ID": t["teacher_id"], "Name": t["name"], "School": t["schools"]["name"] if t["schools"] else "-", "Email": t.get("email",""), "Phone": t.get("phone","")} for t in teachers.data]
            st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)

            st.markdown("#### Edit Teacher")
            t_opts = {f"{t['name']} ({t['teacher_id']})": t for t in teachers.data}
            sel = st.selectbox("Select teacher", list(t_opts.keys()), key="tch_edit_sel")
            t = t_opts[sel]
            col1, col2 = st.columns(2)
            new_name = col1.text_input("Name", value=t["name"], key="edit_tch_name")
            new_email = col2.text_input("Email", value=t.get("email",""), key="edit_tch_email")
            new_phone = col1.text_input("Phone", value=t.get("phone",""), key="edit_tch_phone")
            new_pass = col2.text_input("New Password (leave blank to keep)", type="password", key="edit_tch_pass")
            col_u, col_d = st.columns(2)
            if col_u.button("💾 Update Teacher"):
                upd = {"name": new_name, "email": new_email, "phone": new_phone}
                if new_pass.strip():
                    upd["password_hash"] = hash_password(new_pass.strip())
                db.table("teachers").update(upd).eq("id", t["id"]).execute()
                st.success("Updated!"); st.rerun()
            if col_d.button("🗑️ Deactivate Teacher"):
                db.table("teachers").update({"is_active": False}).eq("id", t["id"]).execute()
                st.warning("Deactivated!"); st.rerun()
        else:
            st.info("No teachers found.")

    with tab2:
        with st.form("add_teacher_form"):
            school_sel = st.selectbox("School", list(school_map.keys()))
            teacher_id = st.text_input("Teacher ID (unique)", placeholder="TCH001")
            name = st.text_input("Full Name")
            email = st.text_input("Email")
            phone = st.text_input("Phone")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("➕ Add Teacher", width="stretch"):
                if not teacher_id or not name or not password:
                    st.error("Teacher ID, Name and Password are required.")
                else:
                    try:
                        db.table("teachers").insert({"school_id": school_map[school_sel]["id"], "teacher_id": teacher_id.strip(), "name": name.strip(), "email": email.strip(), "phone": phone.strip(), "password_hash": hash_password(password)}).execute()
                        st.success(f"Teacher '{name}' added!"); st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
