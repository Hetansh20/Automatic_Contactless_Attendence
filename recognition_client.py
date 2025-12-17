import tkinter as tk
from tkinter import messagebox, ttk
import threading
import cv2
from PIL import Image, ImageTk
from face_recognition_engine import face_recognition_engine
from attendance_marker import attendance_marker
from database import Database
from datetime import datetime
import json
import os

class RecognitionClientWindow:
    """Standalone recognition client for real-time face recognition"""
    
    def __init__(self, root, session_token, faculty_data, timetable_id, on_complete_callback, on_recognized_callback=None):
        self.root = root
        self.session_token = session_token
        self.faculty_data = faculty_data
        self.timetable_id = timetable_id
        self.on_complete_callback = on_complete_callback
        self.on_recognized_callback = on_recognized_callback
        
        self.root.title("Face Recognition - Attendance Marking")
        self.root.geometry("1200x700")
        self.root.resizable(False, False)
        
        self.db = Database()
        self.cap = None
        self.is_running = False
        self.recognized_students = set()
        self.session_id = None
        self.label_mapping = {}  # Load label mapping once at startup
        self.frame_count = 0
        
        # Load label mapping
        if os.path.exists("TrainingImageLabel/label_mapping.json"):
            try:
                with open("TrainingImageLabel/label_mapping.json", "r") as f:
                    self.label_mapping = json.load(f)
                    print(f"[v0] Label mapping loaded: {self.label_mapping}")
            except Exception as e:
                print(f"[v0] Error loading label mapping: {e}")
        
        self.setup_ui()
        self.start_session()
    
    def setup_ui(self):
        """Setup the recognition client UI"""
        # Header
        header_frame = tk.Frame(self.root, bg='#2c3e50', height=80)
        header_frame.pack(fill=tk.X)
        
        title_label = tk.Label(
            header_frame,
            text="Real-time Face Recognition - Attendance Marking",
            font=('Arial', 16, 'bold'),
            bg='#2c3e50',
            fg='#ffffff'
        )
        title_label.pack(pady=10)
        
        info_label = tk.Label(
            header_frame,
            text=f"Faculty: {self.faculty_data['name']} | Session: Active",
            font=('Arial', 10),
            bg='#2c3e50',
            fg='#ecf0f1'
        )
        info_label.pack()
        
        # Main content frame
        content_frame = tk.Frame(self.root, bg='#f0f0f0')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left side - Video feed
        video_frame = tk.LabelFrame(
            content_frame,
            text="Live Camera Feed",
            font=('Arial', 11, 'bold'),
            bg='#f0f0f0'
        )
        video_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.video_label = tk.Label(video_frame, bg='#000000')
        self.video_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Right side - Status and controls
        right_frame = tk.Frame(content_frame, bg='#f0f0f0')
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False, ipadx=10)
        
        # Statistics section
        stats_frame = tk.LabelFrame(
            right_frame,
            text="Session Statistics",
            font=('Arial', 11, 'bold'),
            bg='#f0f0f0'
        )
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.stats_text = tk.Text(
            stats_frame,
            height=8,
            width=35,
            font=('Arial', 9),
            bg='#ffffff',
            fg='#2c3e50',
            relief=tk.FLAT,
            bd=1
        )
        self.stats_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Recognized students section
        recognized_frame = tk.LabelFrame(
            right_frame,
            text="Recognized Students",
            font=('Arial', 11, 'bold'),
            bg='#f0f0f0'
        )
        recognized_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.recognized_text = tk.Text(
            recognized_frame,
            height=12,
            width=35,
            font=('Arial', 9),
            bg='#ffffff',
            fg='#27ae60',
            relief=tk.FLAT,
            bd=1
        )
        self.recognized_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Control buttons
        button_frame = tk.Frame(right_frame, bg='#f0f0f0')
        button_frame.pack(fill=tk.X)
        
        self.stop_btn = tk.Button(
            button_frame,
            text='Stop Recognition',
            command=self.stop_recognition,
            font=('Arial', 10, 'bold'),
            bg='#e74c3c',
            fg='#ffffff',
            relief=tk.FLAT,
            cursor='hand2'
        )
        self.stop_btn.pack(fill=tk.X, ipady=8, pady=5)
        
        self.end_session_btn = tk.Button(
            button_frame,
            text='End Session',
            command=self.end_session,
            font=('Arial', 10, 'bold'),
            bg='#c0392b',
            fg='#ffffff',
            relief=tk.FLAT,
            cursor='hand2'
        )
        self.end_session_btn.pack(fill=tk.X, ipady=8, pady=5)
    
    def start_session(self):
        """Start the attendance session"""
        try:
            session_id, message = attendance_marker.start_session(
                self.faculty_data['faculty_id'],
                self.timetable_id
            )
            
            if session_id:
                self.session_id = session_id
                self.update_stats(f"Session started: {session_id}\nWaiting for faces...")
                self.start_recognition()
            else:
                messagebox.showerror("Error", f"Failed to start session: {message}")
                self.root.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Error starting session: {str(e)}")
            self.root.destroy()
    
    def start_recognition(self):
        """Start face recognition in a separate thread"""
        self.is_running = True
        
        # Start video capture thread
        video_thread = threading.Thread(target=self.capture_and_recognize, daemon=True)
        video_thread.start()
    
    def capture_and_recognize(self):
        """Capture video and perform face recognition"""
        try:
            self.cap = cv2.VideoCapture(0)
            
            if not self.cap.isOpened():
                self.root.after(0, lambda: self.update_stats("ERROR: Cannot access webcam"))
                return
            
            self.frame_count = 0
            
            while self.is_running:
                ret, frame = self.cap.read()
                
                if not ret:
                    break
                
                self.frame_count += 1
                
                # Perform face detection and recognition
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_recognition_engine.face_cascade.detectMultiScale(gray, 1.3, 5)
                
                for (x, y, w, h) in faces:
                    face_roi = gray[y:y+h, x:x+w]
                    
                    try:
                        label, confidence = face_recognition_engine.recognizer.predict(face_roi)
                        
                        if str(label) in self.label_mapping:
                            student_id = int(self.label_mapping[str(label)])
                            
                            if confidence < face_recognition_engine.confidence_threshold:
                                student = self.db.get_student_by_id(student_id)
                                if student:
                                    # Mark attendance only once per session
                                    if student_id not in self.recognized_students:
                                        attendance_marker.mark_student_present(
                                            student_id,
                                            self.timetable_id,
                                            100 - confidence
                                        )
                                        self.recognized_students.add(student_id)
                                        if self.on_recognized_callback:
                                            self.root.after(0, lambda: self.on_recognized_callback(self.recognized_students.copy()))
                                        self.root.after(0, lambda name=student[2], conf=100-confidence: 
                                                       self.add_recognized_student(name, conf))
                                
                                # Draw green rectangle
                                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                                cv2.putText(frame, f"Recognized (Conf: {100-confidence:.1f}%)", (x, y-10),
                                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                            else:
                                # Draw yellow rectangle (low confidence)
                                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 255), 2)
                                cv2.putText(frame, f"Low Conf: {100-confidence:.1f}%", (x, y-10),
                                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
                        else:
                            # Draw red rectangle (unknown)
                            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
                            cv2.putText(frame, f"Unknown", (x, y-10),
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                    except Exception as e:
                        print(f"[v0] Recognition error: {e}")
                        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
                
                # Add frame info
                cv2.putText(frame, f"Frame: {self.frame_count} | Recognized: {len(self.recognized_students)}", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                # Convert frame to PhotoImage
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_resized = cv2.resize(frame_rgb, (640, 480))
                image = Image.fromarray(frame_resized)
                photo = ImageTk.PhotoImage(image)
                
                self.root.after(0, lambda p=photo: self._update_video_label(p))
                
                # Update stats every 30 frames
                if self.frame_count % 30 == 0:
                    stats_text = (
                        f"Session ID: {self.session_id}\n"
                        f"Frames Processed: {self.frame_count}\n"
                        f"Students Recognized: {len(self.recognized_students)}\n"
                        f"Time: {datetime.now().strftime('%H:%M:%S')}"
                    )
                    self.root.after(0, lambda t=stats_text: self._update_stats_safe(t))
        
        except Exception as e:
            print(f"[v0] Error during recognition: {str(e)}")
            self.root.after(0, lambda: self.update_stats(f"ERROR: {str(e)}"))
        
        finally:
            if self.cap:
                self.cap.release()
    
    def _update_video_label(self, photo):
        """Safely update video label from main thread"""
        if self.is_running:
            self.video_label.config(image=photo)
            self.video_label.image = photo
    
    def _update_stats_safe(self, text):
        """Safely update stats from main thread"""
        if self.is_running:
            self.update_stats(text)
    
    def add_recognized_student(self, student_name, confidence):
        """Add a recognized student to the list"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.recognized_text.insert(tk.END, f"[{timestamp}] {student_name} (Conf: {confidence:.1f}%)\n")
        self.recognized_text.see(tk.END)
    
    def update_stats(self, text):
        """Update statistics display"""
        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(tk.END, text)
        self.stats_text.config(state=tk.DISABLED)
    
    def stop_recognition(self):
        """Stop face recognition"""
        self.is_running = False
        self.update_stats("Recognition stopped")
    
    def end_session(self):
        """End the attendance session"""
        response = messagebox.askyesno(
            "End Session",
            f"End attendance session?\n"
            f"Students recognized: {len(self.recognized_students)}"
        )
        
        if response:
            self.is_running = False
            
            if self.cap:
                self.cap.release()
            
            cv2.destroyAllWindows()
            
            session_info, message = attendance_marker.end_session()
            
            if session_info:
                messagebox.showinfo(
                    "Session Ended",
                    f"Attendance recorded successfully!\n"
                    f"Total Students: {session_info['total_students']}\n"
                    f"Present: {session_info['present_count']}\n"
                    f"Absent: {session_info['absent_count']}"
                )
            else:
                messagebox.showerror("Error", message)
            
            if self.on_complete_callback:
                self.on_complete_callback()
            
            self.root.destroy()


class FaceCaptureTool:
    """Tool for capturing student faces for training"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Face Capture Tool - Student Registration")
        self.root.geometry("800x600")
        
        self.db = Database()
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the face capture UI"""
        # Header
        header_frame = tk.Frame(self.root, bg='#2c3e50', height=60)
        header_frame.pack(fill=tk.X)
        
        title_label = tk.Label(
            header_frame,
            text="Capture Student Faces for Training",
            font=('Arial', 16, 'bold'),
            bg='#2c3e50',
            fg='#ffffff'
        )
        title_label.pack(pady=15)
        
        # Main content
        content_frame = tk.Frame(self.root, bg='#f0f0f0')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Student selection
        tk.Label(content_frame, text='Select Student:', bg='#f0f0f0', font=('Arial', 11, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        
        self.student_var = tk.StringVar()
        students = self.db.get_all_students()
        student_options = [f"{s[1]} - {s[2]}" for s in students] if students else []
        
        ttk.Combobox(content_frame, textvariable=self.student_var, values=student_options, state='readonly').pack(fill=tk.X, pady=(0, 20))
        
        # Number of images
        tk.Label(content_frame, text='Number of Images to Capture:', bg='#f0f0f0', font=('Arial', 11, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        
        self.num_images_var = tk.StringVar(value="30")
        ttk.Spinbox(content_frame, from_=10, to=100, textvariable=self.num_images_var).pack(fill=tk.X, pady=(0, 20))
        
        # Instructions
        instructions = """
Instructions:
1. Select a student from the dropdown
2. Click "Start Capture" to begin
3. Position your face in front of the camera
4. The system will capture multiple images automatically
5. Try different angles and lighting conditions
6. Press 'q' to stop capturing early
        """
        
        tk.Label(content_frame, text=instructions, bg='#f0f0f0', font=('Arial', 9), justify=tk.LEFT).pack(anchor=tk.W, pady=(0, 20))
        
        # Capture button
        tk.Button(
            content_frame,
            text='Start Capture',
            command=self.start_capture,
            font=('Arial', 12, 'bold'),
            bg='#27ae60',
            fg='#ffffff',
            relief=tk.FLAT,
            cursor='hand2'
        ).pack(fill=tk.X, ipady=10)
    
    def start_capture(self):
        """Start capturing faces"""
        if not self.student_var.get():
            messagebox.showerror("Error", "Please select a student")
            return
        
        try:
            selection = self.student_var.get()
            # Format is "StudentID - StudentName"
            parts = selection.split(' - ')
            if len(parts) != 2:
                messagebox.showerror("Error", "Invalid student selection")
                return
            
            student_id_str = parts[0].strip()
            student_name = parts[1].strip()
            
            # Get the actual database student record to get the internal ID
            student_record = self.db.get_student_by_student_id(student_id_str)
            if not student_record:
                messagebox.showerror("Error", f"Student {student_id_str} not found in database")
                return
            
            db_student_id = student_record[0]  # Internal database ID
            
            num_images = int(self.num_images_var.get())
            
            print(f"[v0] Capturing {num_images} images for {student_name} (DB ID: {db_student_id}, Student ID: {student_id_str})")
            
            # Start capture
            success, message = face_recognition_engine.capture_student_faces(
                db_student_id,
                student_name,
                num_images
            )
            
            if success:
                messagebox.showinfo("Success", message)
                
                # Ask to train model
                response = messagebox.askyesno("Train Model", "Train the model with captured faces?")
                if response:
                    train_success, train_message = face_recognition_engine.train_model()
                    if train_success:
                        messagebox.showinfo("Training Complete", train_message)
                    else:
                        messagebox.showerror("Training Error", train_message)
            else:
                messagebox.showerror("Capture Error", message)
        
        except Exception as e:
            messagebox.showerror("Error", f"Error: {str(e)}")


def main():
    """Main entry point"""
    root = tk.Tk()
    capture_tool = FaceCaptureTool(root)
    root.mainloop()


if __name__ == "__main__":
    main()
