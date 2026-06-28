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
    st.markdown("<h2 style='color:#01696f'>⬆️ Promote Students</h2>", unsafe_allow_html=True)
    st.info("Promote an entire class or individual students to a new class. Their face data and student ID are preserved — no re-registration needed.")

    schools = db.table("schools").select("id,name,school_id").eq("is_active", True).execute()
    school_map = {f"{s['name']} ({s['school_id']})": s for s in (schools.data or [])}
    if not school_map:
        st.warning("Add a school first."); return

    school_sel = st.selectbox("School", list(school_map.keys()))
    school_id = school_map[school_sel]["id"]

    classes = db.table("classes").select("*").eq("school_id", school_id).eq("is_active", True).execute()
    class_map = {f"{c['class_name']} - {c.get('section','')} ({c.get('academic_year','')})": c for c in (classes.data or [])}
    if not class_map:
        st.warning("No classes found."); return

    tab1, tab2 = st.tabs(["⬆️ Promote Whole Class", "👤 Promote Individual Student"])

    with tab1:
        st.markdown("#### Promote All Students from One Class to Another")
        col1, col2 = st.columns(2)
        from_label = col1.selectbox("From Class", list(class_map.keys()), key="promo_from")
        to_label = col2.selectbox("To Class", list(class_map.keys()), key="promo_to")
        from_class = class_map[from_label]
        to_class = class_map[to_label]

        if from_class["id"] == to_class["id"]:
            st.warning("Source and destination class cannot be the same.")
        else:
            students_in_class = db.table("students").select("id,name,roll_number").eq("class_id", from_class["id"]).eq("is_active", True).execute()
            stu_count = len(students_in_class.data or [])
            st.markdown(f"**{stu_count} students** will be moved from **{from_label}** → **{to_label}**")

            if stu_count > 0:
                if st.button(f"⬆️ Promote {stu_count} Students", type="primary", width="stretch", key="promo_class_btn"):
                    for s in students_in_class.data:
                        db.table("students").update({"class_id": to_class["id"]}).eq("id", s["id"]).execute()
                    st.success(f"✅ {stu_count} students promoted from {from_label} to {to_label}!")
                    st.balloons()
            else:
                st.info("No students in source class.")

    with tab2:
        st.markdown("#### Move Individual Student to Another Class")
        from_cls_label = st.selectbox("Current Class", list(class_map.keys()), key="ind_promo_from")
        from_cls = class_map[from_cls_label]
        students_cls = db.table("students").select("id,name,roll_number").eq("class_id", from_cls["id"]).eq("is_active", True).execute()
        stu_opts = {f"{s['name']} (Roll: {s.get('roll_number','')})": s for s in (students_cls.data or [])}
        if not stu_opts:
            st.info("No students in this class.")
        else:
            stu_sel = st.selectbox("Select Student", list(stu_opts.keys()), key="ind_promo_stu")
            stu = stu_opts[stu_sel]
            to_cls_label = st.selectbox("Move to Class", [l for l in class_map.keys() if l != from_cls_label], key="ind_promo_to")
            to_cls = class_map[to_cls_label]
            if st.button(f"⬆️ Move {stu['name']} to {to_cls_label}", width="stretch", key="ind_promo_btn"):
                db.table("students").update({"class_id": to_cls["id"]}).eq("id", stu["id"]).execute()
                st.success(f"✅ {stu['name']} moved to {to_cls_label}! Face data preserved.")
