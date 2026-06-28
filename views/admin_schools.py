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
    st.markdown("<h2 style='color:#01696f'>🏫 Manage Schools</h2>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["📋 All Schools", "➕ Add School"])

    with tab1:
        schools = db.table("schools").select("*").order("created_at", desc=True).execute()
        if schools.data:
            for s in schools.data:
                with st.expander(f"🏫 {s['name']} — ID: `{s['school_id']}` {'✅' if s['is_active'] else '❌'}"):
                    col1, col2 = st.columns(2)
                    col1.text_input("School Name", value=s["name"], key=f"sn_{s['id']}")
                    col1.text_input("Address", value=s.get("address",""), key=f"sa_{s['id']}")
                    col2.text_input("Phone", value=s.get("phone",""), key=f"sp_{s['id']}")
                    col2.text_input("Email", value=s.get("email",""), key=f"se_{s['id']}")
                    col_upd, col_del = st.columns(2)
                    if col_upd.button("💾 Update", key=f"upd_s_{s['id']}"):
                        db.table("schools").update({
                            "name": st.session_state[f"sn_{s['id']}"],
                            "address": st.session_state[f"sa_{s['id']}"],
                            "phone": st.session_state[f"sp_{s['id']}"],
                            "email": st.session_state[f"se_{s['id']}"],
                        }).eq("id", s["id"]).execute()
                        st.success("Updated!"); st.rerun()
                    if col_del.button("🗑️ Deactivate", key=f"del_s_{s['id']}"):
                        db.table("schools").update({"is_active": False}).eq("id", s["id"]).execute()
                        st.warning("Deactivated!"); st.rerun()
        else:
            st.info("No schools registered yet.")

    with tab2:
        with st.form("add_school_form"):
            school_id = st.text_input("School ID (unique)", placeholder="SCH001")
            name = st.text_input("School Name")
            address = st.text_area("Address", height=80)
            phone = st.text_input("Phone")
            email = st.text_input("Email")
            if st.form_submit_button("➕ Add School", width="stretch"):
                if not school_id or not name:
                    st.error("School ID and Name are required.")
                else:
                    try:
                        db.table("schools").insert({"school_id": school_id.strip(), "name": name.strip(), "address": address, "phone": phone, "email": email}).execute()
                        st.success(f"School '{name}' added!"); st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
