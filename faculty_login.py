import tkinter as tk
from tkinter import messagebox, ttk
import threading
from auth import auth_manager
from database import Database

class FacultyLoginWindow:
    """Faculty login interface for the attendance system"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Contactless Attendance System - Faculty Login")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        # Configure style
        self.root.configure(bg='#f0f0f0')
        
        self.db = Database()
        self.session_token = None
        self.faculty_data = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the login UI"""
        # Header frame
        header_frame = tk.Frame(self.root, bg='#2c3e50', height=80)
        header_frame.pack(fill=tk.X)
        
        title_label = tk.Label(
            header_frame,
            text="Faculty Login",
            font=('Arial', 24, 'bold'),
            bg='#2c3e50',
            fg='#ffffff'
        )
        title_label.pack(pady=20)
        
        subtitle_label = tk.Label(
            header_frame,
            text="Enter your credentials to start attendance session",
            font=('Arial', 10),
            bg='#2c3e50',
            fg='#ecf0f1'
        )
        subtitle_label.pack()
        
        # Main content frame
        content_frame = tk.Frame(self.root, bg='#f0f0f0')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        # Email label and entry
        email_label = tk.Label(
            content_frame,
            text='Email Address:',
            font=('Arial', 11, 'bold'),
            bg='#f0f0f0',
            fg='#2c3e50'
        )
        email_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.email_var = tk.StringVar()
        email_entry = tk.Entry(
            content_frame,
            textvariable=self.email_var,
            font=('Arial', 11),
            bg='#ffffff',
            fg='#2c3e50',
            relief=tk.FLAT,
            bd=1
        )
        email_entry.pack(fill=tk.X, pady=(0, 20), ipady=8)
        
        # Passcode label and entry
        passcode_label = tk.Label(
            content_frame,
            text='Passcode:',
            font=('Arial', 11, 'bold'),
            bg='#f0f0f0',
            fg='#2c3e50'
        )
        passcode_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.passcode_var = tk.StringVar()
        passcode_entry = tk.Entry(
            content_frame,
            textvariable=self.passcode_var,
            font=('Arial', 11),
            bg='#ffffff',
            fg='#2c3e50',
            relief=tk.FLAT,
            bd=1,
            show='*'
        )
        passcode_entry.pack(fill=tk.X, pady=(0, 30), ipady=8)
        
        # Login button
        login_btn = tk.Button(
            content_frame,
            text='LOGIN',
            command=self.handle_login,
            font=('Arial', 12, 'bold'),
            bg='#3498db',
            fg='#ffffff',
            relief=tk.FLAT,
            bd=0,
            cursor='hand2',
            activebackground='#2980b9',
            activeforeground='#ffffff'
        )
        login_btn.pack(fill=tk.X, ipady=10)
        
        # Status label
        self.status_var = tk.StringVar()
        status_label = tk.Label(
            content_frame,
            textvariable=self.status_var,
            font=('Arial', 9),
            bg='#f0f0f0',
            fg='#e74c3c'
        )
        status_label.pack(pady=(20, 0))
        
        # Admin button at bottom
        admin_frame = tk.Frame(self.root, bg='#f0f0f0')
        admin_frame.pack(fill=tk.X, padx=30, pady=(0, 20))
        
        admin_btn = tk.Button(
            admin_frame,
            text='Admin Panel',
            command=self.open_admin_panel,
            font=('Arial', 9),
            bg='#95a5a6',
            fg='#ffffff',
            relief=tk.FLAT,
            bd=0,
            cursor='hand2'
        )
        admin_btn.pack(side=tk.LEFT)
    
    def handle_login(self):
        """Handle faculty login"""
        email = self.email_var.get().strip()
        passcode = self.passcode_var.get().strip()
        
        if not email or not passcode:
            self.status_var.set("Please enter both email and passcode")
            return
        
        # Run login in a separate thread to prevent UI freezing
        thread = threading.Thread(target=self.perform_login, args=(email, passcode))
        thread.daemon = True
        thread.start()
    
    def perform_login(self, email, passcode):
        """Perform the actual login"""
        try:
            session_token, message = auth_manager.faculty_login(email, passcode)
            
            if session_token:
                self.session_token = session_token
                session_data, _ = auth_manager.verify_session(session_token)
                self.faculty_data = session_data
                
                # Clear fields
                self.email_var.set("")
                self.passcode_var.set("")
                self.status_var.set("")
                
                # Open main attendance window
                self.root.after(0, self.open_attendance_window)
            else:
                self.status_var.set(message)
        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")
    
    def open_attendance_window(self):
        """Open the main attendance window after successful login"""
        # Hide login window
        self.root.withdraw()
        
        # Import here to avoid circular imports
        from attendance_client import AttendanceClientWindow
        
        # Create new window for attendance
        attendance_root = tk.Toplevel(self.root)
        attendance_window = AttendanceClientWindow(
            attendance_root,
            self.session_token,
            self.faculty_data,
            self.on_logout
        )
    
    def on_logout(self):
        """Handle logout from attendance window"""
        auth_manager.logout(self.session_token)
        self.session_token = None
        self.faculty_data = None
        
        # Show login window again
        self.root.deiconify()
        self.email_var.set("")
        self.passcode_var.set("")
        self.status_var.set("Logged out successfully")
    
    def open_admin_panel(self):
        """Open admin panel for system management"""
        messagebox.showinfo(
            "Admin Panel",
            "Admin panel will be available in the next update.\n\n"
            "For now, use the admin dashboard web interface."
        )


class AdminSetupWindow:
    """Admin setup window for registering faculties and students"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Contactless Attendance System - Admin Setup")
        self.root.geometry("600x700")
        
        self.db = Database()
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the admin UI"""
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Faculty registration tab
        faculty_frame = ttk.Frame(notebook)
        notebook.add(faculty_frame, text="Register Faculty")
        self.setup_faculty_tab(faculty_frame)
        
        # Student registration tab
        student_frame = ttk.Frame(notebook)
        notebook.add(student_frame, text="Register Student")
        self.setup_student_tab(student_frame)
        
        # Timetable tab
        timetable_frame = ttk.Frame(notebook)
        notebook.add(timetable_frame, text="Manage Timetable")
        self.setup_timetable_tab(timetable_frame)
    
    def setup_faculty_tab(self, parent):
        """Setup faculty registration tab"""
        frame = tk.Frame(parent, bg='#f0f0f0')
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Faculty name
        tk.Label(frame, text='Faculty Name:', bg='#f0f0f0', font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        self.faculty_name_var = tk.StringVar()
        tk.Entry(frame, textvariable=self.faculty_name_var, font=('Arial', 10)).pack(fill=tk.X, pady=(0, 15), ipady=5)
        
        # Faculty email
        tk.Label(frame, text='Email:', bg='#f0f0f0', font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        self.faculty_email_var = tk.StringVar()
        tk.Entry(frame, textvariable=self.faculty_email_var, font=('Arial', 10)).pack(fill=tk.X, pady=(0, 15), ipady=5)
        
        # Department
        tk.Label(frame, text='Department:', bg='#f0f0f0', font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        self.faculty_dept_var = tk.StringVar()
        tk.Entry(frame, textvariable=self.faculty_dept_var, font=('Arial', 10)).pack(fill=tk.X, pady=(0, 15), ipady=5)
        
        # Passcode
        tk.Label(frame, text='Passcode:', bg='#f0f0f0', font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        self.faculty_pass_var = tk.StringVar()
        tk.Entry(frame, textvariable=self.faculty_pass_var, font=('Arial', 10), show='*').pack(fill=tk.X, pady=(0, 20), ipady=5)
        
        # Register button
        tk.Button(
            frame,
            text='Register Faculty',
            command=self.register_faculty,
            bg='#27ae60',
            fg='#ffffff',
            font=('Arial', 11, 'bold'),
            relief=tk.FLAT,
            cursor='hand2'
        ).pack(fill=tk.X, ipady=8)
        
        # Status label
        self.faculty_status_var = tk.StringVar()
        tk.Label(frame, textvariable=self.faculty_status_var, bg='#f0f0f0', font=('Arial', 9), fg='#e74c3c').pack(pady=(10, 0))
    
    def setup_student_tab(self, parent):
        """Setup student registration tab"""
        frame = tk.Frame(parent, bg='#f0f0f0')
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Student ID
        tk.Label(frame, text='Student ID:', bg='#f0f0f0', font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        self.student_id_var = tk.StringVar()
        tk.Entry(frame, textvariable=self.student_id_var, font=('Arial', 10)).pack(fill=tk.X, pady=(0, 15), ipady=5)
        
        # Student name
        tk.Label(frame, text='Student Name:', bg='#f0f0f0', font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        self.student_name_var = tk.StringVar()
        tk.Entry(frame, textvariable=self.student_name_var, font=('Arial', 10)).pack(fill=tk.X, pady=(0, 15), ipady=5)
        
        # Student email
        tk.Label(frame, text='Email:', bg='#f0f0f0', font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        self.student_email_var = tk.StringVar()
        tk.Entry(frame, textvariable=self.student_email_var, font=('Arial', 10)).pack(fill=tk.X, pady=(0, 15), ipady=5)
        
        # Department
        tk.Label(frame, text='Department:', bg='#f0f0f0', font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        self.student_dept_var = tk.StringVar()
        tk.Entry(frame, textvariable=self.student_dept_var, font=('Arial', 10)).pack(fill=tk.X, pady=(0, 20), ipady=5)
        
        # Register button
        tk.Button(
            frame,
            text='Register Student',
            command=self.register_student,
            bg='#27ae60',
            fg='#ffffff',
            font=('Arial', 11, 'bold'),
            relief=tk.FLAT,
            cursor='hand2'
        ).pack(fill=tk.X, ipady=8)
        
        # Status label
        self.student_status_var = tk.StringVar()
        tk.Label(frame, textvariable=self.student_status_var, bg='#f0f0f0', font=('Arial', 9), fg='#e74c3c').pack(pady=(10, 0))
    
    def setup_timetable_tab(self, parent):
        """Setup timetable management tab"""
        frame = tk.Frame(parent, bg='#f0f0f0')
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        tk.Label(frame, text='Timetable management will be available in the dashboard.', bg='#f0f0f0', font=('Arial', 10)).pack(pady=20)
    
    def register_faculty(self):
        """Register a new faculty"""
        name = self.faculty_name_var.get().strip()
        email = self.faculty_email_var.get().strip()
        department = self.faculty_dept_var.get().strip()
        passcode = self.faculty_pass_var.get().strip()
        
        if not all([name, email, department, passcode]):
            self.faculty_status_var.set("Please fill all fields")
            return
        
        try:
            self.db.add_faculty(name, email, department, passcode)
            self.faculty_status_var.set(f"✓ Faculty '{name}' registered successfully!")
            self.faculty_name_var.set("")
            self.faculty_email_var.set("")
            self.faculty_dept_var.set("")
            self.faculty_pass_var.set("")
        except Exception as e:
            self.faculty_status_var.set(f"Error: {str(e)}")
    
    def register_student(self):
        """Register a new student"""
        student_id = self.student_id_var.get().strip()
        name = self.student_name_var.get().strip()
        email = self.student_email_var.get().strip()
        department = self.student_dept_var.get().strip()
        
        if not all([student_id, name, email, department]):
            self.student_status_var.set("Please fill all fields")
            return
        
        try:
            self.db.add_student(student_id, name, email, department)
            self.student_status_var.set(f"✓ Student '{name}' registered successfully!")
            self.student_id_var.set("")
            self.student_name_var.set("")
            self.student_email_var.set("")
            self.student_dept_var.set("")
        except Exception as e:
            self.student_status_var.set(f"Error: {str(e)}")


def main():
    """Main entry point"""
    root = tk.Tk()
    login_window = FacultyLoginWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
