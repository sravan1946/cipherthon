from flask import Flask, flash, request, jsonify, session, redirect, url_for, render_template
from flask_login import (
    LoginManager,
    login_user,
    login_required,
    logout_user,
    current_user,
    UserMixin,
)
import json
import datetime
import uuid
from utils import gen_qrcode
import os


# define a user class using typeddict
class User(UserMixin):
    def __init__(self, pid, name, email, password, phone_no, gender, DOB):
        self.pid = pid
        self.name = name
        self.email = email
        self.password = password
        self.phone_no = phone_no
        self.gender = gender
        self.DOB = DOB
        self.reports = []

    def get_id(self):
        return str(self.pid)

    def __dict__(self):
        return {
            "pid": self.pid,
            "name": self.name,
            "email": self.email,
            "password": self.password,
            "phone_no": self.phone_no,
            "gender": self.gender,
            "DOB": self.DOB,
            "reports": self.reports,
        }


app = Flask(__name__)
app.secret_key = os.urandom(24)
login_manager = LoginManager(app)
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    with open("./data/users.json", "r") as f:
        users = json.load(f)
    for user in users:
        if user["pid"] == int(user_id):
            return User(**user)
    return None


@app.route("/")
@app.route("/index.html")
@app.route("/index")
def index():
    return render_template("index.html", current_user=current_user)


@app.route("/userlogin", methods=["POST", "GET"])
def user_login():
    if current_user.is_authenticated:
        return redirect(url_for("user_dashboard"))
    try:
        with open("./data/users.json", "r") as f:
            users = json.load(f)
    except FileNotFoundError:
        with open("./data/users.json", "w") as f:
            json.dump([], f)
        users = []
    if request.method == "POST":
        email: str = request.form["email"]
        password: str = request.form["password"]
        logged_in = False
        for user in users:
            if user["email"] == email and user["password"] == password:
                user = User(**user)
                login_user(user, force=True)
                session['logged_in'] = True
                logged_in = True
                return redirect(url_for("user_dashboard"))
        if not logged_in:
            return render_template("userlogin.html", error="Invalid email or password")
    error = request.args.get("error")
    return render_template("userlogin.html", error=error)


@app.route("/userregister", methods=["POST", "GET"])
def user_register():
    if current_user.is_authenticated:
        return render_template("userdashboard")
    if request.method == "POST":
        pid: int = int(str(uuid.uuid4().int)[:14])
        name: str = request.form["name"]
        email: str = request.form["email"]
        password: str = request.form["password"]
        phone_no: int = request.form["phone_no"]
        gender: str = request.form["gender"]
        DOB: datetime.date = request.form["DOB"]
        user = User(
            pid=pid,
            name=name,
            email=email,
            password=password,
            phone_no=phone_no,
            gender=gender,
            DOB=DOB,
        )
        try:
            with open("./data/users.json", "r") as f:
                users = json.load(f)
        except FileNotFoundError:
            with open("./data/users.json", "w") as f:
                json.dump([], f)
            users = []
        if user.email in [user['email'] for user in users]:
            return redirect(url_for("user_login", error="User already exists. Please login."))
        users.append(user)
        with open("./data/users.json", "w") as f:
            json.dump(users, f, default=lambda x: x.__dict__())
        login_user(user, force=True)
        session['logged_in'] = True
        return redirect(url_for("user_login", error="User registered successfully. Please login."))
    return render_template("userregister.html")


@app.route("/userreport")
@login_required
def user_report():
    return render_template("uploadreport.html")

@app.route("/userdashboard")
@login_required
def user_dashboard():
    print(current_user.pid)
    return render_template("userdashboard.html", qrcode=gen_qrcode(current_user))

@app.route("/logout")
@login_required
def logout():
    if not current_user.is_authenticated:
        return redirect(url_for("user_login"))
    logout_user()
    session['logged_in'] = False
    return render_template("index.html", current_user=current_user)

@app.route("/profile/<int:pid>")
def profile(pid):
    with open("./data/users.json", "r") as f:
        users = json.load(f)
    for user in users:
        if user["pid"] == pid:
            return jsonify(user)
    return "User not found", 404