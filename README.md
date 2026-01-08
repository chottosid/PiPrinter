# PiPrinter - Easy Remote Printing

Turn your Raspberry Pi into a web-connected printer! Upload PDFs from any device and print.

---

## Requirements

- Raspberry Pi with Raspberry Pi OS
- USB printer
- Network connection
- ~10 minutes to set up

---

## Quick Start Setup

### Step 1: Update System

```bash
sudo apt update && sudo apt upgrade -y
```

### Step 2: Install Dependencies

```bash
sudo apt install -y python3 python3-pip python3-venv cups libcups2-dev
```

### Step 3: Configure Printer Access

Add your user to the printer admin group:

```bash
sudo usermod -a -G lpadmin pi
```

### Step 4: Set Up Project Directory

```bash
cd /home/pi
mkdir piprinter_test && cd piprinter_test
```

### Step 5: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 6: Install Application

```bash
pip install uv
uv pip install -r requirements.txt
```

### Step 7: Configure Application

Create the environment file:

```bash
nano .env
```

Paste the following configuration:

```env
SECRET_KEY=change-this-to-random-string-12345
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
DATABASE_URL=sqlite:///./printer_app.db
UPLOAD_DIR=./uploads
```

Save with `Ctrl+X`, then `Y`, then `Enter`.

### Step 8: Set Up Uploads Directory

```bash
mkdir uploads
chmod 755 uploads
```

### Step 9: Connect Printer

Plug in your USB printer and verify it's detected:

```bash
lpstat -p
```

### Step 10: Start the Application

```bash
source venv/bin/activate
python -m app.main
```

### Step 11: Access the Web Interface

Find your Pi's IP address:

```bash
hostname -I
```

Open your browser and navigate to:

```
http://<your-pi-ip>:6969
```

Example: `http://192.168.1.100:6969`

---

## How to Use

1. **Register** - Create your account
2. **Login** - Enter your email and password
3. **Upload PDF** - Click to select your file
4. **Select Printer** - Choose from the dropdown menu
5. **Print** - Click "Print Document"

Done! 🖨️

---

## Optional: Auto-Start on Boot

### Create the Service File

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

Save with `Ctrl+X`, then `Y`, then `Enter`.

### Enable and Start the Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable piprinter
sudo systemctl start piprinter
```

---

## Troubleshooting

### Printer Not Detected

Check if the printer is recognized:

```bash
lpstat -p
```

### CUPS Service Issues

Restart the CUPS service:

```bash
sudo systemctl restart cups
```

### Can't Access from Other Devices

Allow firewall access for port 6969:

```bash
sudo ufw allow 6969/tcp
```

### Find Pi's IP Address

```bash
hostname -I
```
