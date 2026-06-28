import streamlit as st
from utils.db import get_db
from utils.face_utils import encode_face
import numpy as np
from PIL import Image
import pandas as pd
import traceback
from views._sidebar import admin_sidebar


def require_admin():
    if not st.session_state.get("admin_logged_in"):
        st.session_state["page"] = "admin_login"
        st.rerun()


def read_uploaded_image(uploaded_file):
    if uploaded_file is None:
        return None
    try:
        file_bytes = uploaded_file.getvalue()
        if not file_bytes:
            return None
        img = Image.open(uploaded_file).convert("RGB")
        return np.array(img)
    except Exception:
        return None


def safe_encode_from_uploaded(uploaded_file):
    img_np = read_uploaded_image(uploaded_file)
    if img_np is None:
        return None, "Could not read image."
    try:
        enc = encode_face(img_np)
        if enc is None:
            return None, "No clear single face detected. Please use a frontal, well-lit image."
        return enc, None
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"


def show():
    require_admin()
    admin_sidebar()
    db = get_db()

    st.markdown("<h2 style='color:#01696f'>👨‍🎓 Manage Students</h2>", unsafe_allow_html=True)

    schools = db.table("schools").select("id,name,school_id").eq("is_active", True).order("name").execute()
    school_map = {f"{s['name']} ({s['school_id']})": s for s in (schools.data or [])}

    if not school_map:
        st.warning("Add a school first.")
        return

    tab1, tab2, tab3 = st.tabs([
        "📋 View Students",
        "➕ Add Student",
        "🧠 Register Face"
    ])

    # -------------------------------------------------
    # TAB 1 - VIEW / EDIT / REMOVE STUDENTS
    # -------------------------------------------------
    with tab1:
        school_filter = st.selectbox("School", list(school_map.keys()), key="stu_filter_sch")
        school_id = school_map[school_filter]["id"]

        classes = db.table("classes").select("*").eq("school_id", school_id).eq("is_active", True).order("class_name").execute()
        class_map = {"All Classes": None}
        class_map.update({f"{c['class_name']} - {c.get('section', '')}": c for c in (classes.data or [])})

        class_filter = st.selectbox("Class", list(class_map.keys()), key="stu_filter_cls")
        selected_class = class_map[class_filter]

        query = db.table("students").select("*, classes(class_name,section)").eq("school_id", school_id).eq("is_active", True)
        if selected_class:
            query = query.eq("class_id", selected_class["id"])

        students = query.order("roll_number").execute()
        stu_data = students.data or []

        st.markdown(f"**{len(stu_data)} student(s) found**")

        if stu_data:
            rows = []
            for s in stu_data:
                rows.append({
                    "Roll": s.get("roll_number", ""),
                    "Name": s.get("name", ""),
                    "Class": f"{s['classes']['class_name']} {s['classes'].get('section', '')}" if s.get("classes") else "-",
                    "DOB": s.get("date_of_birth", ""),
                    "Gender": s.get("gender", ""),
                    "Face Registered": "✅" if s.get("face_encoding") else "❌",
                    "Guardian Phone": s.get("guardian_phone", ""),
                })
            st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)

            st.markdown("#### Edit / Remove Student")
            stu_opts = {f"{s['name']} (Roll: {s.get('roll_number', '')})": s for s in stu_data}
            sel = st.selectbox("Select student", list(stu_opts.keys()), key="stu_edit_sel")
            s = stu_opts[sel]

            with st.expander("Edit Details", expanded=False):
                col1, col2 = st.columns(2)
                new_name = col1.text_input("Name", value=s.get("name", ""), key="edit_stu_name")
                new_roll = col2.text_input("Roll Number", value=s.get("roll_number", ""), key="edit_stu_roll")
                new_dob = col1.text_input("Date of Birth", value=str(s.get("date_of_birth", "")), key="edit_stu_dob")
                gender_options = ["", "Male", "Female", "Other"]
                current_gender = s.get("gender", "") or ""
                if current_gender not in gender_options:
                    current_gender = ""
                new_gender = col2.selectbox("Gender", gender_options, index=gender_options.index(current_gender), key="edit_stu_gender")

                st.markdown("**Parent/Guardian Details (Optional)**")
                col3, col4 = st.columns(2)
                new_fname = col3.text_input("Father Name", value=s.get("father_name", ""), key="edit_stu_fn")
                new_mname = col4.text_input("Mother Name", value=s.get("mother_name", ""), key="edit_stu_mn")
                new_gphone = col3.text_input("Guardian Phone", value=s.get("guardian_phone", ""), key="edit_stu_gp")
                new_gemail = col4.text_input("Guardian Email", value=s.get("guardian_email", ""), key="edit_stu_ge")
                new_addr = st.text_area("Address", value=s.get("address", ""), key="edit_stu_addr", height=70)

                col_u, col_d = st.columns(2)

                if col_u.button("💾 Update Student", key="upd_stu", width="stretch"):
                    try:
                        db.table("students").update({
                            "name": new_name.strip() or None,
                            "roll_number": new_roll.strip() or None,
                            "date_of_birth": new_dob.strip() or None,
                            "gender": new_gender or None,
                            "father_name": new_fname.strip() or None,
                            "mother_name": new_mname.strip() or None,
                            "guardian_phone": new_gphone.strip() or None,
                            "guardian_email": new_gemail.strip() or None,
                            "address": new_addr.strip() or None
                        }).eq("id", s["id"]).execute()
                        st.success("Updated!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Update failed: {e}")
                        st.code(traceback.format_exc())

                if col_d.button("🗑️ Remove Student", key="del_stu", width="stretch"):
                    try:
                        db.table("students").update({"is_active": False}).eq("id", s["id"]).execute()
                        st.warning("Removed!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Remove failed: {e}")
                        st.code(traceback.format_exc())
        else:
            st.info("No students found.")

    # -------------------------------------------------
    # TAB 2 - ADD STUDENT
    # -------------------------------------------------
    with tab2:
        school_sel2 = st.selectbox("School", list(school_map.keys()), key="add_stu_sch")
        school_id2 = school_map[school_sel2]["id"]

        classes2 = db.table("classes").select("*").eq("school_id", school_id2).eq("is_active", True).order("class_name").execute()
        class_map2 = {f"{c['class_name']} - {c.get('section', '')}": c for c in (classes2.data or [])}

        if not class_map2:
            st.warning("Add a class for this school first.")
        else:
            with st.form("add_student_form"):
                cls_sel = st.selectbox("Class", list(class_map2.keys()))
                roll = st.text_input("Roll Number")
                name = st.text_input("Full Name *")

                col1, col2 = st.columns(2)
                dob = col1.text_input("Date of Birth (YYYY-MM-DD)")
                gender = col2.selectbox("Gender", ["", "Male", "Female", "Other"])

                st.markdown("**Optional Details**")
                col3, col4 = st.columns(2)
                adm_no = col3.text_input("Admission Number")
                blood = col4.text_input("Blood Group")
                address = st.text_area("Address", height=60)

                st.markdown("**Parent/Guardian (Optional)**")
                col5, col6 = st.columns(2)
                fname = col5.text_input("Father Name")
                mname = col6.text_input("Mother Name")
                gphone = col5.text_input("Guardian Phone")
                gemail = col6.text_input("Guardian Email")

                st.markdown("**Face Registration at Add Time (Optional)**")
                face_source = st.radio(
                    "Choose face input method",
                    ["No Face Now", "Upload Image", "Use Camera"],
                    horizontal=True
                )

                face_upload = None
                face_camera = None

                if face_source == "Upload Image":
                    face_upload = st.file_uploader(
                        "📷 Upload Face Photo",
                        type=["jpg", "jpeg", "png"],
                        key="add_student_face_upload"
                    )

                elif face_source == "Use Camera":
                    face_camera = st.camera_input(
                        "📸 Capture student face from camera",
                        key="add_student_face_camera"
                    )

                submitted = st.form_submit_button("➕ Add Student", width="stretch")

            if submitted:
                if not name.strip():
                    st.error("Student Name is required.")
                else:
                    face_enc = None
                    try:
                        selected_input = None
                        if face_source == "Upload Image":
                            selected_input = face_upload
                        elif face_source == "Use Camera":
                            selected_input = face_camera

                        if selected_input is not None:
                            with st.spinner("Encoding face..."):
                                face_enc, err = safe_encode_from_uploaded(selected_input)
                            if err:
                                st.warning(f"Student will be added without face data. Reason: {err}")
                                face_enc = None

                        db.table("students").insert({
                            "school_id": school_id2,
                            "class_id": class_map2[cls_sel]["id"],
                            "roll_number": roll.strip() or None,
                            "name": name.strip(),
                            "date_of_birth": dob.strip() or None,
                            "gender": gender or None,
                            "admission_number": adm_no.strip() or None,
                            "blood_group": blood.strip() or None,
                            "address": address.strip() or None,
                            "father_name": fname.strip() or None,
                            "mother_name": mname.strip() or None,
                            "guardian_phone": gphone.strip() or None,
                            "guardian_email": gemail.strip() or None,
                            "face_encoding": face_enc
                        }).execute()

                        st.success(f"Student '{name}' added successfully!")
                        st.rerun()

                    except Exception as e:
                        st.error(f"Error: {e}")
                        st.code(traceback.format_exc())

    # -------------------------------------------------
    # TAB 3 - REGISTER / UPDATE FACE
    # -------------------------------------------------
    with tab3:
        st.markdown("#### 🧠 Register / Update Face Encoding")
        st.info("You can register face using image upload or camera capture.")

        school_sel3 = st.selectbox("School", list(school_map.keys()), key="face_reg_sch")
        school_id3 = school_map[school_sel3]["id"]

        classes3 = db.table("classes").select("*").eq("school_id", school_id3).eq("is_active", True).order("class_name").execute()
        class_map3 = {f"{c['class_name']} - {c.get('section', '')}": c for c in (classes3.data or [])}

        if class_map3:
            cls_sel3 = st.selectbox("Class", list(class_map3.keys()), key="face_reg_cls")

            students3 = db.table("students").select("id,name,roll_number,face_encoding").eq(
                "class_id", class_map3[cls_sel3]["id"]
            ).eq("is_active", True).order("name").execute()

            stu_map3 = {f"{s['name']} (Roll: {s.get('roll_number', '')})": s for s in (students3.data or [])}

            if stu_map3:
                sel3 = st.selectbox("Student", list(stu_map3.keys()), key="face_reg_stu")
                stu3 = stu_map3[sel3]

                has_face = "✅ Face registered" if stu3.get("face_encoding") else "❌ No face data"
                st.markdown(f"**Current status:** {has_face}")

                reg_method = st.radio(
                    "Face input method",
                    ["Upload Image", "Use Camera"],
                    horizontal=True,
                    key="reg_face_method"
                )

                reg_upload = None
                reg_camera = None

                if reg_method == "Upload Image":
                    reg_upload = st.file_uploader(
                        "Upload Face Photo",
                        type=["jpg", "jpeg", "png"],
                        key="face_upload_register"
                    )
                    if reg_upload is not None:
                        st.image(reg_upload, caption="Selected image", width=250)

                else:
                    reg_camera = st.camera_input(
                        "Capture face from camera",
                        key="face_camera_register"
                    )
                    if reg_camera is not None:
                        st.image(reg_camera, caption="Captured image", width=250)

                if st.button("🧠 Register Face", width="stretch", key="reg_face_btn"):
                    selected_input = reg_upload if reg_method == "Upload Image" else reg_camera

                    if selected_input is None:
                        st.warning("Please upload or capture an image first.")
                    else:
                        try:
                            with st.spinner("Encoding face..."):
                                enc, err = safe_encode_from_uploaded(selected_input)

                            if err:
                                st.error(err)
                            else:
                                db.table("students").update({
                                    "face_encoding": enc
                                }).eq("id", stu3["id"]).execute()

                                st.success("✅ Face registered successfully!")
                                st.rerun()

                        except Exception as e:
                            st.error(f"Face registration failed: {e}")
                            st.code(traceback.format_exc())
            else:
                st.info("No students in this class.")
        else:
            st.info("No classes found for this school.")