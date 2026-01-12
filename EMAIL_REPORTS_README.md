# Weekly Email Reports Feature

## Overview

The Work Monitor app now supports automatic weekly email reports! Every Friday at 5:30 PM, the app will automatically send a beautifully formatted HTML email report with your weekly work statistics and metrics.

## Features

- 📧 **Automatic weekly emails** sent every Friday at 5:30 PM
- 📊 **Comprehensive metrics** including:
  - Total work hours
  - Real work hours (excluding suspicious activity)
  - Idle time
  - Suspicious activity hours
  - Productivity score
  - Daily breakdown with screenshots count
- 🎨 **Beautiful HTML formatting** with gradient colors and responsive design
- 📅 **Previous week summary** - reports cover Monday to Sunday of the completed week
- 💡 **Smart insights** based on your productivity score
- ✅ **Test email function** to verify your configuration

## Setup Instructions

### 1. Install Dependencies

First, make sure you have the required package installed:

```bash
pip install schedule
```

Or install all requirements:

```bash
pip install -r WorkMonitor/src/requirements.txt
```

### 2. Configure Email Settings

1. Open the Work Monitor application
2. Click on **"Admin Panel"** button
3. Enter the admin password (default: `admin123`)
4. Scroll down to the **"📧 Weekly Email Reports"** section

### 3. Email Configuration Fields

Fill in the following fields:

- **Enable Weekly Email Reports**: Check this box to enable automatic reports
- **Send Report To (Email)**: The recipient email address
- **SMTP Server**: Your email provider's SMTP server
  - Gmail: `smtp.gmail.com`
  - Outlook: `smtp-mail.outlook.com`
  - Yahoo: `smtp.mail.yahoo.com`
- **SMTP Port**: Usually `587` for TLS or `465` for SSL
- **SMTP Username/Email**: Your email address
- **SMTP Password**: Your email password or app password

### 4. Gmail-Specific Instructions

If using Gmail, you need to use an **App Password** instead of your regular password:

1. Go to your Google Account settings
2. Navigate to Security → 2-Step Verification
3. Scroll down to "App passwords"
4. Generate a new app password for "Mail"
5. Use this 16-character password in the SMTP Password field

### 5. Test Your Configuration

1. After filling in all the fields, click **"📧 Send Test Email"**
2. Wait a few seconds for the email to send
3. Check your inbox to verify the test email was received
4. If successful, click **"Save Settings"** to save your configuration

### 6. Enable and Restart

1. Make sure **"Enable Weekly Email Reports"** is checked
2. Click **"Save Settings"**
3. **Restart the application** for the scheduler to start

## Email Report Contents

The weekly email report includes:

### Key Metrics Cards
- Total Work Hours
- Real Work Hours (productivity time)
- Idle Hours
- Suspicious Hours

### Productivity Score
- Visual progress bar showing productivity percentage
- Based on real work vs total work time

### Week Summary
- Days worked
- Average hours per day
- Total screenshots captured
- Overtime hours

### Daily Breakdown Table
- Day-by-day breakdown for the week
- Work hours, idle time, suspicious activity per day
- Screenshot count per day

### Insights
- Smart recommendations based on your productivity score

## Scheduling Details

- **Frequency**: Every Friday
- **Time**: 5:30 PM (17:30)
- **Week Covered**: Previous Monday to Sunday
- **Automatic**: Runs in the background while the app is running

## Troubleshooting

### Email not sending?

1. **Check credentials**: Verify SMTP username and password are correct
2. **App password**: If using Gmail, make sure you're using an app password, not your regular password
3. **Firewall**: Ensure your firewall allows outgoing SMTP connections
4. **Port**: Try port 465 with SSL if port 587 doesn't work

### Test email shows error?

- Check the console output for specific error messages
- Verify SMTP server address is correct
- Ensure your email provider allows SMTP connections
- Some providers require "Less secure app access" to be enabled

### Scheduler not running?

- Make sure you **restarted the app** after enabling email reports
- Check that "Enable Weekly Email Reports" is checked
- Verify the `schedule` package is installed: `pip install schedule`

## Security Notes

- Email passwords are stored in the encrypted config file
- Passwords are displayed as asterisks in the UI
- Consider using app-specific passwords instead of your main email password
- Keep your config files secure

## Support

For issues or questions:
- Check the console output for error messages
- Verify all configuration fields are filled correctly
- Test with the "Send Test Email" button before relying on scheduled reports

---

Enjoy your automated weekly reports! 📊✨
