# FaceAttend

FaceAttend is a lightweight, cloud-integrated school attendance system that uses facial recognition and liveness detection. 

I built this to solve a specific problem: manual roll calls in schools waste a lot of instructional time, but dedicated biometric hardware (like fingerprint scanners or RFID gates) is too expensive and hard to maintain for resource-constrained or rural institutions. FaceAttend shifts that logic to software, allowing teachers to take attendance using the standard cameras already built into their laptops or smartphones.

## 🎯 What it does

The system is split into two main portals:
* **Admin Dashboard:** For management to handle the database. You can register schools, add teachers, enroll students (and capture their facial biometric data), and promote whole classes at the end of the academic year.
* **Teacher Portal:** A mobile-friendly interface where teachers select their class and start a continuous camera loop. As students walk by, the system verifies they are a live human (via eye-blink detection), matches their face, logs them as "Present" in the database, and shows a quick toast notification.

### Key Features
* **Continuous Auto-Attendance:** No clicking required. The camera stream processes frames in real-time.
* **Anti-Spoofing:** Uses MediaPipe Face Mesh to track the Eye Aspect Ratio (EAR). It requires a blink to register attendance, preventing students from holding up photos of their friends.
* **Manual Overrides:** Computer vision isn't perfect, especially in poorly lit classrooms. Teachers can easily override the AI and mark a student present manually.
* **Automated Reporting:** Generates and downloads class-wise or school-wise attendance reports in CSV, Excel, or PDF formats.

## 🛠️ Tech Stack

* **Frontend & Routing:** Streamlit (Custom CSS to hide native sidebars for a seamless app-like feel)
* **Computer Vision:** OpenCV (`opencv-python-headless` for cloud compatibility), MediaPipe
* **Facial Recognition:** `face_recognition` (built on dlib's HOG model)
* **Database:** Supabase (PostgreSQL)
* **Reporting:** Pandas, OpenPyXL, FPDF

---

## 💻 Local Setup & Installation

If you want to run this on your own machine, follow these steps. 

**1. Clone the repo and set up a virtual environment**
```bash
git clone [https://github.com/yourusername/Face-attendance_system.git](https://github.com/yourusername/Face-attendance_system.git)
cd Face-attendance_system
python -m venv venv

# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
