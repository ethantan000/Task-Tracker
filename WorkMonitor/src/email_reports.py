"""
Email Reports Module - Sends weekly activity reports via email
Generates and sends formatted HTML email reports with weekly statistics
"""

import smtplib
import schedule
import time
import threading
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta


class EmailReportSender:
    """Handles email report generation and sending"""

    def __init__(self, config, logger_class):
        self.config = config
        self.logger_class = logger_class
        self.scheduler_thread = None
        self.running = False

    def generate_weekly_report_html(self):
        """Generate HTML content for the weekly email report"""
        # Get the week summary (Monday to Sunday)
        today = datetime.now()
        start_of_week = today - timedelta(days=today.weekday())  # Monday
        end_of_week = start_of_week + timedelta(days=6)  # Sunday

        # If today is Friday, we want last Monday to last Sunday (completed week)
        if today.weekday() == 4:  # Friday
            # Get the previous completed week
            start_of_week = start_of_week - timedelta(days=7)
            end_of_week = start_of_week + timedelta(days=6)

        week_summary = self.logger_class.get_date_range_summary(start_of_week, end_of_week)

        # Format dates
        week_start_str = start_of_week.strftime("%B %d, %Y")
        week_end_str = end_of_week.strftime("%B %d, %Y")

        # Calculate productivity percentage
        total_hours = week_summary['work_hours']
        real_work_hours = week_summary['real_work_hours']
        productivity_pct = (real_work_hours / total_hours * 100) if total_hours > 0 else 0

        # Generate daily breakdown HTML
        daily_rows = ""
        for day in week_summary['daily_data']:
            if day['work_hours'] > 0:  # Only show days with activity
                daily_rows += f"""
                <tr>
                    <td style="padding: 12px; border-bottom: 1px solid #e0e0e0;">{day['day_name']}</td>
                    <td style="padding: 12px; border-bottom: 1px solid #e0e0e0;">{day['date']}</td>
                    <td style="padding: 12px; border-bottom: 1px solid #e0e0e0; color: #4CAF50; font-weight: bold;">{day['work_hours']:.1f}h</td>
                    <td style="padding: 12px; border-bottom: 1px solid #e0e0e0; color: #ff9800;">{day['idle_hours']:.1f}h</td>
                    <td style="padding: 12px; border-bottom: 1px solid #e0e0e0; color: #9c27b0;">{day['suspicious_hours']:.1f}h</td>
                    <td style="padding: 12px; border-bottom: 1px solid #e0e0e0;">{day['screenshots']}</td>
                </tr>
                """

        # Build the HTML email
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; background-color: #f5f5f5; margin: 0; padding: 20px; }}
        .container {{ max-width: 800px; margin: 0 auto; background-color: white; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px 10px 0 0; text-align: center; }}
        .header h1 {{ margin: 0; font-size: 28px; }}
        .header p {{ margin: 10px 0 0 0; opacity: 0.9; font-size: 16px; }}
        .content {{ padding: 30px; }}
        .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .metric-card {{ background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); border-radius: 10px; padding: 20px; text-align: center; }}
        .metric-card.primary {{ background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%); color: white; }}
        .metric-card.warning {{ background: linear-gradient(135deg, #ff9800 0%, #fb8c00 100%); color: white; }}
        .metric-card.danger {{ background: linear-gradient(135deg, #9c27b0 0%, #7b1fa2 100%); color: white; }}
        .metric-value {{ font-size: 36px; font-weight: bold; margin: 10px 0; }}
        .metric-label {{ font-size: 14px; text-transform: uppercase; letter-spacing: 1px; opacity: 0.9; }}
        .section {{ margin-bottom: 30px; }}
        .section h2 {{ color: #333; font-size: 20px; margin-bottom: 15px; padding-bottom: 10px; border-bottom: 2px solid #667eea; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
        th {{ background-color: #667eea; color: white; padding: 12px; text-align: left; font-weight: 600; }}
        .footer {{ background-color: #f5f5f5; padding: 20px; text-align: center; color: #666; font-size: 14px; border-radius: 0 0 10px 10px; }}
        .productivity-bar {{ background-color: #e0e0e0; height: 30px; border-radius: 15px; overflow: hidden; margin-top: 10px; }}
        .productivity-fill {{ background: linear-gradient(90deg, #4CAF50 0%, #8bc34a 100%); height: 100%; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; transition: width 0.3s; }}
        .highlight {{ background-color: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; border-radius: 5px; margin: 15px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Weekly Work Report</h1>
            <p>{week_start_str} - {week_end_str}</p>
        </div>

        <div class="content">
            <!-- Key Metrics -->
            <div class="metrics">
                <div class="metric-card primary">
                    <div class="metric-label">Total Work Hours</div>
                    <div class="metric-value">{week_summary['work_hours']:.1f}h</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Real Work Hours</div>
                    <div class="metric-value">{week_summary['real_work_hours']:.1f}h</div>
                </div>
                <div class="metric-card warning">
                    <div class="metric-label">Idle Hours</div>
                    <div class="metric-value">{week_summary['idle_hours']:.1f}h</div>
                </div>
                <div class="metric-card danger">
                    <div class="metric-label">Suspicious Hours</div>
                    <div class="metric-value">{week_summary['suspicious_hours']:.1f}h</div>
                </div>
            </div>

            <!-- Productivity Score -->
            <div class="section">
                <h2>📈 Productivity Score</h2>
                <div class="highlight">
                    <strong>Productivity Rate:</strong> {productivity_pct:.1f}%
                    <div class="productivity-bar">
                        <div class="productivity-fill" style="width: {min(productivity_pct, 100)}%;">
                            {productivity_pct:.1f}%
                        </div>
                    </div>
                </div>
            </div>

            <!-- Summary Stats -->
            <div class="section">
                <h2>📋 Week Summary</h2>
                <ul style="line-height: 2; color: #555;">
                    <li><strong>Days Worked:</strong> {week_summary['days_worked']} days</li>
                    <li><strong>Average Hours/Day:</strong> {week_summary['avg_work_per_day']:.1f} hours</li>
                    <li><strong>Total Screenshots:</strong> {week_summary['screenshot_count']} captures</li>
                    <li><strong>Overtime Hours:</strong> {week_summary['overtime_hours']:.1f} hours</li>
                </ul>
            </div>

            <!-- Daily Breakdown -->
            <div class="section">
                <h2>📅 Daily Breakdown</h2>
                {'<p style="color: #999; font-style: italic;">No activity recorded this week.</p>' if not daily_rows else f'''
                <table>
                    <thead>
                        <tr>
                            <th>Day</th>
                            <th>Date</th>
                            <th>Work</th>
                            <th>Idle</th>
                            <th>Suspicious</th>
                            <th>Screenshots</th>
                        </tr>
                    </thead>
                    <tbody>
                        {daily_rows}
                    </tbody>
                </table>
                '''}
            </div>

            <!-- Insights -->
            <div class="section">
                <h2>💡 Insights</h2>
                <div style="background-color: #e3f2fd; padding: 15px; border-radius: 5px; border-left: 4px solid #2196F3;">
                    <p style="margin: 0; color: #1976d2; line-height: 1.6;">
                        {'Great week! Your productivity is excellent.' if productivity_pct >= 90 else
                         'Good work this week. Consider minimizing idle time for better productivity.' if productivity_pct >= 70 else
                         'There is room for improvement. Try to reduce idle and suspicious activity.'}
                    </p>
                </div>
            </div>
        </div>

        <div class="footer">
            <p><strong>Work Monitor</strong> - Automated Weekly Report</p>
            <p>Generated on {datetime.now().strftime("%B %d, %Y at %I:%M %p")}</p>
        </div>
    </div>
</body>
</html>
        """
        return html

    def send_email_report(self):
        """Send the weekly report via email"""
        try:
            # Check if email is configured
            if not self.config.get('email_enabled'):
                print("Email reports are disabled in settings")
                return False

            email_to = self.config.get('email_to')
            email_from = self.config.get('email_from')
            smtp_server = self.config.get('smtp_server')
            smtp_port = self.config.get('smtp_port')
            smtp_username = self.config.get('smtp_username')
            smtp_password = self.config.get('smtp_password')
            smtp_use_tls = self.config.get('smtp_use_tls', True)

            # Validate configuration
            if not all([email_to, email_from, smtp_server, smtp_username, smtp_password]):
                print("Email configuration incomplete. Please configure in Admin Panel.")
                return False

            # Generate report
            html_content = self.generate_weekly_report_html()

            # Create email
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"Weekly Work Report - {datetime.now().strftime('%B %d, %Y')}"
            msg['From'] = email_from
            msg['To'] = email_to

            # Attach HTML content
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)

            # Send email
            print(f"Sending weekly report to {email_to}...")

            if smtp_use_tls:
                server = smtplib.SMTP(smtp_server, smtp_port)
                server.starttls()
            else:
                server = smtplib.SMTP_SSL(smtp_server, smtp_port)

            server.login(smtp_username, smtp_password)
            server.sendmail(email_from, email_to, msg.as_string())
            server.quit()

            print(f"✓ Weekly report sent successfully to {email_to}")
            return True

        except smtplib.SMTPAuthenticationError:
            print("✗ Email authentication failed. Check username/password.")
            return False
        except smtplib.SMTPException as e:
            print(f"✗ SMTP error: {e}")
            return False
        except Exception as e:
            print(f"✗ Error sending email: {e}")
            return False

    def schedule_weekly_reports(self):
        """Schedule weekly email reports for Friday at 5:30 PM"""
        # Schedule for every Friday at 5:30 PM
        schedule.every().friday.at("17:30").do(self.send_email_report)
        print("✓ Weekly email reports scheduled for every Friday at 5:30 PM")

        # Run scheduler in background
        self.running = True
        while self.running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

    def start_scheduler(self):
        """Start the email scheduler in a background thread"""
        if self.scheduler_thread is not None and self.scheduler_thread.is_alive():
            print("Email scheduler already running")
            return

        self.scheduler_thread = threading.Thread(target=self.schedule_weekly_reports, daemon=True)
        self.scheduler_thread.start()
        print("Email scheduler started")

    def stop_scheduler(self):
        """Stop the email scheduler"""
        self.running = False
        schedule.clear()
        print("Email scheduler stopped")

    def send_test_email(self):
        """Send a test email immediately (for testing configuration)"""
        print("Sending test email...")
        return self.send_email_report()
