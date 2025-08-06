# AttendEase 🎓📲

**AttendEase** is a Flask-based QR Code Attendance System that allows teachers to generate and manage secure QR codes for student attendance. Students can scan dynamic QR codes to mark attendance using their device ID — helping prevent proxy and misuse.

---

## 🚀 Features

- 👨‍🏫 Teacher login and dashboard
- 🧾 Create and manage lectures
- 📷 QR code generation (linked to ngrok public URL)
- 🔐 JWT-based session authentication
- 📱 Student-side device-based attendance marking
- 📊 View attendance per lecture
- ✅ Prevents duplicate entries and proxies

---

## 📂 Folder Structure

AttendEase/
├── app.py
├── static/
│ └── qr/
├── templates/
│ ├── dashboard.html
│ ├── create_lecture.html
│ ├── qr_display.html
│ ├── login.html
│ ├── register_teacher.html
│ ├── scanner.html
│ ├── success.html
│ └── already.html
├── .env
├── .gitignore
├── requirements.txt
└── README.md


---

## ⚙️ Installation

### 🔧 1. Clone the repo

```bash
git clone https://github.com/dineshcecilia-atpeak/AttendEase.git
cd AttendEase

### 2. Create a virtual environment (recommended)

python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
