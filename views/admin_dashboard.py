import streamlit as st
from views._sidebar import admin_sidebar
from utils.db import get_db
import plotly.express as px
import pandas as pd

def require_admin():
    if not st.session_state.get("admin_logged_in"):
        st.session_state["page"] = "admin_login"; st.rerun()

def show():
    require_admin()
    admin_sidebar()
    db = get_db()

    st.markdown("<h2 style='color:#01696f;margin-bottom:4px'>🛡️ Admin Dashboard</h2>", unsafe_allow_html=True)
    st.markdown("Full system overview and quick actions.")
    st.markdown("---")

    schools  = db.table("schools").select("id", count="exact").eq("is_active", True).execute()
    students = db.table("students").select("id", count="exact").eq("is_active", True).execute()
    teachers = db.table("teachers").select("id", count="exact").eq("is_active", True).execute()
    classes  = db.table("classes").select("id", count="exact").eq("is_active", True).execute()
    att_total= db.table("attendance").select("id", count="exact").execute()

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("🏫 Schools",  schools.count  or 0)
    c2.metric("👨‍🎓 Students", students.count or 0)
    c3.metric("👩‍🏫 Teachers", teachers.count or 0)
    c4.metric("📚 Classes",  classes.count  or 0)
    c5.metric("📋 Records",  att_total.count or 0)

    st.markdown("---")
    st.subheader("⚡ Quick Actions")
    col1, col2, col3, col4 = st.columns(4)
    if col1.button("➕ Add School",   width="stretch"): st.session_state["page"] = "admin_schools";  st.rerun()
    if col2.button("➕ Add Student",  width="stretch"): st.session_state["page"] = "admin_students"; st.rerun()
    if col3.button("➕ Add Teacher",  width="stretch"): st.session_state["page"] = "admin_teachers"; st.rerun()
    if col4.button("➕ Add Class",    width="stretch"): st.session_state["page"] = "admin_classes";  st.rerun()

    st.markdown("---")
    st.subheader("🏫 Students per School")
    try:
        school_list = db.table("schools").select("id,name").eq("is_active", True).execute()
        if school_list.data:
            rows = []
            for s in school_list.data:
                cnt = db.table("students").select("id", count="exact").eq("school_id", s["id"]).eq("is_active", True).execute()
                rows.append({"School": s["name"], "Students": cnt.count or 0})
            df = pd.DataFrame(rows)
            if not df.empty:
                fig = px.bar(df, x="School", y="Students", color_discrete_sequence=["#01696f"])
                fig.update_layout(plot_bgcolor="white", paper_bgcolor="white", margin=dict(t=20,b=20))
                st.plotly_chart(fig, width="stretch")
    except Exception as e:
        st.info(f"Could not load chart: {e}")
