import streamlit as st
from views._sidebar import teacher_sidebar
from utils.db import get_db
from utils.reports import df_to_excel_bytes, df_to_csv_bytes, generate_attendance_pdf
import pandas as pd
import plotly.express as px
from datetime import date, timedelta

def require_teacher():
    if not st.session_state.get("teacher_logged_in"):
        st.session_state["page"] = "teacher_login"; st.rerun()

def teacher_sidebar():
    teacher = st.session_state.get("teacher_data", {})
    school = st.session_state.get("school_data", {})
    with st.sidebar:
        st.markdown(f"### 🎓 {school.get('name','FaceAttend')[:22]}")
        st.markdown(f"👩‍🏫 **{teacher.get('name','Teacher')}**")
        st.markdown("---")
        if st.button("📋 Dashboard", width="stretch"): st.session_state["page"] = "teacher_dashboard"; st.rerun()
        if st.button("📸 Take Attendance", width="stretch"): st.session_state["page"] = "take_attendance"; st.rerun()
        if st.button("📊 Reports", width="stretch"): st.session_state["page"] = "teacher_reports"; st.rerun()
        st.markdown("---")
        if st.button("🚪 Logout", width="stretch"):
            teacher_logout(); st.session_state["page"] = "home"; st.rerun()

def show():
    require_teacher()
    teacher_sidebar()
    teacher = st.session_state["teacher_data"]
    school = st.session_state["school_data"]
    db = get_db()

    st.markdown("<h2 style='color:#01696f'>📊 Attendance Reports</h2>", unsafe_allow_html=True)

    classes = db.table("classes").select("*").eq("school_id", school["id"]).eq("is_active", True).execute()
    class_list = classes.data or []
    if not class_list:
        st.warning("No classes found."); return

    class_options = {f"{c['class_name']} - {c.get('section','')}": c for c in class_list}
    selected_label = st.selectbox("📚 Select Class", list(class_options.keys()))
    selected_class = class_options[selected_label]

    col_d1, col_d2 = st.columns(2)
    start_date = col_d1.date_input("📅 From Date", value=date.today() - timedelta(days=30))
    end_date = col_d2.date_input("📅 To Date", value=date.today())

    st.markdown("---")

 
    att_raw = db.table("attendance").select("*, students(id,name,roll_number)") \
        .eq("class_id", selected_class["id"]).gte("date", str(start_date)).lte("date", str(end_date)).execute()
    att_data = att_raw.data or []

    if not att_data:
        st.info("No attendance records for this class in the selected date range."); return

 
    rows = []
    for r in att_data:
        rows.append({
            "date": r["date"],
            "student_id": r["student_id"],
            "name": r["students"]["name"] if r["students"] else "Unknown",
            "roll": r["students"]["roll_number"] if r["students"] else "-",
            "status": r["status"],
        })
    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"])

    # Summary stats
    total_days = df["date"].nunique()
    total_students = df["student_id"].nunique()
    present_df = df[df["status"] == "present"]
    avg_present = present_df.groupby("date")["student_id"].count().mean() if not present_df.empty else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("📅 Total Days", total_days)
    col2.metric("👨‍🎓 Total Students", total_students)
    col3.metric("📈 Avg Present/Day", f"{avg_present:.1f}")

    tabs = st.tabs(["📅 Day-wise", "👤 Student-wise", "📈 Charts", "⬇️ Download"])

    with tabs[0]:
        st.subheader("Day-wise Attendance")
        day_df = df.groupby(["date","status"]).size().reset_index(name="count")
        day_pivot = day_df.pivot_table(index="date", columns="status", values="count", fill_value=0).reset_index()
        day_pivot["date"] = day_pivot["date"].dt.strftime("%d %b %Y")
        st.dataframe(day_pivot, width="stretch", hide_index=True)

    with tabs[1]:
        st.subheader("Student-wise Attendance Summary")
        stu_present = df[df["status"] == "present"].groupby(["student_id","name","roll"])["date"].count().reset_index()
        stu_present.columns = ["student_id","name","roll","days_present"]
        stu_present["total_days"] = total_days
        stu_present["attendance_%"] = (stu_present["days_present"] / total_days * 100).round(1)
        stu_present = stu_present.sort_values("roll")
        st.dataframe(stu_present[["roll","name","days_present","total_days","attendance_%"]], width="stretch", hide_index=True)

        low_att = stu_present[stu_present["attendance_%"] < 75]
        if not low_att.empty:
            st.warning(f"⚠️ {len(low_att)} student(s) with attendance below 75%:")
            st.dataframe(low_att[["roll","name","attendance_%"]], width="stretch", hide_index=True)

    with tabs[2]:
        st.subheader("Attendance Trend")
        daily_count = df[df["status"]=="present"].groupby("date")["student_id"].count().reset_index()
        daily_count.columns = ["date","present_count"]
        fig = px.line(daily_count, x="date", y="present_count", title="Daily Present Count",
                      color_discrete_sequence=["#01696f"])
        fig.update_layout(plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig, width="stretch")

        if not stu_present.empty:
            fig2 = px.histogram(stu_present, x="attendance_%", nbins=10,
                                title="Student Attendance Distribution (%)",
                                color_discrete_sequence=["#01696f"])
            fig2.update_layout(plot_bgcolor="white", paper_bgcolor="white")
            st.plotly_chart(fig2, width="stretch")

    with tabs[3]:
        st.subheader("⬇️ Download Reports")
        export_df = df.copy()
        export_df["date"] = export_df["date"].dt.strftime("%Y-%m-%d")
        export_df = export_df[["date","roll","name","status"]].sort_values(["date","roll"])

        col_dl1, col_dl2, col_dl3 = st.columns(3)
        col_dl1.download_button("📥 Download CSV", df_to_csv_bytes(export_df), "attendance_report.csv", "text/csv", width="stretch")
        col_dl2.download_button("📥 Download Excel", df_to_excel_bytes(export_df, "Attendance"), "attendance_report.xlsx", width="stretch")
        try:
            pdf_bytes = generate_attendance_pdf(export_df.head(100), f"Attendance Report - {selected_label}", school["name"])
            col_dl3.download_button("📥 Download PDF", pdf_bytes, "attendance_report.pdf", "application/pdf", width="stretch")
        except Exception as e:
            col_dl3.info(f"PDF: {e}")
