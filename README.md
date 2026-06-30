# 🎓 FaceAttend — AI-Based Face Attendance System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35-red?style=for-the-badge&logo=streamlit)
![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-green?style=for-the-badge&logo=supabase)
![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10-orange?style=for-the-badge&logo=google)
![License](https://img.shields.io/badge/License-MIT-purple?style=for-the-badge)

**An AI-powered, real-time face recognition attendance system for schools.**  
Built with Python · Streamlit · face_recognition · MediaPipe · Supabase

[Features](#-features) · [Demo](#-project-structure) · [Setup](#-installation) · [Usage](#-how-to-use) · [Tech Stack](#-tech-stack)

</div>

---

## 📌 Overview

**FaceAttend** is a full-stack web application that automates student attendance using real-time facial recognition. Teachers can mark attendance in seconds using any mobile or laptop camera. The system uses **eye-blink liveness detection** to prevent photo spoofing, and all data is stored securely in a cloud database (Supabase).

It supports two roles:
- 👩‍🏫 **Teacher** — take attendance, view reports, download CSV/Excel/PDF
- 🛡️ **Admin** — manage schools, classes, students, teachers, promote classes

---

## ✨ Features

### 👩‍🏫 Teacher Dashboard
- Login with School ID + Teacher ID
- Start live attendance session by class
- Real-time face recognition via mobile (front/back) or laptop camera
- **Eye-blink liveness detection** — prevents photo spoofing
- Auto-mark present + manual override for unrecognized students
- Mark all students present in one click
- View class-wise attendance reports with date filters
- Per-student attendance % with **low attendance alerts (< 75%)**
- Export reports as **CSV / Excel / PDF**

### 🛡️ Admin Dashboard
- Manage Schools, Classes, Teachers, Students (Full CRUD)
- Register student face photos — auto-generates 128-dim face encodings
- **Face Quality Check** — rejects blurry, dark, or multi-face images
- **Class Promotion** — promote whole class or individual students (preserves face data + student ID)
- Reports at 3 levels: Overall · School-wise · Class-wise
- Export all data as CSV / Excel / PDF

### 🔐 Security
- SHA-256 password hashing — no plain-text passwords stored
- Eye-blink liveness detection via MediaPipe EAR method
- Face image quality validation at registration
- Role-based access control (Teacher vs Admin)

---

## 🗂️ Project Structure

```
face_attendance/
├── app.py                     ← Main entry point + homepage
├── requirements.txt           ← All dependencies
├── schema.sql                 ← Supabase DB schema (run once)
├── .env.example               ← Environment variables template
├── .streamlit/
│   └── config.toml            ← Theme + upload limit settings
├── pages/
│   ├── teacher_login.py       ← Teacher login page
│   ├── teacher_dashboard.py   ← Teacher home dashboard
│   ├── take_attendance.py     ← Live camera + liveness + face match
│   ├── teacher_reports.py     ← Reports + export for teacher
│   ├── admin_login.py         ← Admin login page
│   ├── admin_dashboard.py     ← Admin home dashboard
│   ├── admin_schools.py       ← School management
│   ├── admin_classes.py       ← Class management
│   ├── admin_students.py      ← Student management + face registration
│   ├── admin_teachers.py      ← Teacher management
│   ├── admin_reports.py       ← Multi-level reports
│   └── admin_promote.py       ← Class & student promotion
└── utils/
    ├── db.py                  ← Supabase client (cached connection)
    ├── auth.py                ← SHA-256 login verification
    ├── face_utils.py          ← face_recognition + MediaPipe liveness
    └── reports.py             ← CSV / Excel / FPDF export helpers
```

---

## 🛠️ Installation

### Prerequisites
- Python 3.9 or higher
- A free [Supabase](https://supabase.com) account
- VS Code (recommended)
- Git

---

### Step 1 — Clone the Repository

```bash
git clone https://github.com/your-username/face-attend.git
cd face-attend
```

---

### Step 2 — Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / Mac
source venv/bin/activate
```

---

### Step 3 — Install dlib (Windows only)

> dlib requires a C++ build environment. The easiest way on Windows is using a prebuilt wheel.

```bash
pip install cmake

# Download the correct .whl for your Python version from:
# https://github.com/z-mahmud22/Dlib_Windows_Python3.x
pip install dlib-19.24.2-cp311-cp311-win_amd64.whl

pip install face_recognition
```

---

### Step 4 — Install All Dependencies

```bash
pip install -r requirements.txt
```

---

### Step 5 — Set Up Supabase

1. Go to [supabase.com](https://supabase.com) → Create a new project
2. Go to **Settings → API**
3. Copy your **Project URL** and **Anon Key**
4. Open the **SQL Editor** → paste the full contents of `schema.sql` → click **Run**

---

### Step 6 — Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env`:

```env
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_KEY=your-anon-key-here
```

---

### Step 7 — Run the App

```bash
streamlit run app.py
```

Open **http://localhost:8501** in your browser 🎉

---

## 🔑 Default Admin Credentials

| Field    | Value       |
|----------|-------------|
| Username | `admin`     |
| Password | `admin@123` |

> ⚠️ **Change the default password immediately after first login.**  
> Generate a new hash: `python -c "import hashlib; print(hashlib.sha256(b'newpassword').hexdigest())"`  
> Then update the `admins` table in Supabase.

---

## 🚀 How to Use

### As Admin
1. Login at `/admin_login`
2. Add a School → Add Classes → Add Teachers
3. Add Students → Upload face photos (quality check runs automatically)
4. View reports from Admin Dashboard

### As Teacher
1. Login at `/teacher_login` with your School ID + Teacher ID
2. Select your class and enter your name
3. Click **Start Attendance** — camera opens
4. Each student stands in front of the camera and **blinks once**
5. System auto-marks them present
6. Review the list, correct any errors manually, and submit
7. Download reports from the Reports page

---

## 🧠 Tech Stack

| Category | Technology |
|----------|------------|
| Web Framework | [Streamlit](https://streamlit.io) |
| Face Recognition | [face_recognition](https://github.com/ageitgey/face_recognition) (dlib) |
| Liveness Detection | [MediaPipe Face Mesh](https://ai.google.dev/edge/mediapipe/solutions/vision/face_landmarker) |
| Image Processing | OpenCV, NumPy, Pillow |
| Database | [Supabase](https://supabase.com) (PostgreSQL) |
| Reporting | pandas, openpyxl, FPDF2 |
| Security | SHA-256 (hashlib) |
| Language | Python 3.9+ |

---

## 🧬 How Face Recognition Works

1. **Registration**: Student photo is uploaded → `face_recognition` generates a **128-dimensional face encoding vector** → stored as JSON in Supabase
2. **Attendance**: Camera captures live frame → encoding extracted → **Euclidean distance** compared against all stored encodings
3. **Match condition**: `distance ≤ 0.5` → student identified ✅
4. **Liveness check**: MediaPipe detects **Eye Aspect Ratio (EAR)** → confirmed blink required before marking

```
EAR = (||p2-p6|| + ||p3-p5||) / (2 × ||p1-p4||)

Eye OPEN  : EAR ≈ 0.30–0.40
Eye CLOSED: EAR < 0.25  →  blink confirmed ✅
```

---

## 🔍 Face Image Quality Check

At registration, photos are validated for:

| Check | Condition |
|-------|-----------|
| Blur | Laplacian variance > 100 |
| Brightness | Mean pixel value between 70–200 |
| Face count | Exactly 1 face detected |
| Face detected | MediaPipe confirms face present |

Low-quality images are **rejected before encoding** — this reduces false matches during attendance.

---

## 📊 Database Schema

| Table | Key Columns |
|-------|-------------|
| `schools` | id, school_id, name, address |
| `classes` | id, school_id (FK), class_name, section, academic_year |
| `students` | id, student_id, class_id (FK), name, face_encodings (JSON) |
| `teachers` | id, teacher_id, school_id (FK), name, password_hash |
| `admins` | id, username, password_hash |
| `attendance_records` | id, student_id, class_id, date, status, marked_by, method |

---

## 🔮 Future Scope

- [ ] 3D liveness detection using depth cameras
- [ ] Multi-face simultaneous detection
- [ ] Native Android / iOS app
- [ ] Parent SMS/email alerts via Twilio on absence
- [ ] Offline mode with SQLite + cloud sync
- [ ] Plotly-based analytics dashboard (heatmaps, trend lines)
- [ ] Fingerprint backup biometric
- [ ] Timetable integration for automatic session scheduling

---

## ⚠️ Known Limitations

- Face recognition may produce false positives if two students look similar — use stricter threshold (0.5) and enroll multiple photos per student
- Accuracy decreases in poor lighting — ensure well-lit environment for best results
- dlib installation on Windows requires extra steps (see setup guide above)
- Mobile camera quality varies — higher resolution phones give better results

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Satyam Kumar**  
BSc. (Hons.) Data Science & Artificial Intelligence  
Indian Institute of Technology Guwahati (Online Degree Programme)  
Student ID: 23035010959  
Course: DA-379 — Term Project 2  

---

## 🙏 Acknowledgements

- [ageitgey/face_recognition](https://github.com/ageitgey/face_recognition) — face encoding library
- [Google MediaPipe](https://ai.google.dev/edge/mediapipe) — face mesh and landmark detection
- [Supabase](https://supabase.com) — open-source Firebase alternative
- [Streamlit](https://streamlit.io) — Python web app framework

---

<div align="center">
  Made with ❤️ using Python · Streamlit · MediaPipe · Supabase
</div>
