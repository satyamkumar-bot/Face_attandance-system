import streamlit as st
from views._sidebar import teacher_sidebar
from utils.db import get_db
from datetime import date, timedelta
import pandas as pd

def require_teacher():
    if not st.session_state.get("teacher_logged_in"):
        st.session_state["page"] = "teacher_login"; st.rerun()

def show():
    require_teacher()
    teacher_sidebar()
    teacher = st.session_state["teacher_data"]
    school  = st.session_state["school_data"]
    db = get_db()

    st.markdown(f"<h2 style='color:#01696f;margin-bottom:4px'>📋 Dashboard</h2>", unsafe_allow_html=True)
    st.markdown(f"Welcome back, **{teacher['name']}** — {school['name']} &nbsp;|&nbsp; {date.today().strftime('%A, %d %B %Y')}")
    st.markdown("---")

    classes = db.table("classes").select("*").eq("school_id", school["id"]).eq("is_active", True).execute()
    class_list = classes.data or []

    total_students = db.table("students").select("id", count="exact").eq("school_id", school["id"]).eq("is_active", True).execute()
    total_today    = db.table("attendance").select("id", count="exact").eq("school_id", school["id"]).eq("date", str(date.today())).eq("status", "present").execute()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🏫 Classes", len(class_list))
    c2.metric("👨‍🎓 Students", total_students.count or 0)
    c3.metric("✅ Present Today", total_today.count or 0)
    c4.metric("📅 Today", date.today().strftime("%d %b"))

    st.markdown("---")
    st.subheader("📸 Start Attendance")

    if class_list:
        class_options = {f"{c['class_name']} — {c.get('section','')} ({c.get('academic_year','')})": c for c in class_list}
        selected_label = st.selectbox("Select Class", list(class_options.keys()))
        if st.button("▶ Start Face Attendance", width="stretch", type="primary"):
            st.session_state["selected_class"] = class_options[selected_label]
            st.session_state["page"] = "take_attendance"
            st.rerun()
    else:
        st.info("No classes found. Ask Admin to add classes for your school.")

    st.markdown("---")
    st.subheader("🕐 Recent Activity (Last 7 Days)")
    week_ago = (date.today() - timedelta(days=7)).isoformat()
    recent = db.table("attendance") \
        .select("*, students(name,roll_number), classes(class_name,section)") \
        .eq("school_id", school["id"]) \
        .eq("teacher_id", teacher["id"]) \
        .gte("date", week_ago) \
        .order("created_at", desc=True).limit(30).execute()

    if recent.data:
        rows = [{
            "Date": r["date"],
            "Student": r["students"]["name"] if r["students"] else "-",
            "Roll": r["students"]["roll_number"] if r["students"] else "-",
            "Class": f"{r['classes']['class_name']} {r['classes'].get('section','')}" if r["classes"] else "-",
            "Status": r["status"].capitalize(),
            "By": r["marked_by"].capitalize(),
        } for r in recent.data]
        st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
    else:
        st.info("No attendance records in the last 7 days.")
