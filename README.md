
# Contactless Attendance System 🎯

A **Contactless Attendance System** that uses **Face Recognition** to automatically mark attendance without physical interaction.  
The system captures facial images, trains a recognition model, identifies users in real time, and records attendance digitally.

---

## 📌 Overview

The project implements a face-based attendance mechanism using **Local Binary Pattern Histogram (LBPH)** for face recognition.  
Facial images are captured through a webcam, processed using OpenCV, and matched against trained data. Once a face is recognized, attendance is recorded in the database and can be exported or emailed as reports.

---

## ✨ Key Features

- 📷 Face detection using Haar Cascade Classifier  
- 🧠 Face recognition using **LBP / LBPH algorithm**  
- 🗂️ Automatic attendance marking  
- 👨‍🏫 Faculty authentication system  
- 🗄️ SQLite database integration  
- 📊 Attendance export to CSV  
- ✉️ Automated email reporting  
- 🖥️ GUI-based interface and backend API  
- 🔐 Secure login and session handling  

---

## 🛠️ Technologies Used

- **Programming Language:** Python  
- **Computer Vision:** OpenCV  
- **Face Recognition Algorithm:** Local Binary Pattern Histogram (LBPH)  
- **Database:** SQLite  
- **GUI Framework:** Tkinter / CustomTkinter  
- **Backend Framework:** Flask  
- **Email Service:** SMTP  
- **Version Control:** Git  

---

## 📂 Project Structure

Contactless-Attendance-System/
│
├── Attendance/ # Daily attendance records
├── EmployeeDetails/ # Registered user data
├── ImagesUnknown/ # Unrecognized face images
├── TrainingImage/ # Training dataset
├── TrainingImageLabel/ # Generated labels
│
├── admin_dashboard.py
├── app_launcher.py
├── attendance_client.py
├── attendance_marker.py
├── attendance_system.db
├── auth.py
├── automail.py
├── automail_enhanced.py
├── Capture_Image.py
├── csv_export_service.py
├── database.py
├── email_service.py
├── face_recognition_engine.py
├── faculty_login.py
├── haarcascade_frontalface_default.xml
├── Info.py
├── label_mapping.json
├── main.py
├── main_gui.py
├── Recognize.py
├── recognition_client.py
├── Train_Image.py
├── timetable_manager/
├── requirements.txt
├── setup.py
└── README.md

yaml
Copy code

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/your-username/Contactless-Attendance-System.git
cd Contactless-Attendance-System
2️⃣ Create and Activate Virtual Environment
bash
Copy code
python -m venv venv
venv\Scripts\activate   # Windows
3️⃣ Install Dependencies
bash
Copy code
pip install -r requirements.txt
🚀 How to Run the System
▶️ Launch GUI
bash
Copy code
python main_gui.py
▶️ Start Backend Server
bash
Copy code
python main.py
▶️ Capture User Images
bash
Copy code
python Capture_Image.py
▶️ Train Face Recognition Model
bash
Copy code
python Train_Image.py
▶️ Recognize Face and Mark Attendance
bash
Copy code
python Recognize.py
🔄 System Flow
Step-by-Step Flow
Faculty Login

Faculty logs in using secure credentials.

Image Capture

Facial images are captured via webcam for new users.

Image Preprocessing

Face detection using Haar Cascade.

Grayscale conversion and normalization.

Model Training

Feature extraction using LBP.

Histogram generation using LBPH.

Face Recognition

Live face captured.

Histogram comparison with trained data.

Attendance Marking

If matched, attendance is stored in database.

If not matched, face is saved as unknown.

Report Generation

Attendance exported as CSV.

Email report sent automatically.

🔁 Flow Diagram
pgsql
Copy code
+-------------------+
| Faculty Login     |
+---------+---------+
          |
          v
+-------------------+
| Capture Face      |
+---------+---------+
          |
          v
+-------------------+
| Face Detection    |
| (Haar Cascade)    |
+---------+---------+
          |
          v
+-------------------+
| LBP Feature       |
| Extraction        |
+---------+---------+
          |
          v
+-------------------+
| LBPH Model        |
| Training / Match  |
+---------+---------+
          |
    +-----+-----+
    |           |
    v           v
+---------+  +------------------+
| Known   |  | Unknown Face     |
| Face    |  | Stored           |
+----+----+  +------------------+
     |
     v
+-------------------+
| Mark Attendance   |
+---------+---------+
          |
          v
+-------------------+
| Database / CSV /  |
| Email Report      |
+-------------------+
📊 Attendance Management
Attendance is stored in:

SQLite database

CSV report files

Each record contains:

User ID

Name

Date and time

Session or subject information

🔐 Authentication
Faculty login system

Password hashing

Session-based access control

📧 Email Reporting
Attendance reports sent automatically

SMTP-based email service

Supports enhanced templates

⚠️ Important Notes
Webcam access is required

Proper lighting improves recognition accuracy

Train the model with sufficient images per user

Unknown faces are stored for review

👥 Project Authors
Ansh Raythatha

Hetansh Shah
