# Contactless Attendance System 🎯

A **Contactless Attendance System** that uses **Face Recognition** to automatically mark attendance without physical interaction.  
The system captures facial images, trains a recognition model, identifies users in real time, and records attendance digitally.

---

## 📌 Overview

This project implements a face-based attendance mechanism using **Local Binary Pattern (LBP)** and **Local Binary Pattern Histogram (LBPH)** algorithms.  
Facial images are captured through a webcam, processed using OpenCV, and matched against trained data. When a face is successfully recognized, attendance is recorded in the database and can be exported or emailed as reports.

---

## ✨ Features

- Face detection using Haar Cascade Classifier  
- Face recognition using **LBP / LBPH**  
- Automatic attendance marking  
- Faculty authentication system  
- SQLite database storage  
- CSV export of attendance  
- Automated email reports  
- GUI-based application  
- Backend API support  

---

## 🛠️ Technologies Used

- **Language:** Python  
- **Computer Vision:** OpenCV  
- **Face Recognition:** LBP, LBPH  
- **Database:** SQLite  
- **GUI:** Tkinter / CustomTkinter  
- **Backend:** Flask  
- **Email Service:** SMTP  

---

## 📂 Project Structure

```text
Contactless-Attendance-System/
│
├── Attendance/                   # Daily attendance records
├── EmployeeDetails/              # Registered user details
├── ImagesUnknown/                # Unrecognized face images
├── TrainingImage/                # Images used for training
├── TrainingImageLabel/           # Generated labels
│
├── admin_dashboard.py            # Admin dashboard
├── app_launcher.py               # Application launcher
├── attendance_client.py
├── attendance_marker.py          # Attendance logic
├── attendance_system.db          # SQLite database
├── auth.py                       # Authentication logic
├── automail.py                   # Email service
├── automail_enhanced.py
├── Capture_Image.py              # Capture face images
├── csv_export_service.py         # CSV export
├── database.py                   # Database operations
├── email_service.py
├── face_recognition_engine.py    # Face recognition core
├── faculty_login.py              # Faculty login module
├── haarcascade_frontalface_default.xml
├── Info.py
├── label_mapping.json
├── main.py                       # Backend server
├── main_gui.py                   # GUI entry point
├── Recognize.py                  # Recognition & attendance
├── recognition_client.py
├── Train_Image.py                # Model training
├── timetable_manager/
├── requirements.txt
├── setup.py
└── README.md
```
---

##⚙️ Installation & Setup
# Step 1: Clone the Repository
- git clone https://github.com/your-username/Contactless-Attendance-System.git
- cd Contactless-Attendance-System

# Step 2: Create Virtual Environment
- python -m venv venv

# Step 3: Activate Virtual Environment
- venv\Scripts\activate      # Windows
- #source venv/bin/activate  # Linux / macOS

# Step 4: Install Dependencies
- pip install -r requirements.txt

---

## 🚀 How to Run

# Start GUI Application
- python main_gui.py

---

## 🔄 System Flow

- Faculty logs in using credentials
- Facial images are captured via webcam
- Face detection using Haar Cascade
- Feature extraction using LBP
- Histogram generation using LBPH
- Live face comparison with trained data
- Attendance marked for recognized faces
- Data stored and reports generated

---

## 📊 Attendance Management

- Stored in SQLite database
- Exportable as CSV
- Each record contains:
- User ID
- Name
- Date
- Time
- Subject / Session

---

## 🔐 Authentication

- Faculty login system
- Password hashing
- Session-based access control

---

## 📧 Email Reporting

- Automatic attendance reports via email
- SMTP-based email service
- Configurable email settings

---

## ⚠️ Important Notes

- Webcam access is required
- Proper lighting improves recognition accuracy
- Train the model with sufficient images
- Unknown faces are stored for review

---

## 👥 Project Authors
- [Ansh Raythatha] (https://github.com/Ansh0308)
- [Hetansh Shah] (https://github.com/Hetansh20)

---

## 📌 Conclusion
- This project demonstrates a complete face recognition–based attendance system using LBP and LBPH, integrating image processing, machine learning, database management, and automated reporting into a single application.
