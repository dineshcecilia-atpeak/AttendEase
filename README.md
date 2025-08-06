# AttendEase 🎓📲

AttendEase is a Flask-based QR Code Attendance System that allows teachers to generate and manage secure QR codes for student attendance. Students can scan dynamic QR codes to mark attendance using their device ID — helping prevent proxy and misuse.

<img width="1080" height="1080" alt="3" src="https://github.com/user-attachments/assets/958db54b-aa1f-4194-8bd7-37a7df4de2db" />

<img width="1080" height="1080" alt="1" src="https://github.com/user-attachments/assets/819dc3eb-ad6c-4144-ad6d-7f07e8045f62" />

<img width="1080" height="1080" alt="2" src="https://github.com/user-attachments/assets/3126b1df-fde4-4c56-a0b2-784c1a530fd5" />


---

## 🚀 Features

- Teacher login and dashboard  
- Create and manage lectures  
- QR code generation (linked to ngrok public URL)  
- JWT-based session authentication  
- Student-side device-based attendance marking  
- View attendance per lecture  
- Prevents duplicate entries and proxies  

---

## ⚙️ Installation

1. Clone the Repository

    git clone https://github.com/dineshcecilia-atpeak/AttendEase.git  
    cd AttendEase

2. Create Virtual Environment (Recommended)

    python -m venv venv  
    source venv/bin/activate  # For Windows: venv\\Scripts\\activate

3. Install Dependencies

    pip install -r requirements.txt

4. Create .env File

    Create a `.env` file in the project root and add:

    FLASK_SECRET_KEY=your_flask_secret_key  
    JWT_SECRET=your_jwt_secret_key  
    MONGODB_URI=mongodb://localhost:27017  
    NGROK_URL=https://your-ngrok-subdomain.ngrok-free.app

    (Replace `your_*` values accordingly.)

5. Run the App

    python app.py  
    The app will start at http://localhost:5050

---

## 🌐 External Access via ngrok

If you want students to access the QR page from mobile devices:

    ngrok http 5050

Copy the generated HTTPS URL and update your `.env` file:

    NGROK_URL=https://your-generated-ngrok-url.ngrok-free.app

---

## Author

Developed by: Cecilia Dinesh  
GitHub: https://github.com/dineshcecilia-atpeak

---

## License

This project is licensed under the MIT License.
