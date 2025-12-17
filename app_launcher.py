import tkinter as tk
from tkinter import messagebox
import os
import sys
import threading
from database import Database

class AppLauncher:
    """Main application launcher with database initialization"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Contactless Attendance System - Launcher")
        self.root.geometry("600x750")
        self.root.resizable(False, False)
        
        # Configure style
        self.root.configure(bg='#2c3e50')
        
        # Initialize database
        self.init_database()
        
        self.setup_ui()
    
    def init_database(self):
        """Initialize the database if it doesn't exist"""
        try:
            db = Database()
            messagebox.showinfo("Success", "Database initialized successfully!")
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to initialize database: {str(e)}")
            sys.exit(1)
    
    def setup_ui(self):
        """Setup the launcher UI"""
        # Header frame
        header_frame = tk.Frame(self.root, bg='#34495e', height=100)
        header_frame.pack(fill=tk.X)
        
        title_label = tk.Label(
            header_frame,
            text="Contactless Attendance System",
            font=('Arial', 28, 'bold'),
            bg='#34495e',
            fg='#ecf0f1'
        )
        title_label.pack(pady=(20, 5))
        
        subtitle_label = tk.Label(
            header_frame,
            text="Select an option to get started",
            font=('Arial', 12),
            bg='#34495e',
            fg='#bdc3c7'
        )
        subtitle_label.pack(pady=(0, 20))
        
        # Main content frame
        content_frame = tk.Frame(self.root, bg='#2c3e50')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=40)
        
        # Faculty Login button
        faculty_btn = tk.Button(
            content_frame,
            text='👤 Faculty Login',
            command=self.launch_faculty_login,
            font=('Arial', 14, 'bold'),
            bg='#3498db',
            fg='#ffffff',
            relief=tk.FLAT,
            bd=0,
            cursor='hand2',
            activebackground='#2980b9',
            activeforeground='#ffffff',
            height=3
        )
        faculty_btn.pack(fill=tk.X, pady=10)
        
        faculty_desc = tk.Label(
            content_frame,
            text="Start attendance session with face recognition",
            font=('Arial', 9),
            bg='#2c3e50',
            fg='#bdc3c7'
        )
        faculty_desc.pack(anchor=tk.W, padx=10)
        
        # Admin Dashboard button
        admin_btn = tk.Button(
            content_frame,
            text='⚙️ Admin Dashboard',
            command=self.launch_admin_dashboard,
            font=('Arial', 14, 'bold'),
            bg='#e74c3c',
            fg='#ffffff',
            relief=tk.FLAT,
            bd=0,
            cursor='hand2',
            activebackground='#c0392b',
            activeforeground='#ffffff',
            height=3
        )
        admin_btn.pack(fill=tk.X, pady=(30, 10))
        
        admin_desc = tk.Label(
            content_frame,
            text="Manage faculties, students, timetables, and view reports",
            font=('Arial', 9),
            bg='#2c3e50',
            fg='#bdc3c7'
        )
        admin_desc.pack(anchor=tk.W, padx=10)
        
        # Recognition Client button
        recognition_btn = tk.Button(
            content_frame,
            text='📷 Recognition Client',
            command=self.launch_recognition_client,
            font=('Arial', 14, 'bold'),
            bg='#27ae60',
            fg='#ffffff',
            relief=tk.FLAT,
            bd=0,
            cursor='hand2',
            activebackground='#229954',
            activeforeground='#ffffff',
            height=3
        )
        recognition_btn.pack(fill=tk.X, pady=(30, 10))
        
        recognition_desc = tk.Label(
            content_frame,
            text="Capture faces and train recognition model",
            font=('Arial', 9),
            bg='#2c3e50',
            fg='#bdc3c7'
        )
        recognition_desc.pack(anchor=tk.W, padx=10)
        
        # Setup & Configuration button
        setup_btn = tk.Button(
            content_frame,
            text='🔧 Setup & Configuration',
            command=self.launch_setup,
            font=('Arial', 14, 'bold'),
            bg='#f39c12',
            fg='#ffffff',
            relief=tk.FLAT,
            bd=0,
            cursor='hand2',
            activebackground='#d68910',
            activeforeground='#ffffff',
            height=3
        )
        setup_btn.pack(fill=tk.X, pady=(30, 10))
        
        setup_desc = tk.Label(
            content_frame,
            text="Register faculties, students, and manage timetables",
            font=('Arial', 9),
            bg='#2c3e50',
            fg='#bdc3c7'
        )
        setup_desc.pack(anchor=tk.W, padx=10)
        
        # Footer frame
        footer_frame = tk.Frame(self.root, bg='#34495e', height=50)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        footer_label = tk.Label(
            footer_frame,
            text="Version 2.0 | Secure Face Recognition Attendance System",
            font=('Arial', 9),
            bg='#34495e',
            fg='#95a5a6'
        )
        footer_label.pack(pady=15)
    
    def launch_faculty_login(self):
        """Launch faculty login interface"""
        try:
            from faculty_login import FacultyLoginWindow
            
            # Create new window
            login_root = tk.Toplevel(self.root)
            login_window = FacultyLoginWindow(login_root)
            
            # Hide launcher
            self.root.withdraw()
            
            # Show launcher when login window closes
            def on_login_close():
                self.root.deiconify()
            
            login_root.protocol("WM_DELETE_WINDOW", on_login_close)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch Faculty Login: {str(e)}")
    
    def launch_admin_dashboard(self):
        """Launch admin dashboard"""
        try:
            from admin_dashboard import AdminDashboard
            
            # Create new window
            dashboard_root = tk.Toplevel(self.root)
            dashboard = AdminDashboard(dashboard_root)
            
            # Hide launcher
            self.root.withdraw()
            
            # Show launcher when dashboard closes
            def on_dashboard_close():
                self.root.deiconify()
            
            dashboard_root.protocol("WM_DELETE_WINDOW", on_dashboard_close)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch Admin Dashboard: {str(e)}")
    
    def launch_recognition_client(self):
        """Launch recognition client for face capture and training"""
        try:
            from recognition_client import FaceCaptureTool
            
            # Create new window
            client_root = tk.Toplevel(self.root)
            client = FaceCaptureTool(client_root)
            
            # Hide launcher
            self.root.withdraw()
            
            # Show launcher when client closes
            def on_client_close():
                self.root.deiconify()
            
            client_root.protocol("WM_DELETE_WINDOW", on_client_close)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch Recognition Client: {str(e)}")
    
    def launch_setup(self):
        """Launch setup and configuration window"""
        try:
            from faculty_login import AdminSetupWindow
            
            # Create new window
            setup_root = tk.Toplevel(self.root)
            setup_window = AdminSetupWindow(setup_root)
            
            # Hide launcher
            self.root.withdraw()
            
            # Show launcher when setup closes
            def on_setup_close():
                self.root.deiconify()
            
            setup_root.protocol("WM_DELETE_WINDOW", on_setup_close)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch Setup: {str(e)}")


def main():
    """Main entry point for the application"""
    root = tk.Tk()
    launcher = AppLauncher(root)
    root.mainloop()


if __name__ == "__main__":
    main()
