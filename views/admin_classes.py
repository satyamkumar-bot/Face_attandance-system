import streamlit as st
from views._sidebar import admin_sidebar as _adm_sb
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
    st.markdown("<h2 style='color:#01696f'>📚 Manage Classes</h2>", unsafe_allow_html=True)

    schools = db.table("schools").select("id,name,school_id").eq("is_active", True).execute()
    school_map = {f"{s['name']} ({s['school_id']})": s for s in (schools.data or [])}
    if not school_map:
        st.warning("Add a school first."); return

    tab1, tab2 = st.tabs(["📋 All Classes", "➕ Add Class"])
    with tab1:
        selected_school_label = st.selectbox("Filter by School", ["All"] + list(school_map.keys()))
        query = db.table("classes").select("*, schools(name)").eq("is_active", True)
        if selected_school_label != "All":
            query = query.eq("school_id", school_map[selected_school_label]["id"])
        classes = query.order("class_name").execute()
        if classes.data:
            import pandas as pd
            rows = [{"ID": c["id"][:8], "School": c["schools"]["name"] if c["schools"] else "-", "Class": c["class_name"], "Section": c.get("section",""), "Year": c.get("academic_year","")} for c in classes.data]
            df = pd.DataFrame(rows)
            st.dataframe(df, width="stretch", hide_index=True)

            st.markdown("#### Edit / Delete")
            class_opts = {f"{c['class_name']} - {c.get('section','')} ({c.get('academic_year','')})": c for c in classes.data}
            sel = st.selectbox("Select class to edit", list(class_opts.keys()), key="cls_edit_sel")
            cls = class_opts[sel]
            col1, col2, col3 = st.columns(3)
            new_name = col1.text_input("Class Name", value=cls["class_name"], key="edit_cls_name")
            new_sec = col2.text_input("Section", value=cls.get("section",""), key="edit_cls_sec")
            new_yr = col3.text_input("Academic Year", value=cls.get("academic_year",""), key="edit_cls_yr")
            col_u, col_d = st.columns(2)
            if col_u.button("💾 Update Class"):
                db.table("classes").update({"class_name": new_name, "section": new_sec, "academic_year": new_yr}).eq("id", cls["id"]).execute()
                st.success("Updated!"); st.rerun()
            if col_d.button("🗑️ Delete Class"):
                db.table("classes").update({"is_active": False}).eq("id", cls["id"]).execute()
                st.warning("Deleted!"); st.rerun()
        else:
            st.info("No classes found.")

    with tab2:
        with st.form("add_class_form"):
            school_sel = st.selectbox("School", list(school_map.keys()))
            class_name = st.text_input("Class Name", placeholder="Class 6, Grade 10, etc.")
            section = st.text_input("Section", placeholder="A, B, Science, Arts...")
            academic_year = st.text_input("Academic Year", placeholder="2025-26")
            if st.form_submit_button("➕ Add Class", width="stretch"):
                if not class_name:
                    st.error("Class Name is required.")
                else:
                    try:
                        db.table("classes").insert({"school_id": school_map[school_sel]["id"], "class_name": class_name.strip(), "section": section.strip(), "academic_year": academic_year.strip()}).execute()
                        st.success("Class added!"); st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
