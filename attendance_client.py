import tkinter as tk
from tkinter import messagebox
import threading
from datetime import datetime
from auth import auth_manager
from database import Database

class AttendanceClientWindow:
    """Main attendance client window for faculty"""
    
    def __init__(self, root, session_token, faculty_data, on_logout_callback):
        self.root = root
        self.session_token = session_token
        self.faculty_data = faculty_data
        self.on_logout_callback = on_logout_callback
        
        self.root.title("Contactless Attendance System - Attendance Session")
        self.root.geometry("700x600")
        self.root.resizable(False, False)
        
        self.db = Database()
        self.active_class = None
        self.session_id = None
        self.recognized_students = set()
        
        self.setup_ui()
        self.load_active_class()
    
    def setup_ui(self):
        """Setup the attendance client UI"""
        # Header
        header_frame = tk.Frame(self.root, bg='#2c3e50', height=100)
        header_frame.pack(fill=tk.X)
        
        title_label = tk.Label(
            header_frame,
            text=f"Welcome, {self.faculty_data['name']}",
            font=('Arial', 18, 'bold'),
            bg='#2c3e50',
            fg='#ffffff'
        )
        title_label.pack(pady=10)
        
        info_label = tk.Label(
            header_frame,
            text=f"Department: {self.faculty_data.get('department', 'N/A')}",
            font=('Arial', 10),
            bg='#2c3e50',
            fg='#ecf0f1'
        )
        info_label.pack()
        
        # Main content
        content_frame = tk.Frame(self.root, bg='#f0f0f0')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Class info section
        class_frame = tk.LabelFrame(
            content_frame,
            text="Active Class",
            font=('Arial', 11, 'bold'),
            bg='#f0f0f0',
            fg='#2c3e50'
        )
        class_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.class_info_var = tk.StringVar(value="Loading class information...")
        class_info_label = tk.Label(
            class_frame,
            textvariable=self.class_info_var,
            font=('Arial', 10),
            bg='#f0f0f0',
            fg='#2c3e50',
            justify=tk.LEFT
        )
        class_info_label.pack(padx=10, pady=10, anchor=tk.W)
        
        # Attendance status section
        status_frame = tk.LabelFrame(
            content_frame,
            text="Attendance Status",
            font=('Arial', 11, 'bold'),
            bg='#f0f0f0',
            fg='#2c3e50'
        )
        status_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        self.status_text = tk.Text(
            status_frame,
            height=10,
            font=('Arial', 9),
            bg='#ffffff',
            fg='#2c3e50',
            relief=tk.FLAT,
            bd=1
        )
        self.status_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Button frame
        button_frame = tk.Frame(content_frame, bg='#f0f0f0')
        button_frame.pack(fill=tk.X)
        
        start_btn = tk.Button(
            button_frame,
            text='Start Recognition',
            command=self.start_recognition,
            font=('Arial', 11, 'bold'),
            bg='#27ae60',
            fg='#ffffff',
            relief=tk.FLAT,
            cursor='hand2'
        )
        start_btn.pack(side=tk.LEFT, padx=(0, 10), ipady=8, ipadx=20)
        
        end_btn = tk.Button(
            button_frame,
            text='End Session',
            command=self.end_session,
            font=('Arial', 11, 'bold'),
            bg='#e74c3c',
            fg='#ffffff',
            relief=tk.FLAT,
            cursor='hand2'
        )
        end_btn.pack(side=tk.LEFT, padx=(0, 10), ipady=8, ipadx=20)
        
        export_btn = tk.Button(
            button_frame,
            text='Export Session (CSV)',
            command=self.export_session_csv,
            font=('Arial', 11, 'bold'),
            bg='#f39c12',
            fg='#ffffff',
            relief=tk.FLAT,
            cursor='hand2'
        )
        export_btn.pack(side=tk.LEFT, padx=(0, 10), ipady=8, ipadx=20)
        
        logout_btn = tk.Button(
            button_frame,
            text='Logout',
            command=self.logout,
            font=('Arial', 11, 'bold'),
            bg='#95a5a6',
            fg='#ffffff',
            relief=tk.FLAT,
            cursor='hand2'
        )
        logout_btn.pack(side=tk.LEFT, ipady=8, ipadx=20)
    
    def load_active_class(self):
        """Load the active class for the faculty"""
        try:
            faculty_id = self.faculty_data['faculty_id']
            active_class, message = auth_manager.get_active_class(faculty_id)
            
            if active_class:
                self.active_class = active_class
                class_info = f"""
Class: {active_class[2]}
Day: {active_class[3]}
Time: {active_class[4]} - {active_class[5]}
Room: {active_class[6] or 'N/A'}
                """
                self.class_info_var.set(class_info.strip())
                self.log_status(f"✓ Active class loaded: {active_class[2]}")
            else:
                self.class_info_var.set("No active class at this time")
                self.log_status("⚠ No active class found. Please check the timetable.")
        except Exception as e:
            self.log_status(f"✗ Error loading class: {str(e)}")
    
    def start_recognition(self):
        """Start face recognition for attendance"""
        if not self.active_class:
            messagebox.showwarning("No Active Class", "There is no active class at this time.")
            return
        
        self.log_status("Starting face recognition...")
        messagebox.showinfo(
            "Recognition Started",
            "Face recognition will start in a new window.\n"
            "Please ensure the webcam is properly positioned."
        )
        
        # Import and launch the recognition client
        try:
            from recognition_client import RecognitionClientWindow
            
            recognition_root = tk.Toplevel(self.root)
            recognition_window = RecognitionClientWindow(
                recognition_root,
                self.session_token,
                self.faculty_data,
                self.active_class[0],  # timetable_id
                self.on_recognition_complete,
                self.update_recognized_students  # Add callback to update recognized students
            )
            
            self.log_status("✓ Face recognition session started")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start recognition: {str(e)}")
            self.log_status(f"✗ Error starting recognition: {str(e)}")
    
    def on_recognition_complete(self):
        """Callback when recognition is complete"""
        self.log_status("✓ Face recognition session completed")
    
    def update_recognized_students(self, recognized_set):
        """Update recognized students from recognition client"""
        self.recognized_students = recognized_set
        self.log_status(f"Updated: {len(self.recognized_students)} students recognized")
    
    def end_session(self):
        """End the attendance session"""
        if not self.active_class:
            messagebox.showwarning("No Session", "No active session to end.")
            return
        
        response = messagebox.askyesno(
            "End Session",
            f"End attendance session for {self.active_class[2]}?\n"
            f"Recognized students: {len(self.recognized_students)}"
        )
        
        if response:
            self.log_status("✓ Attendance session ended")
            messagebox.showinfo("Session Ended", "Attendance has been recorded.")
    
    def logout(self):
        """Logout from the attendance session"""
        response = messagebox.askyesno("Logout", "Are you sure you want to logout?")
        if response:
            self.on_logout_callback()
            self.root.destroy()
    
    def log_status(self, message):
        """Log a status message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.status_text.see(tk.END)
        self.status_text.update()
    
    def export_session_csv(self):
        """Export current session attendance to CSV"""
        if not self.active_class:
            messagebox.showwarning("No Session", "No active session to export.")
            return
        
        try:
            from csv_export_service import CSVExportService
            
            export_service = CSVExportService()
            class_name = self.active_class[2]
            timetable_id = self.active_class[0]
            
            filename, message = export_service.export_session_attendance(timetable_id, class_name)
            
            if filename:
                messagebox.showinfo("Export Successful", f"{message}\n\nFile saved: {filename}")
                self.log_status(f"✓ Session exported to CSV: {filename}")
            else:
                messagebox.showwarning("Export Failed", message)
                self.log_status(f"✗ Failed to export session: {message}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Error exporting session: {str(e)}")
            self.log_status(f"✗ Error exporting session: {str(e)}")
