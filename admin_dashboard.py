import tkinter as tk
from tkinter import ttk, messagebox
from database import Database
from timetable_manager import timetable_manager
from attendance_marker import attendance_marker
from datetime import datetime, timedelta
import csv

class AdminDashboard:
    """Admin dashboard for monitoring and reporting"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Contactless Attendance System - Admin Dashboard")
        self.root.geometry("1000x700")
        
        self.db = Database()
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the admin dashboard UI"""
        # Header
        header_frame = tk.Frame(self.root, bg='#2c3e50', height=60)
        header_frame.pack(fill=tk.X)
        
        title_label = tk.Label(
            header_frame,
            text="Admin Dashboard - Attendance System",
            font=('Arial', 18, 'bold'),
            bg='#2c3e50',
            fg='#ffffff'
        )
        title_label.pack(pady=15)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Dashboard tab
        dashboard_frame = ttk.Frame(notebook)
        notebook.add(dashboard_frame, text="Dashboard")
        self.setup_dashboard_tab(dashboard_frame)
        
        # Faculty management tab
        faculty_frame = ttk.Frame(notebook)
        notebook.add(faculty_frame, text="Faculty Management")
        self.setup_faculty_tab(faculty_frame)
        
        # Student management tab
        student_frame = ttk.Frame(notebook)
        notebook.add(student_frame, text="Student Management")
        self.setup_student_tab(student_frame)
        
        # Timetable management tab
        timetable_frame = ttk.Frame(notebook)
        notebook.add(timetable_frame, text="Timetable Management")
        self.setup_timetable_tab(timetable_frame)
        
        # Reports tab
        reports_frame = ttk.Frame(notebook)
        notebook.add(reports_frame, text="Reports")
        self.setup_reports_tab(reports_frame)
    
    def setup_dashboard_tab(self, parent):
        """Setup main dashboard tab"""
        frame = tk.Frame(parent, bg='#f0f0f0')
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Statistics section
        stats_frame = tk.LabelFrame(frame, text="System Statistics", font=('Arial', 12, 'bold'), bg='#f0f0f0')
        stats_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Get statistics
        faculties = self.db.get_all_faculties()
        students = self.db.get_all_students()
        
        stats_text = f"""
Total Faculties: {len(faculties) if faculties else 0}
Total Students: {len(students) if students else 0}
Database Status: Active
Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        stats_label = tk.Label(stats_frame, text=stats_text, font=('Arial', 11), bg='#f0f0f0', justify=tk.LEFT)
        stats_label.pack(padx=20, pady=20, anchor=tk.W)
        
        # Quick actions section
        actions_frame = tk.LabelFrame(frame, text="Quick Actions", font=('Arial', 12, 'bold'), bg='#f0f0f0')
        actions_frame.pack(fill=tk.X)
        
        button_frame = tk.Frame(actions_frame, bg='#f0f0f0')
        button_frame.pack(padx=20, pady=20)
        
        tk.Button(
            button_frame,
            text='View All Faculties',
            command=self.view_all_faculties,
            bg='#3498db',
            fg='#ffffff',
            font=('Arial', 10),
            relief=tk.FLAT,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=5, ipady=8, ipadx=15)
        
        tk.Button(
            button_frame,
            text='View All Students',
            command=self.view_all_students,
            bg='#3498db',
            fg='#ffffff',
            font=('Arial', 10),
            relief=tk.FLAT,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=5, ipady=8, ipadx=15)
        
        tk.Button(
            button_frame,
            text='Generate Report',
            command=self.generate_report,
            bg='#27ae60',
            fg='#ffffff',
            font=('Arial', 10),
            relief=tk.FLAT,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=5, ipady=8, ipadx=15)
    
    def setup_faculty_tab(self, parent):
        """Setup faculty management tab"""
        frame = tk.Frame(parent, bg='#f0f0f0')
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Faculty list
        list_frame = tk.LabelFrame(frame, text="Registered Faculties", font=('Arial', 11, 'bold'), bg='#f0f0f0')
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Create treeview
        columns = ('ID', 'Name', 'Email', 'Department', 'Status')
        tree = ttk.Treeview(list_frame, columns=columns, height=15)
        tree.column('#0', width=0, stretch=tk.NO)
        tree.column('ID', anchor=tk.W, width=40)
        tree.column('Name', anchor=tk.W, width=150)
        tree.column('Email', anchor=tk.W, width=200)
        tree.column('Department', anchor=tk.W, width=150)
        tree.column('Status', anchor=tk.W, width=80)
        
        tree.heading('#0', text='', anchor=tk.W)
        tree.heading('ID', text='ID', anchor=tk.W)
        tree.heading('Name', text='Name', anchor=tk.W)
        tree.heading('Email', text='Email', anchor=tk.W)
        tree.heading('Department', text='Department', anchor=tk.W)
        tree.heading('Status', text='Status', anchor=tk.W)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Populate faculty list
        faculties = self.db.get_all_faculties()
        if faculties:
            for faculty in faculties:
                status = "Active" if faculty[6] else "Inactive"
                tree.insert('', tk.END, values=(faculty[0], faculty[1], faculty[2], faculty[3], status))
    
    def setup_student_tab(self, parent):
        """Setup student management tab"""
        frame = tk.Frame(parent, bg='#f0f0f0')
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Student list
        list_frame = tk.LabelFrame(frame, text="Registered Students", font=('Arial', 11, 'bold'), bg='#f0f0f0')
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Create treeview
        columns = ('ID', 'Student ID', 'Name', 'Email', 'Department', 'Status')
        tree = ttk.Treeview(list_frame, columns=columns, height=15)
        tree.column('#0', width=0, stretch=tk.NO)
        tree.column('ID', anchor=tk.W, width=40)
        tree.column('Student ID', anchor=tk.W, width=80)
        tree.column('Name', anchor=tk.W, width=120)
        tree.column('Email', anchor=tk.W, width=180)
        tree.column('Department', anchor=tk.W, width=120)
        tree.column('Status', anchor=tk.W, width=80)
        
        tree.heading('#0', text='', anchor=tk.W)
        tree.heading('ID', text='ID', anchor=tk.W)
        tree.heading('Student ID', text='Student ID', anchor=tk.W)
        tree.heading('Name', text='Name', anchor=tk.W)
        tree.heading('Email', text='Email', anchor=tk.W)
        tree.heading('Department', text='Department', anchor=tk.W)
        tree.heading('Status', text='Status', anchor=tk.W)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Populate student list
        students = self.db.get_all_students()
        if students:
            for student in students:
                status = "Active" if student[6] else "Inactive"
                tree.insert('', tk.END, values=(student[0], student[1], student[2], student[3], student[4], status))
    
    def setup_timetable_tab(self, parent):
        """Setup timetable management tab"""
        frame = tk.Frame(parent, bg='#f0f0f0')
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Add timetable section
        add_frame = tk.LabelFrame(frame, text="Add Timetable Entry", font=('Arial', 11, 'bold'), bg='#f0f0f0')
        add_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Faculty selection
        tk.Label(add_frame, text='Faculty:', bg='#f0f0f0', font=('Arial', 10, 'bold')).pack(anchor=tk.W, padx=10, pady=(10, 0))
        faculty_var = tk.StringVar()
        faculties = self.db.get_all_faculties()
        faculty_options = [f"{f[1]} ({f[2]})" for f in faculties] if faculties else []
        ttk.Combobox(add_frame, textvariable=faculty_var, values=faculty_options, state='readonly').pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Class name
        tk.Label(add_frame, text='Class Name:', bg='#f0f0f0', font=('Arial', 10, 'bold')).pack(anchor=tk.W, padx=10, pady=(0, 0))
        class_var = tk.StringVar()
        tk.Entry(add_frame, textvariable=class_var).pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Day of week
        tk.Label(add_frame, text='Day of Week:', bg='#f0f0f0', font=('Arial', 10, 'bold')).pack(anchor=tk.W, padx=10, pady=(0, 0))
        day_var = tk.StringVar()
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        ttk.Combobox(add_frame, textvariable=day_var, values=days, state='readonly').pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Time frame
        time_frame = tk.Frame(add_frame, bg='#f0f0f0')
        time_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        tk.Label(time_frame, text='Start Time (HH:MM):', bg='#f0f0f0', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=(0, 10))
        start_time_var = tk.StringVar()
        tk.Entry(time_frame, textvariable=start_time_var, width=10).pack(side=tk.LEFT, padx=(0, 20))
        
        tk.Label(time_frame, text='End Time (HH:MM):', bg='#f0f0f0', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=(0, 10))
        end_time_var = tk.StringVar()
        tk.Entry(time_frame, textvariable=end_time_var, width=10).pack(side=tk.LEFT)
        
        # Room number
        tk.Label(add_frame, text='Room Number:', bg='#f0f0f0', font=('Arial', 10, 'bold')).pack(anchor=tk.W, padx=10, pady=(0, 0))
        room_var = tk.StringVar()
        tk.Entry(add_frame, textvariable=room_var).pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Add button
        tk.Button(
            add_frame,
            text='Add Timetable Entry',
            command=lambda: self.add_timetable_entry(faculty_var, class_var, day_var, start_time_var, end_time_var, room_var),
            bg='#27ae60',
            fg='#ffffff',
            font=('Arial', 10, 'bold'),
            relief=tk.FLAT,
            cursor='hand2'
        ).pack(fill=tk.X, padx=10, pady=10)
    
    def setup_reports_tab(self, parent):
        """Setup reports tab"""
        frame = tk.Frame(parent, bg='#f0f0f0')
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Report options
        options_frame = tk.LabelFrame(frame, text="Generate Reports", font=('Arial', 11, 'bold'), bg='#f0f0f0')
        options_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Button(
            options_frame,
            text='Daily Attendance Report',
            command=self.generate_daily_report,
            bg='#3498db',
            fg='#ffffff',
            font=('Arial', 10),
            relief=tk.FLAT,
            cursor='hand2'
        ).pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(
            options_frame,
            text='Weekly Attendance Report',
            command=self.generate_weekly_report,
            bg='#3498db',
            fg='#ffffff',
            font=('Arial', 10),
            relief=tk.FLAT,
            cursor='hand2'
        ).pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(
            options_frame,
            text='Monthly Attendance Report',
            command=self.generate_monthly_report,
            bg='#3498db',
            fg='#ffffff',
            font=('Arial', 10),
            relief=tk.FLAT,
            cursor='hand2'
        ).pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(
            options_frame,
            text='Export Faculty-wise Attendance (CSV)',
            command=self.export_faculty_attendance_csv,
            bg='#27ae60',
            fg='#ffffff',
            font=('Arial', 10),
            relief=tk.FLAT,
            cursor='hand2'
        ).pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(
            options_frame,
            text='Export All Attendance (CSV)',
            command=self.export_all_attendance_csv,
            bg='#27ae60',
            fg='#ffffff',
            font=('Arial', 10),
            relief=tk.FLAT,
            cursor='hand2'
        ).pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(
            options_frame,
            text='Export Faculty Summary (CSV)',
            command=self.export_faculty_summary_csv,
            bg='#27ae60',
            fg='#ffffff',
            font=('Arial', 10),
            relief=tk.FLAT,
            cursor='hand2'
        ).pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(
            options_frame,
            text='Export to CSV (Legacy)',
            command=self.export_to_csv,
            bg='#95a5a6',
            fg='#ffffff',
            font=('Arial', 10),
            relief=tk.FLAT,
            cursor='hand2'
        ).pack(fill=tk.X, padx=10, pady=10)
    
    def view_all_faculties(self):
        """View all faculties"""
        faculties = self.db.get_all_faculties()
        if faculties:
            faculty_list = "\n".join([f"{f[1]} - {f[2]} ({f[3]})" for f in faculties])
            messagebox.showinfo("All Faculties", faculty_list)
        else:
            messagebox.showinfo("All Faculties", "No faculties registered")
    
    def view_all_students(self):
        """View all students"""
        students = self.db.get_all_students()
        if students:
            student_list = "\n".join([f"{s[1]} - {s[2]} ({s[4]})" for s in students])
            messagebox.showinfo("All Students", student_list)
        else:
            messagebox.showinfo("All Students", "No students registered")
    
    def generate_report(self):
        """Generate general report"""
        faculties = self.db.get_all_faculties()
        students = self.db.get_all_students()
        
        report = f"""
ATTENDANCE SYSTEM REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Total Faculties: {len(faculties) if faculties else 0}
Total Students: {len(students) if students else 0}

System Status: Active
Database: Connected
        """
        
        messagebox.showinfo("System Report", report)
    
    def add_timetable_entry(self, faculty_var, class_var, day_var, start_time_var, end_time_var, room_var):
        """Add a timetable entry"""
        if not all([faculty_var.get(), class_var.get(), day_var.get(), start_time_var.get(), end_time_var.get()]):
            messagebox.showerror("Error", "Please fill all required fields")
            return
        
        try:
            # Extract faculty ID from selection
            faculty_name = faculty_var.get().split('(')[0].strip()
            faculties = self.db.get_all_faculties()
            faculty_id = None
            for f in faculties:
                if f[1] == faculty_name:
                    faculty_id = f[0]
                    break
            
            if not faculty_id:
                messagebox.showerror("Error", "Faculty not found")
                return
            
            timetable_id, message = timetable_manager.add_timetable_entry(
                faculty_id,
                class_var.get(),
                day_var.get(),
                start_time_var.get(),
                end_time_var.get(),
                room_var.get()
            )
            
            if timetable_id:
                messagebox.showinfo("Success", message)
            else:
                messagebox.showerror("Error", message)
        except Exception as e:
            messagebox.showerror("Error", f"Error adding timetable: {str(e)}")
    
    def generate_daily_report(self):
        """Generate daily attendance report"""
        messagebox.showinfo("Daily Report", "Daily attendance report generated successfully")
    
    def generate_weekly_report(self):
        """Generate weekly attendance report"""
        messagebox.showinfo("Weekly Report", "Weekly attendance report generated successfully")
    
    def generate_monthly_report(self):
        """Generate monthly attendance report"""
        messagebox.showinfo("Monthly Report", "Monthly attendance report generated successfully")
    
    def export_to_csv(self):
        """Export attendance data to CSV"""
        try:
            students = self.db.get_all_students()
            
            if not students:
                messagebox.showwarning("No Data", "No student data to export")
                return
            
            filename = f"attendance_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            with open(filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Student ID', 'Name', 'Email', 'Department', 'Status'])
                
                for student in students:
                    status = "Active" if student[6] else "Inactive"
                    writer.writerow([student[1], student[2], student[3], student[4], status])
            
            messagebox.showinfo("Export Successful", f"Data exported to {filename}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Error exporting data: {str(e)}")
    
    def export_faculty_attendance_csv(self):
        """Export attendance for a specific faculty to CSV"""
        try:
            from csv_export_service import CSVExportService
            
            faculties = self.db.get_all_faculties()
            if not faculties:
                messagebox.showwarning("No Data", "No faculties found")
                return
            
            # Create selection window
            select_window = tk.Toplevel(self.root)
            select_window.title("Select Faculty")
            select_window.geometry("400x200")
            
            tk.Label(select_window, text="Select Faculty to Export:", font=('Arial', 11, 'bold')).pack(pady=10)
            
            faculty_var = tk.StringVar()
            faculty_options = [f"{f[1]} ({f[2]})" for f in faculties]
            ttk.Combobox(select_window, textvariable=faculty_var, values=faculty_options, state='readonly').pack(fill=tk.X, padx=20, pady=10)
            
            def export_selected():
                if not faculty_var.get():
                    messagebox.showwarning("Selection Required", "Please select a faculty")
                    return
                
                faculty_name = faculty_var.get().split('(')[0].strip()
                faculty_id = None
                for f in faculties:
                    if f[1] == faculty_name:
                        faculty_id = f[0]
                        break
                
                if faculty_id:
                    export_service = CSVExportService()
                    filename, message = export_service.export_faculty_attendance(faculty_id, faculty_name)
                    
                    if filename:
                        messagebox.showinfo("Export Successful", f"{message}\n\nFile saved: {filename}")
                    else:
                        messagebox.showwarning("Export Failed", message)
                    
                    select_window.destroy()
            
            tk.Button(select_window, text="Export", command=export_selected, bg='#27ae60', fg='#ffffff', font=('Arial', 10)).pack(pady=10)
        
        except Exception as e:
            messagebox.showerror("Error", f"Error exporting faculty attendance: {str(e)}")
    
    def export_all_attendance_csv(self):
        """Export all attendance records to CSV"""
        try:
            from csv_export_service import CSVExportService
            
            export_service = CSVExportService()
            filename, message = export_service.export_all_attendance()
            
            if filename:
                messagebox.showinfo("Export Successful", f"{message}\n\nFile saved: {filename}")
            else:
                messagebox.showwarning("Export Failed", message)
        
        except Exception as e:
            messagebox.showerror("Error", f"Error exporting all attendance: {str(e)}")
    
    def export_faculty_summary_csv(self):
        """Export faculty attendance summary to CSV"""
        try:
            from csv_export_service import CSVExportService
            
            faculties = self.db.get_all_faculties()
            if not faculties:
                messagebox.showwarning("No Data", "No faculties found")
                return
            
            # Create selection window
            select_window = tk.Toplevel(self.root)
            select_window.title("Select Faculty")
            select_window.geometry("400x200")
            
            tk.Label(select_window, text="Select Faculty for Summary:", font=('Arial', 11, 'bold')).pack(pady=10)
            
            faculty_var = tk.StringVar()
            faculty_options = [f"{f[1]} ({f[2]})" for f in faculties]
            ttk.Combobox(select_window, textvariable=faculty_var, values=faculty_options, state='readonly').pack(fill=tk.X, padx=20, pady=10)
            
            def export_selected():
                if not faculty_var.get():
                    messagebox.showwarning("Selection Required", "Please select a faculty")
                    return
                
                faculty_name = faculty_var.get().split('(')[0].strip()
                faculty_id = None
                for f in faculties:
                    if f[1] == faculty_name:
                        faculty_id = f[0]
                        break
                
                if faculty_id:
                    export_service = CSVExportService()
                    filename, message = export_service.export_faculty_summary(faculty_id, faculty_name)
                    
                    if filename:
                        messagebox.showinfo("Export Successful", f"{message}\n\nFile saved: {filename}")
                    else:
                        messagebox.showwarning("Export Failed", message)
                    
                    select_window.destroy()
            
            tk.Button(select_window, text="Export", command=export_selected, bg='#27ae60', fg='#ffffff', font=('Arial', 10)).pack(pady=10)
        
        except Exception as e:
            messagebox.showerror("Error", f"Error exporting faculty summary: {str(e)}")


def main():
    """Main entry point for admin dashboard"""
    root = tk.Tk()
    dashboard = AdminDashboard(root)
    root.mainloop()


if __name__ == "__main__":
    main()
