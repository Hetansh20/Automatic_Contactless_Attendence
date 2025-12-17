import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from database import Database
import os

class EmailService:
    """Email service for sending attendance summaries"""
    
    def __init__(self, smtp_server="smtp.gmail.com", smtp_port=587):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = os.getenv("SENDER_EMAIL", "your-email@gmail.com")
        self.sender_password = os.getenv("SENDER_PASSWORD", "your-app-password")
        self.db = Database()
    
    def send_email(self, recipient_email, subject, body, html_body=None):
        """Send an email"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.sender_email
            msg['To'] = recipient_email
            
            # Attach plain text version
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach HTML version if provided
            if html_body:
                msg.attach(MIMEText(html_body, 'html'))
            
            # Connect to SMTP server and send
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            return True, "Email sent successfully"
        except Exception as e:
            return False, f"Error sending email: {str(e)}"
    
    def generate_attendance_summary_html(self, session_id, faculty_name, class_name, attendance_records):
        """Generate HTML email body for attendance summary"""
        total_students = len(attendance_records)
        present_students = len(set([r[1] for r in attendance_records]))
        absent_students = total_students - present_students
        attendance_percentage = (present_students / total_students * 100) if total_students > 0 else 0
        
        # Build student list HTML
        student_rows = ""
        for record in attendance_records:
            student_rows += f"""
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{record[2]}</td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{record[3]}</td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd; color: #27ae60;">Present</td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{record[4]}</td>
            </tr>
            """
        
        html_body = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; color: #333; }}
                    .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
                    .header {{ background-color: #2c3e50; color: white; padding: 20px; border-radius: 5px; }}
                    .content {{ margin: 20px 0; }}
                    .stats {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; margin: 20px 0; }}
                    .stat-box {{ background-color: #ecf0f1; padding: 15px; border-radius: 5px; text-align: center; }}
                    .stat-number {{ font-size: 24px; font-weight: bold; color: #2c3e50; }}
                    .stat-label {{ color: #7f8c8d; font-size: 12px; }}
                    table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                    th {{ background-color: #3498db; color: white; padding: 10px; text-align: left; }}
                    .footer {{ background-color: #ecf0f1; padding: 15px; border-radius: 5px; text-align: center; color: #7f8c8d; font-size: 12px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Attendance Summary Report</h1>
                        <p>Session ID: {session_id}</p>
                    </div>
                    
                    <div class="content">
                        <h2>Class Information</h2>
                        <p><strong>Faculty:</strong> {faculty_name}</p>
                        <p><strong>Class:</strong> {class_name}</p>
                        <p><strong>Date & Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    </div>
                    
                    <div class="stats">
                        <div class="stat-box">
                            <div class="stat-number">{total_students}</div>
                            <div class="stat-label">Total Students</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-number">{present_students}</div>
                            <div class="stat-label">Present</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-number">{absent_students}</div>
                            <div class="stat-label">Absent</div>
                        </div>
                    </div>
                    
                    <div class="content">
                        <h3>Attendance Percentage: {attendance_percentage:.2f}%</h3>
                    </div>
                    
                    <div class="content">
                        <h2>Attendance Details</h2>
                        <table>
                            <thead>
                                <tr>
                                    <th>Student Name</th>
                                    <th>Email</th>
                                    <th>Status</th>
                                    <th>Time</th>
                                </tr>
                            </thead>
                            <tbody>
                                {student_rows}
                            </tbody>
                        </table>
                    </div>
                    
                    <div class="footer">
                        <p>This is an automated email from the Contactless Attendance System.</p>
                        <p>Please do not reply to this email.</p>
                    </div>
                </div>
            </body>
        </html>
        """
        
        return html_body
    
    def send_attendance_summary_to_faculty(self, session_id, faculty_email, faculty_name, class_name, attendance_records):
        """Send attendance summary to faculty"""
        try:
            html_body = self.generate_attendance_summary_html(session_id, faculty_name, class_name, attendance_records)
            
            plain_body = f"""
Attendance Summary Report
Session ID: {session_id}

Faculty: {faculty_name}
Class: {class_name}
Date & Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Total Students: {len(attendance_records)}
Present: {len(set([r[1] for r in attendance_records]))}
Absent: {len(attendance_records) - len(set([r[1] for r in attendance_records]))}

Attendance Details:
{chr(10).join([f"- {r[2]} ({r[3]}): Present at {r[4]}" for r in attendance_records])}

This is an automated email from the Contactless Attendance System.
            """
            
            subject = f"Attendance Summary - {class_name} - {datetime.now().strftime('%Y-%m-%d')}"
            
            return self.send_email(faculty_email, subject, plain_body, html_body)
        except Exception as e:
            return False, f"Error sending faculty summary: {str(e)}"
    
    def send_attendance_summary_to_students(self, session_id, class_name, attendance_records):
        """Send attendance confirmation to students"""
        try:
            for record in attendance_records:
                student_email = record[3]
                student_name = record[2]
                
                plain_body = f"""
Dear {student_name},

Your attendance has been marked for the class: {class_name}

Date & Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Status: Present

If you believe this is incorrect, please contact your faculty member.

Best regards,
Attendance System
                """
                
                html_body = f"""
                <html>
                    <body style="font-family: Arial, sans-serif;">
                        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                            <h2>Attendance Confirmation</h2>
                            <p>Dear {student_name},</p>
                            <p>Your attendance has been marked for the class: <strong>{class_name}</strong></p>
                            <p><strong>Date & Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                            <p><strong>Status:</strong> <span style="color: #27ae60;">Present</span></p>
                            <p>If you believe this is incorrect, please contact your faculty member.</p>
                            <p>Best regards,<br>Attendance System</p>
                        </div>
                    </body>
                </html>
                """
                
                subject = f"Attendance Confirmation - {class_name}"
                self.send_email(student_email, subject, plain_body, html_body)
        except Exception as e:
            return False, f"Error sending student confirmations: {str(e)}"
    
    def send_admin_report(self, admin_email, report_data):
        """Send daily admin report"""
        try:
            plain_body = f"""
Daily Attendance Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Total Sessions: {report_data.get('total_sessions', 0)}
Total Students Marked: {report_data.get('total_marked', 0)}
Average Attendance: {report_data.get('average_attendance', 0):.2f}%

This is an automated report from the Attendance System.
            """
            
            subject = f"Daily Attendance Report - {datetime.now().strftime('%Y-%m-%d')}"
            
            return self.send_email(admin_email, subject, plain_body)
        except Exception as e:
            return False, f"Error sending admin report: {str(e)}"

# Initialize email service
email_service = EmailService()
