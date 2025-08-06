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


## ⚙️ Installation

### 🔧 1. Clone the repo

```bash
git clone https://github.com/dineshcecilia-atpeak/AttendEase.git
cd AttendEase

### 2. Create a virtual environment (recommended)

python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

3. Install required packages

pip install -r requirements.txt

4. Create .env file

FLASK_SECRET_KEY=your_flask_secret_key
JWT_SECRET=your_jwt_secret_key
MONGODB_URI=mongodb://localhost:27017
NGROK_URL=https://your-ngrok-subdomain.ngrok-free.app

5. Run the app

python app.py

Access via ngrok (for student mobile access)
If testing externally, run:

ngrok http 5050
Copy the generated https://... URL and paste it into your .env as NGROK_URL.
---

## 👨‍💻 Author

Developed by Cecilia Dinesh
GitHub: @dineshcecilia-atpeak

---
