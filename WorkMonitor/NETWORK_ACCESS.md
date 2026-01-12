# Network Dashboard Access

This feature allows you to access the Work Monitor dashboard from other computers on the same network.

## How to Enable Network Access

1. Open the **Work Monitor** application
2. Click on **Admin Panel** button
3. Enter the admin password (default: `admin123`)
4. Scroll down to the **🌐 Network Dashboard Access** section
5. Check the box **"Enable Network Access to Dashboard"**
6. Set the **Dashboard Port** (default: `8080`)
7. Click **Save Settings**
8. **Restart the application** for changes to take effect

## Accessing the Dashboard

### From the Same Computer
- Open your browser and go to: `http://localhost:8080`

### From Another Computer on the Same Network

1. **Find the IP address** of the computer running Work Monitor:
   - The IP address is displayed in the main window under "Network: http://xxx.xxx.xxx.xxx:8080"
   - Or check the Admin Panel for the access URL

2. **Access the dashboard** from another computer:
   - Open a web browser on the other computer
   - Enter the URL: `http://[IP_ADDRESS]:8080`
   - Example: `http://192.168.1.100:8080`

## Troubleshooting

### Cannot Access from Another Computer

1. **Check Firewall Settings**
   - Windows Firewall may block incoming connections
   - Allow Python or the Work Monitor app through the firewall
   - Or allow incoming connections on port 8080

2. **Verify Network Connection**
   - Make sure both computers are on the same network
   - Try pinging the IP address from the other computer

3. **Check the Port Number**
   - Make sure you're using the correct port number
   - Default is 8080, but it can be changed in Admin Panel

4. **Restart the Application**
   - Changes to network settings require a restart

## Security Considerations

- The dashboard is accessible to anyone on your local network
- No authentication is required to view the dashboard
- Do NOT expose this to the internet (only use on local network)
- Consider using a VPN if accessing from outside your network

## Changing the Port

If port 8080 is already in use, you can change it:

1. Open Admin Panel
2. Change the **Dashboard Port** to a different number (e.g., 8081, 8888)
3. Save settings and restart the app

Common port alternatives:
- 8081
- 8888
- 9090
- 3000

## Technical Details

- The dashboard auto-refreshes every 30 seconds
- Uses standard HTTP protocol
- Serves static HTML with embedded images
- No database or external dependencies required
