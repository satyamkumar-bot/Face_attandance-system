import hashlib
import streamlit as st
from utils.db import get_db

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_teacher_login(school_id: str, teacher_id: str, password: str) -> dict | None:
    db = get_db()
    # Get school
    school = db.table("schools").select("*").eq("school_id", school_id).eq("is_active", True).execute()
    if not school.data:
        return None
    school_data = school.data[0]
    # Get teacher
    teacher = db.table("teachers").select("*").eq("teacher_id", teacher_id).eq("school_id", school_data["id"]).eq("is_active", True).execute()
    if not teacher.data:
        return None
    t = teacher.data[0]
    if t["password_hash"] == hash_password(password):
        return {"teacher": t, "school": school_data}
    return None

def verify_admin_login(username: str, password: str) -> bool:
    db = get_db()
    admin = db.table("admins").select("*").eq("username", username).execute()
    if not admin.data:
        return False
    stored = admin.data[0]["password_hash"]
    return stored == hash_password(password)

def teacher_logout():
    for key in ["teacher_logged_in", "teacher_data", "school_data", "teacher_name_input"]:
        st.session_state.pop(key, None)

def admin_logout():
    for key in ["admin_logged_in"]:
        st.session_state.pop(key, None)
