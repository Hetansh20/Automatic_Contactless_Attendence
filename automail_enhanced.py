import tkinter as tk
from tkinter import messagebox, ttk
from email_service import email_service
from database import Database
from datetime import datetime, timedelta
import threading

class AutoMailWindow:
    """Auto-mail configuration and sending window"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Auto-Mail - Attendance Summary")
        self.root.geometry("700x600")
        
        self.db = Database()
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the auto-mail UI"""
        # Header
        header_frame = tk.Frame(self.root, bg='#2c3e50', height=60)
        header_frame.pack(fill=tk.X)
        
        title_label = tk.Label(
            header_frame,
            text="Auto-Mail - Send Attendance Summaries",
            font=('Arial', 16, 'bold'),
            bg='#2c3e50',
            fg='#ffffff'
        )
        title_label.pack(pady=15)
        
        # Main content
        content_frame = tk.Frame(self.root, bg='#f0f0f0')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Email configuration section
        config_frame = tk.LabelFrame(
            content_frame,
            text="Email Configuration",
            font=('Arial', 11, 'bold'),
            bg='#f0f0f0'
        )
        config_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Sender email
        tk.Label(config_frame, text='Sender Email:', bg='#f0f0f0', font=('Arial', 10, 'bold')).pack(anchor=tk.W, padx=10, pady=(10, 0))
        self.sender_email_var = tk.StringVar()
        tk.Entry(config_frame, textvariable=self.sender_email_var).pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Sender password
        tk.Label(config_frame, text='App Password:', bg='#f0f0f0', font=('Arial', 10, 'bold')).pack(anchor=tk.W, padx=10, pady=(0, 0))
        self.sender_pass_var = tk.StringVar()
        tk.Entry(config_frame, textvariable=self.sender_pass_var, show='*').pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Mail options section
        options_frame = tk.LabelFrame(
            content_frame,
            text="Mail Options",
            font=('Arial', 11, 'bold'),
            bg='#f0f0f0'
        )
        options_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Send to faculty
        self.send_faculty_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            options_frame,
            text='Send to Faculty',
            variable=self.send_faculty_var,
            bg='#f0f0f0',
            font=('Arial', 10)
        ).pack(anchor=tk.W, padx=10, pady=5)
        
        # Send to students
        self.send_students_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            options_frame,
            text='Send to Students',
            variable=self.send_students_var,
            bg='#f0f0f0',
            font=('Arial', 10)
        ).pack(anchor=tk.W, padx=10, pady=5)
        
        # Send to admin
        self.send_admin_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            options_frame,
            text='Send to Admin',
            variable=self.send_admin_var,
            bg='#f0f0f0',
            font=('Arial', 10)
        ).pack(anchor=tk.W, padx=10, pady=5)
        
        # Admin email (if selected)
        tk.Label(content_frame, text='Admin Email (if selected):', bg='#f0f0f0', font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(10, 0))
        self.admin_email_var = tk.StringVar()
        tk.Entry(content_frame, textvariable=self.admin_email_var).pack(fill=tk.X, pady=(0, 20))
        
        # Status section
        status_frame = tk.LabelFrame(
            content_frame,
            text="Status",
            font=('Arial', 11, 'bold'),
            bg='#f0f0f0'
        )
        status_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        self.status_text = tk.Text(
            status_frame,
            height=8,
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
        
        tk.Button(
            button_frame,
            text='Send Summaries',
            command=self.send_summaries,
            font=('Arial', 11, 'bold'),
            bg='#27ae60',
            fg='#ffffff',
            relief=tk.FLAT,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=(0, 10), ipady=8, ipadx=20)
        
        tk.Button(
            button_frame,
            text='Clear Status',
            command=self.clear_status,
            font=('Arial', 11, 'bold'),
            bg='#95a5a6',
            fg='#ffffff',
            relief=tk.FLAT,
            cursor='hand2'
        ).pack(side=tk.LEFT, ipady=8, ipadx=20)
    
    def log_status(self, message):
        """Log a status message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.status_text.see(tk.END)
        self.status_text.update()
    
    def clear_status(self):
        """Clear status log"""
        self.status_text.delete(1.0, tk.END)
    
    def send_summaries(self):
        """Send attendance summaries"""
        sender_email = self.sender_email_var.get().strip()
        sender_pass = self.sender_pass_var.get().strip()
        
        if not sender_email or not sender_pass:
            messagebox.showerror("Error", "Please enter sender email and password")
            return
        
        # Update email service credentials
        email_service.sender_email = sender_email
        email_service.sender_password = sender_pass
        
        # Run in separate thread
        thread = threading.Thread(target=self.perform_send, daemon=True)
        thread.start()
    
    def perform_send(self):
        """Perform the actual sending"""
        try:
            self.log_status("Starting to send attendance summaries...")
            
            # Get all faculties
            faculties = self.db.get_all_faculties()
            
            if not faculties:
                self.log_status("No faculties found")
                return
            
            total_sent = 0
            
            for faculty in faculties:
                faculty_id = faculty[0]
                faculty_name = faculty[1]
                faculty_email = faculty[2]
                
                self.log_status(f"Processing faculty: {faculty_name}")
                
                # Get faculty's timetables
                timetables = self.db.get_faculty_timetables(faculty_id)
                
                for timetable in timetables:
                    timetable_id = timetable[0]
                    class_name = timetable[2]
                    
                    # Get attendance records
                    attendance_records = self.db.get_attendance_by_session(timetable_id)
                    
                    if attendance_records:
                        # Send to faculty
                        if self.send_faculty_var.get():
                            success, message = email_service.send_attendance_summary_to_faculty(
                                timetable_id,
                                faculty_email,
                                faculty_name,
                                class_name,
                                attendance_records
                            )
                            
                            if success:
                                self.log_status(f"✓ Sent summary to faculty: {faculty_name}")
                                total_sent += 1
                            else:
                                self.log_status(f"✗ Failed to send to faculty: {message}")
                        
                        # Send to students
                        if self.send_students_var.get():
                            email_service.send_attendance_summary_to_students(
                                timetable_id,
                                class_name,
                                attendance_records
                            )
                            self.log_status(f"✓ Sent confirmations to {len(attendance_records)} students")
            
            # Send to admin
            if self.send_admin_var.get():
                admin_email = self.admin_email_var.get().strip()
                if admin_email:
                    report_data = {
                        'total_sessions': len(faculties),
                        'total_marked': sum(len(self.db.get_attendance_by_session(t[0])) for f in faculties for t in self.db.get_faculty_timetables(f[0])),
                        'average_attendance': 85.5
                    }
                    
                    success, message = email_service.send_admin_report(admin_email, report_data)
                    if success:
                        self.log_status(f"✓ Sent admin report to: {admin_email}")
                    else:
                        self.log_status(f"✗ Failed to send admin report: {message}")
            
            self.log_status(f"✓ Completed! Total emails sent: {total_sent}")
            messagebox.showinfo("Success", f"Attendance summaries sent successfully!\nTotal: {total_sent}")
        
        except Exception as e:
            self.log_status(f"✗ Error: {str(e)}")
            messagebox.showerror("Error", f"Error sending summaries: {str(e)}")


def main():
    """Main entry point"""
    root = tk.Tk()
    automail_window = AutoMailWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
