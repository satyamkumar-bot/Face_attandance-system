import streamlit as st
from utils.db import get_db
from utils.face_utils import decode_face_encoding, compare_faces_batch, encode_face
from views._sidebar import teacher_sidebar
from PIL import Image
import numpy as np
import pandas as pd
import traceback
from datetime import datetime, date


def require_teacher():
    if not st.session_state.get("teacher_logged_in"):
        st.session_state["page"] = "teacher_login"
        st.rerun()


def image_to_np(uploaded_file):
    if uploaded_file is None:
        return None
    try:
        img = Image.open(uploaded_file).convert("RGB")
        return np.array(img)
    except Exception:
        return None


def mark_attendance(db, school_id, class_id, teacher_id, student_id, status="present", method="face"):
    today = date.today().isoformat()

    existing = db.table("attendance").select("id").eq("date", today).eq("student_id", student_id).eq("class_id", class_id).execute()
    if existing.data:
        return False, "Already marked today."

    db.table("attendance").insert({
        "school_id": school_id,
        "class_id": class_id,
        "teacher_id": teacher_id,
        "student_id": student_id,
        "date": today,
        "status": status,
        "marked_by": method,
        "marked_at": datetime.now().isoformat()
    }).execute()
    return True, "Marked present."


def safe_student_face_array(stu):
    enc = stu.get("face_encoding")
    if not enc:
        return None
    return decode_face_encoding(enc)


def show():
    require_teacher()
    teacher_sidebar()
    db = get_db()

    teacher = st.session_state["teacher_data"]
    school = st.session_state["school_data"]

    st.markdown("<h2 style='color:#01696f'>📸 Take Attendance</h2>", unsafe_allow_html=True)
    st.caption("Capture from camera or upload image, then match faces against the selected class.")

    schools = db.table("schools").select("id,name,school_id").eq("is_active", True).execute()
    school_map = {f"{s['name']} ({s['school_id']})": s for s in (schools.data or [])}

    if not school_map:
        st.warning("No schools found.")
        return

    school_labels = list(school_map.keys())
    default_school = next((i for i, k in enumerate(school_labels) if school_map[k]["id"] == school["id"]), 0)
    sel_school = st.selectbox("School", school_labels, index=default_school, key="att_school")
    school_id = school_map[sel_school]["id"]

    classes = db.table("classes").select("*").eq("school_id", school_id).eq("is_active", True).order("class_name").execute()
    class_map = {f"{c['class_name']} - {c.get('section', '')}": c for c in (classes.data or [])}

    if not class_map:
        st.warning("No classes found for this school.")
        return

    class_labels = list(class_map.keys())
    selected_class_label = st.selectbox("Class", class_labels, key="att_class")
    cls = class_map[selected_class_label]

    tab1, tab2, tab3 = st.tabs(["🎥 Camera", "🖼️ Upload Image", "✍️ Manual"])

    with tab1:
        st.info("Capture a clear image from the camera, then match faces.")
        cam = st.camera_input("Use camera to capture attendance", key="attendance_camera")

        if cam is not None:
            img_np = image_to_np(cam)
            if img_np is None:
                st.error("Could not read camera image.")
            else:
                st.image(img_np, caption="Captured Frame", width=450)

                if st.button("🔍 Recognize & Mark", key="cam_recognize", width="stretch"):
                    process_attendance_image(db, img_np, school_id, cls, teacher, selected_class_label)

    with tab2:
        up = st.file_uploader("Upload attendance image", type=["jpg", "jpeg", "png"], key="attendance_upload")
        if up is not None:
            img_np = image_to_np(up)
            if img_np is None:
                st.error("Could not read uploaded image.")
            else:
                st.image(img_np, caption="Uploaded Image", width=450)

                if st.button("🔍 Recognize & Mark from Image", key="img_recognize", width="stretch"):
                    process_attendance_image(db, img_np, school_id, cls, teacher, selected_class_label)

    with tab3:
        st.warning("Use manual attendance if face recognition fails.")
        students = db.table("students").select("id,name,roll_number").eq("class_id", cls["id"]).eq("is_active", True).order("roll_number").execute()
        stu_data = students.data or []

        if not stu_data:
            st.info("No students in this class.")
            return

        present_names = st.multiselect(
            "Select present students",
            [f"{s['name']} ({s.get('roll_number', '')})" for s in stu_data],
            key="manual_present"
        )

        if st.button("✅ Save Manual Attendance", key="save_manual", width="stretch"):
            today = date.today().isoformat()
            count = 0
            for label in present_names:
                student = next((x for x in stu_data if f"{x['name']} ({x.get('roll_number', '')})" == label), None)
                if student:
                    existing = db.table("attendance").select("id").eq("date", today).eq("student_id", student["id"]).eq("class_id", cls["id"]).execute()
                    if not existing.data:
                        db.table("attendance").insert({
                            "school_id": school_id,
                            "class_id": cls["id"],
                            "teacher_id": teacher["id"],
                            "student_id": student["id"],
                            "date": today,
                            "status": "present",
                            "marked_by": "manual",
                            "marked_at": datetime.now().isoformat()
                        }).execute()
                        count += 1
            st.success(f"Saved manual attendance for {count} student(s).")


def process_attendance_image(db, img_np, school_id, cls, teacher, selected_class_label):
    try:
        students = db.table("students").select("id,name,roll_number,face_encoding").eq("class_id", cls["id"]).eq("is_active", True).execute()
        stu_data = students.data or []

        known_encodings = []
        known_students = []

        for s in stu_data:
            enc = s.get("face_encoding")
            if enc:
                decoded = decode_face_encoding(enc)
                if decoded is not None:
                    known_encodings.append(decoded)
                    known_students.append(s)

        if not known_encodings:
            st.warning("No face data found for students in this class.")
            return

        live_encoding = encode_face(img_np)
        if live_encoding is None:
            st.error("No clear face detected in the captured image.")
            return

        matches, distances, best_index = compare_faces_batch(known_encodings, live_encoding)

        if best_index is None:
            st.error("No matching student found.")
            return

        best_student = known_students[best_index]
        best_distance = distances[best_index]

        st.write(f"Best match: **{best_student['name']}**")
        st.write(f"Distance: `{best_distance:.4f}`")

        if matches[best_index]:
            ok, msg = mark_attendance(
                db=db,
                school_id=school_id,
                class_id=cls["id"],
                teacher_id=teacher["id"],
                student_id=best_student["id"],
                status="present",
                method="face"
            )
            if ok:
                st.success(f"✅ {best_student['name']} marked present.")
            else:
                st.info(msg)
        else:
            st.warning("Face not close enough to a known student.")
    except Exception as e:
        st.error(f"Attendance processing failed: {e}")
        st.code(traceback.format_exc())