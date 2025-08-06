from flask import Flask, render_template, request, redirect, jsonify, session
from pymongo import MongoClient
from datetime import datetime, timedelta
from bson.objectid import ObjectId
import qrcode
import hashlib
import os
import requests
import jwt
from functools import wraps
from pytz import timezone, utc
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.secret_key = "123Cecilia123"  # Secret Key

# From environment
app.secret_key = os.getenv("FLASK_SECRET_KEY")
JWT_SECRET = os.getenv("JWT_SECRET")
MONGO_URI = os.getenv("MONGODB_URI")
NGROK_URL = os.getenv("NGROK_URL")

# MongoDB
client = MongoClient(MONGO_URI)

db = client["qr_attendance"]
lectures = db["lectures"]
logs = db["logs"]
users = db["users"]
teachers = db["teachers"]

# JWT setup
JWT_SECRET = "u92$dFg6@A1e!xG#9qLp4vRzK!yNm2"
JWT_EXPIRATION_MINUTES = 30

# ---------------- Token Auth ------------------

def generate_token(teacher_id):
    payload = {
        "teacher_id": str(teacher_id),
        "exp": datetime.utcnow() + timedelta(minutes=JWT_EXPIRATION_MINUTES)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def verify_token(token):
    try:
        decoded = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return decoded["teacher_id"]
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None

def jwt_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.cookies.get('token')
        if not token:
            return redirect('/login')
        teacher_id = verify_token(token)
        if not teacher_id:
            return redirect('/login')
        session["teacher_id"] = teacher_id
        return f(*args, **kwargs)
    return decorated_function

# ---------------- Utility Functions ------------------

def get_device_id(request):
    ip = request.remote_addr or "unknown"
    agent = request.headers.get("User-Agent", "unknown")
    return hashlib.sha256((ip + agent).encode()).hexdigest()

def get_ngrok_url():
    return os.getenv("NGROK_URL", "")


# ---------------- Routes ------------------

@app.route("/")
def home():
    return redirect("/landing")

@app.route("/landing")
def landing():
    return render_template("landing.html")

# ---------------- Auth ------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        teacher = teachers.find_one({"username": username, "password": password})
        if teacher:
            token = generate_token(teacher["_id"])
            resp = redirect("/dashboard")
            resp.set_cookie("token", token, httponly=True)
            session["username"] = teacher["username"]
            return resp
        # Render template with error message
        return render_template("login.html", error="Invalid credentials!")
    return render_template("login.html")

@app.route("/register_teacher", methods=["GET", "POST"])
def register_teacher():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if teachers.find_one({"username": username}):
            return "Username already exists!"
        teachers.insert_one({"username": username, "password": password})
        return redirect("/login")
    return render_template("register_teacher.html")

@app.route("/logout")
def logout():
    session.clear()
    resp = redirect("/login")
    resp.delete_cookie("token")
    return resp

# ---------------- Dashboard & Lecture ------------------

@app.route('/dashboard')
@jwt_required
def dashboard():
    teacher_id = session.get("teacher_id")
    teacher = teachers.find_one({"_id": ObjectId(teacher_id)})
    teacher_lectures = list(lectures.find({"teacher_id": teacher_id}))
    return render_template("dashboard.html", lectures=teacher_lectures, username=teacher["username"])

@app.route("/create", methods=["GET", "POST"])
@jwt_required
def create_lecture():
    if request.method == "POST":
        lecture_name = request.form["lecture_name"]
        date = request.form["date"]
        time = request.form["time"]
        teacher_id = session["teacher_id"]
        teacher_name = session["username"]

        existing = lectures.find_one({
            "teacher_id": teacher_id,
            "lecture_name": lecture_name,
            "date": date,
            "time": time
        })

        if existing:
            return render_template("create_lecture.html", error="⚠️ Lecture with same name, date and time exists.")

        lecture = {
            "lecture_name": lecture_name,
            "teacher_name": teacher_name,
            "teacher_id": teacher_id,
            "date": date,
            "time": time,
            "active": True,
            "created_at": datetime.now()
        }

        lecture_id = lectures.insert_one(lecture).inserted_id
        ngrok_url = get_ngrok_url()
        attendance_url = f"{ngrok_url}/scan/{lecture_id}"

        os.makedirs("static/qr", exist_ok=True)
        qr_path = f"static/qr/{lecture_id}.png"
        qrcode.make(attendance_url).save(qr_path)

        return render_template("qr_display.html",
                               lecture_name=lecture_name,
                               teacher_name=teacher_name,
                               date=date,
                               time=time,
                               qr_path=qr_path,
                               url=attendance_url,
                               lecture_id=str(lecture_id))
    return render_template("create_lecture.html")

@app.route("/qr/<lecture_id>")
@jwt_required
def view_qr(lecture_id):
    lecture = lectures.find_one({"_id": ObjectId(lecture_id)})
    if not lecture:
        return "Lecture not found", 404

    # Paths and URL
    qr_folder = "static/qr"
    os.makedirs(qr_folder, exist_ok=True)  # Ensure folder exists

    qr_path = os.path.join(qr_folder, f"{lecture_id}.png")
    ngrok_url = get_ngrok_url()
    attendance_url = f"{ngrok_url}/scan/{lecture_id}"

    # Regenerate QR code if missing
    if not os.path.exists(qr_path):
        qr = qrcode.make(attendance_url)
        qr.save(qr_path)

    return render_template("qr_display.html",
                           lecture_name=lecture["lecture_name"],
                           teacher_name=lecture["teacher_name"],
                           date=lecture["date"],
                           time=lecture["time"],
                           qr_path=qr_path,
                           url=attendance_url,
                           lecture_id=lecture_id)
    
@app.route("/stop/<lecture_id>", methods=["POST"])
@jwt_required
def stop_qr(lecture_id):
    lectures.update_one({"_id": ObjectId(lecture_id)}, {"$set": {"active": False}})
    return redirect("/dashboard")

@app.route("/activate/<lecture_id>", methods=["POST"])
@jwt_required
def activate_qr(lecture_id):
    lectures.update_one({"_id": ObjectId(lecture_id)}, {"$set": {"active": True}})
    return redirect("/dashboard")

@app.route("/delete/<lecture_id>", methods=["POST"])
@jwt_required
def delete_lecture(lecture_id):
    password = request.form.get("password")
    teacher_id = session["teacher_id"]
    teacher = teachers.find_one({"_id": ObjectId(teacher_id)})

    if not teacher or teacher["password"] != password:
        return "Incorrect password", 403

    lectures.delete_one({"_id": ObjectId(lecture_id), "teacher_id": teacher_id})
    logs.delete_many({"lecture_id": lecture_id})
    return redirect("/dashboard")

@app.route("/view/<lecture_id>")
@jwt_required
def view_attendance(lecture_id):
    teacher_id = session["teacher_id"]
    lecture = lectures.find_one({"_id": ObjectId(lecture_id)})

    if not lecture or lecture["teacher_id"] != teacher_id:
        return "Unauthorized", 403

    # Fix: Query logs using lecture_id as string
    entries = list(logs.find({"lecture_id": lecture_id}))

    india = timezone("Asia/Kolkata")
    for entry in entries:
        if isinstance(entry["timestamp"], datetime):
            entry["timestamp"] = entry["timestamp"].replace(tzinfo=utc).astimezone(india)

    return render_template("view_attendance.html", lecture=lecture, entries=entries)


@app.route("/qr/<lecture_id>")
def qr(lecture_id):
    lec = lectures_collection.find_one({"_id": ObjectId(lecture_id)})
    if not lec or "qr_filename" not in lec:
        return "QR not found", 404

    return render_template("qr.html", qr_filename=lec["qr_filename"])


# ---------------- Student QR Scan & Attendance ------------------

@app.route("/scan/<lecture_id>")
def scan(lecture_id):
    lecture = lectures.find_one({"_id": ObjectId(lecture_id)})
    if not lecture or not lecture.get("active", True):
        return "QR Code Disabled or Invalid", 404
    return render_template("scanner.html", lecture=lecture, lecture_id=str(lecture_id))

@app.route("/check_user", methods=["POST"])
def check_user():
    data = request.get_json()
    device_id = data.get("device_id")
    user = users.find_one({"device_id": device_id})
    if user and user.get("name") and user.get("roll_no"):
        return {"status": "known"}
    return {"status": "unknown"}

@app.route("/register_inline", methods=["POST"])
def register_inline():
    data = request.get_json()
    device_id = data["device_id"]
    name = data["name"]
    roll_no = data["roll_no"]

    existing = users.find_one({"device_id": device_id})
    if existing:
        users.update_one({"device_id": device_id}, {"$set": {"name": name, "roll_no": roll_no}})
    else:
        users.insert_one({"device_id": device_id, "name": name, "roll_no": roll_no})

    return {"status": "registered"}

@app.route("/mark/<lecture_id>", methods=["POST"])
def mark_attendance(lecture_id):
    data = request.get_json()
    device_id = data.get("device_id")
    if not device_id:
        return "Missing device ID", 400

    lecture = lectures.find_one({"_id": ObjectId(lecture_id)})
    if not lecture:
        return "Invalid Lecture ID", 404

    user = users.find_one({"device_id": device_id})
    name = user["name"] if user else "Unknown"
    roll_no = user.get("roll_no", "Unknown")

    already = logs.find_one({
        "lecture_id": lecture_id,
        "device_id": device_id
    })

    if already:
        return render_template("already.html", lecture=lecture, name=name, roll_no=roll_no)

    logs.insert_one({
        "lecture_id": lecture_id,
        "device_id": device_id,
        "name": name,
        "roll_no": roll_no,
        "timestamp": datetime.now(),
        "ip": request.remote_addr or "unknown"
    })

    return render_template("success.html", lecture=lecture, name=name, roll_no=roll_no)

# ---------------- Main ------------------

if __name__ == "__main__":
    app.run(debug=True, port=5050)
