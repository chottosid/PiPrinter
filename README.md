# PiPrinter - Simple PDF Printing Web App

A minimal, cute web application for printing PDF documents via a web interface, designed for Raspberry Pi OS or Kubuntu systems.

## Features

- User authentication (register/login with JWT tokens)
- PDF document upload with drag & drop
- Client-side PDF preview using PDF.js
- Multiple printer selection from available CUPS printers
- Document history with print status tracking (pending, printed, failed)
- Real-time printer status monitoring
- Cute, responsive UI design
- SQLite database for data persistence

## Hardware Requirements

- Raspberry Pi (any model with Raspberry Pi OS)
- 2GB+ RAM recommended
- 8GB+ storage space
- Network connection (Ethernet or WiFi)
- USB printer (or network printer)

## Software Requirements

- Raspberry Pi OS (Bookworm or later) or Ubuntu/Kubuntu 20.04+
- Python 3.8+
- CUPS (Common Unix Printing System)
- SSH access (for remote management)

## Installation Guide

### 1. System Update and Prerequisites

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and development tools
sudo apt install -y python3 python3-pip python3-venv git
```

### 2. Install CUPS (Print Server)

```bash
# Install CUPS and development headers
sudo apt install -y cups libcups2-dev

# Add your user to the lpadmin group (required for printer management)
sudo usermod -a -G lpadmin pi

# Enable and start CUPS service
sudo systemctl enable cups
sudo systemctl start cups

# Verify CUPS is running
sudo systemctl status cups
```

### 3. Configure CUPS for Remote Access

```bash
# Edit CUPS configuration to allow remote access
sudo nano /etc/cups/cupsd.conf
```

Find and modify these lines to allow access from your local network:

```
# Listen only on localhost
Listen localhost:631

# Change to:
Port 631

# Allow access from local network
<Location />
  Order allow,deny
  Allow @LOCAL
</Location>

<Location /admin>
  Order allow,deny
  Allow @LOCAL
</Location>

<Location /admin/conf>
  AuthType Default
  Require user @SYSTEM
  Order allow,deny
  Allow @LOCAL
</Location>
```

Restart CUPS:

```bash
sudo systemctl restart cups
```

### 4. Clone or Setup Project

```bash
# Navigate to project directory (adjust path as needed)
cd /home/pi/piprinter_test

# OR clone from git repository (if applicable)
# git clone https://github.com/yourusername/piprinter_test.git
# cd piprinter_test
```

### 5. Create Python Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

### 6. Install Python Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install uv (faster package installer)
pip install uv

# Install all dependencies
uv pip install -r requirements.txt
```

**Note:** If pycups installation fails:

```bash
# Install CUPS development headers
sudo apt install libcups2-dev

# Then retry
uv pip install pycups
```

### 7. Configure Environment Variables

```bash
# Generate a secure secret key
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the generated key and update the `.env` file:

```bash
nano .env
```

Update the SECRET_KEY:

```env
SECRET_KEY=your-generated-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
DATABASE_URL=sqlite:///./printer_app.db
UPLOAD_DIR=./uploads
```

### 8. Create Upload Directory

```bash
# Create uploads directory with proper permissions
mkdir -p uploads
chmod 755 uploads
```

### 9. Test the Application

```bash
# Run the application
python -m app.main
```

The application should start on `http://0.0.0.0:6969`

**Access the web interface:**
- On the Pi: `http://localhost:6969`
- From other devices: `http://<pi-ip-address>:6969`

## Setting Up a Printer

### Option 1: Via CUPS Web Interface

1. Access CUPS web interface: `http://<pi-ip-address>:631`
2. Click "Administration" tab
3. Click "Add Printer"
4. Select your printer from the list
5. Follow the setup wizard
6. Set as default printer if desired

### Option 2: Via Command Line

```bash
# List available printers
lpstat -p

# Add a USB printer (example)
lpadmin -p MyPrinter -v usb://HP/DeskJet%20Series?serial=1234 -m driver.ppd

# Set as default
lpadmin -d MyPrinter

# Test print
echo "Test" | lp -d MyPrinter
```

## Running as a System Service (Auto-startup)

### Create Systemd Service File

```bash
sudo nano /etc/systemd/system/piprinter.service
```

Add the following content:

```ini
[Unit]
Description=PiPrinter Web Application
After=network.target cups.service

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/piprinter_test
Environment="PATH=/home/pi/piprinter_test/venv/bin"
ExecStart=/home/pi/piprinter_test/venv/bin/python -m app.main
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Enable and Start the Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable auto-start on boot
sudo systemctl enable piprinter

# Start the service
sudo systemctl start piprinter

# Check status
sudo systemctl status piprinter

# View logs
sudo journalctl -u piprinter -f
```

## Network Access

### Find Your Pi's IP Address

```bash
hostname -I
```

### Access from Other Devices

- **LAN access:** `http://<pi-ip-address>:6969`
- **Example:** `http://192.168.1.100:6969`

### Firewall Configuration (if enabled)

```bash
# Allow port 6969 through firewall
sudo ufw allow 6969/tcp

# Allow CUPS web interface
sudo ufw allow 6969/tcp
sudo ufw allow 631/tcp
```

## Usage

1. **Register User**
   - Visit `http://<pi-ip>:6969`
   - Click "Register"
   - Enter email and password

2. **Login**
   - Use your credentials to login
   - You'll be redirected to the dashboard

3. **Upload PDF**
   - Click or drag a PDF file into the upload area
   - Preview will appear automatically

4. **Select Printer**
   - Choose from available printers in the dropdown
   - Check printer status indicator (green = connected, red = disconnected)

5. **Print Document**
   - Click "Print Document" button
   - Status will be updated in document history

6. **View History**
   - See all uploaded documents and print status
   - Delete documents if needed

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get access token
- `GET /api/auth/me` - Get current user info

### Documents
- `POST /api/documents/upload` - Upload PDF document
- `GET /api/documents/history` - Get user's document history
- `POST /api/documents/print/{document_id}` - Print document
- `DELETE /api/documents/{document_id}` - Delete document
- `GET /api/documents/download/{document_id}` - Download document

### Printers
- `GET /api/printers/` - List available printers
- `GET /api/printers/status` - Check printer connection status

## Configuration

### Environment Variables (.env)

```env
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
DATABASE_URL=sqlite:///./printer_app.db
UPLOAD_DIR=./uploads
```

### Changing Port

Edit `app/main.py`:

```python
uvicorn.run(app, host="0.0.0.0", port=YOUR_PORT)
```

Update `API_BASE` in all HTML templates to match new port.

## Troubleshooting

### Printer Not Detected

```bash
# Check CUPS status
sudo systemctl status cups

# Check available printers
lpstat -p

# Test CUPS connection
curl http://localhost:631
```

### Application Won't Start

```bash
# Check Python version
python3 --version

# Check virtual environment
source venv/bin/activate
which python

# Check dependencies
pip list

# View application logs
tail -f app.log
```

### Permission Denied Errors

```bash
# Fix uploads directory permissions
sudo chown -R pi:pi /home/pi/piprinter_test/uploads
chmod 755 /home/pi/piprinter_test/uploads

# Fix CUPS permissions
sudo usermod -a -G lpadmin pi
```

### Database Errors

```bash
# Check database file permissions
ls -la printer_app.db

# Recreate database if corrupted
rm printer_app.db
python -m app.main  # Will auto-recreate
```

### Port Already in Use

```bash
# Find process using port 6969
sudo lsof -i :6969

# Kill the process
sudo kill -9 <PID>
```

## Security Recommendations

1. **Change the SECRET_KEY** in `.env` before production use
2. **Use HTTPS** for production (setup with Let's Encrypt/Certbot)
3. **Enable firewall** and restrict access to trusted networks
4. **Use strong passwords** for user accounts
5. **Regular updates**: `sudo apt update && sudo apt upgrade`
6. **Backup database regularly**

### Setting up HTTPS with Certbot

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate (requires domain name)
sudo certbot --nginx -d your-domain.com

# Auto-renewal is configured automatically
```

## Maintenance

### Update Dependencies

```bash
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

### Backup Database

```bash
cp printer_app.db printer_app.db.backup.$(date +%Y%m%d)
```

### Clear Old Files

```bash
# Remove PDFs older than 30 days
find uploads/ -name "*.pdf" -mtime +30 -delete
```

### View Logs

```bash
# Application logs
tail -f app.log

# Systemd service logs
sudo journalctl -u piprinter -f

# CUPS logs
sudo tail -f /var/log/cups/error_log
```

## Performance Optimization

### For High Traffic

```bash
# Use Gunicorn with multiple workers
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:6969
```

### Monitor Resources

```bash
# System monitor
htop

# Check disk usage
df -h

# Check memory
free -h
```

## Development

### Run in Development Mode

```bash
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 6969
```

### API Documentation

- Interactive API docs: `http://<pi-ip>:6969/docs`
- Alternative docs: `http://<pi-ip>:6969/redoc`

## License

MIT License

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review application logs
3. Check CUPS logs: `sudo tail -f /var/log/cups/error_log`
4. Verify network connectivity and firewall settings

---

**Enjoy easy PDF printing from your Raspberry Pi! 🖨️**
