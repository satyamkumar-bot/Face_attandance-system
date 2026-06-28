import streamlit as st
from views._sidebar import admin_sidebar as _adm_sb
from utils.db import get_db
from utils.reports import df_to_excel_bytes, df_to_csv_bytes, generate_attendance_pdf
import pandas as pd
import plotly.express as px
from datetime import date, timedelta

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
    st.markdown("<h2 style='color:#01696f'>📊 Admin Reports</h2>", unsafe_allow_html=True)

    report_scope = st.radio("Report Scope", ["Overall", "School-wise", "Class-wise"], horizontal=True)

    col_d1, col_d2 = st.columns(2)
    start_date = col_d1.date_input("From Date", value=date.today() - timedelta(days=30))
    end_date = col_d2.date_input("To Date", value=date.today())

    school_id_filter = None
    class_id_filter = None

    if report_scope in ["School-wise", "Class-wise"]:
        schools = db.table("schools").select("id,name,school_id").eq("is_active", True).execute()
        school_map = {f"{s['name']} ({s['school_id']})": s for s in (schools.data or [])}
        if school_map:
            sch_sel = st.selectbox("School", list(school_map.keys()))
            school_id_filter = school_map[sch_sel]["id"]

    if report_scope == "Class-wise" and school_id_filter:
        classes = db.table("classes").select("*").eq("school_id", school_id_filter).eq("is_active", True).execute()
        class_map = {f"{c['class_name']} - {c.get('section','')}": c for c in (classes.data or [])}
        if class_map:
            cls_sel = st.selectbox("Class", list(class_map.keys()))
            class_id_filter = class_map[cls_sel]["id"]

    st.markdown("---")
    if st.button("📊 Generate Report", type="primary", width="stretch"):
        with st.spinner("Generating report..."):
            query = db.table("attendance").select("*, students(name,roll_number), classes(class_name,section), schools(name)") \
                .gte("date", str(start_date)).lte("date", str(end_date))
            if school_id_filter:
                query = query.eq("school_id", school_id_filter)
            if class_id_filter:
                query = query.eq("class_id", class_id_filter)
            att_raw = query.execute()

        att_data = att_raw.data or []
        if not att_data:
            st.info("No attendance records found for the selected criteria."); return

        rows = []
        for r in att_data:
            rows.append({
                "Date": r["date"],
                "School": r["schools"]["name"] if r.get("schools") else "-",
                "Class": f"{r['classes']['class_name']} {r['classes'].get('section','')}" if r.get("classes") else "-",
                "Roll": r["students"]["roll_number"] if r.get("students") else "-",
                "Student": r["students"]["name"] if r.get("students") else "-",
                "Status": r["status"].capitalize(),
            })
        df = pd.DataFrame(rows)
        df["Date"] = pd.to_datetime(df["Date"])

        # Summary stats
        total_records = len(df)
        total_present = len(df[df["Status"] == "Present"])
        attendance_pct = (total_present / total_records * 100) if total_records else 0
        unique_students = df["Student"].nunique()
        unique_days = df["Date"].nunique()

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("📋 Total Records", total_records)
        c2.metric("✅ Present", total_present)
        c3.metric("📈 Avg Attendance %", f"{attendance_pct:.1f}%")
        c4.metric("👨‍🎓 Unique Students", unique_students)

        tabs = st.tabs(["📅 Daily Trend", "🏫 School-wise", "👤 Student-wise", "⬇️ Download"])

        with tabs[0]:
            daily = df[df["Status"]=="Present"].groupby("Date").size().reset_index(name="Present")
            fig = px.area(daily, x="Date", y="Present", title="Daily Attendance Trend", color_discrete_sequence=["#01696f"])
            fig.update_layout(plot_bgcolor="white", paper_bgcolor="white")
            st.plotly_chart(fig, width="stretch")

        with tabs[1]:
            sch_grp = df.groupby(["School","Status"]).size().reset_index(name="Count")
            fig2 = px.bar(sch_grp, x="School", y="Count", color="Status", barmode="group",
                          title="Attendance by School",
                          color_discrete_map={"Present":"#01696f","Absent":"#a12c7b","Late":"#d19900"})
            fig2.update_layout(plot_bgcolor="white", paper_bgcolor="white")
            st.plotly_chart(fig2, width="stretch")

        with tabs[2]:
            total_days = df["Date"].nunique()
            stu_present = df[df["Status"]=="Present"].groupby(["Student","Roll"])["Date"].count().reset_index()
            stu_present.columns = ["Student","Roll","Days Present"]
            stu_present["Total Days"] = total_days
            stu_present["Att %"] = (stu_present["Days Present"] / total_days * 100).round(1)
            stu_present = stu_present.sort_values("Att %")
            st.dataframe(stu_present, width="stretch", hide_index=True)

        with tabs[3]:
            export_df = df.copy()
            export_df["Date"] = export_df["Date"].dt.strftime("%Y-%m-%d")
            col_dl1, col_dl2 = st.columns(2)
            col_dl1.download_button("📥 CSV", df_to_csv_bytes(export_df), "admin_report.csv", "text/csv", width="stretch")
            col_dl2.download_button("📥 Excel", df_to_excel_bytes(export_df, "Report"), "admin_report.xlsx", width="stretch")
