from flask import Flask, request, jsonify, session, redirect, url_for, render_template
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
        if user["pid"] == user_id:
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
        return redirect(url_for("userdashboard"))
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
                login_user(user)
                logged_in = True
                return render_template("userdashboard.html", qrcode=gen_qrcode(current_user))
        if not logged_in:
            return render_template("userlogin.html", error="Invalid email or password")
    return render_template("userlogin.html")


@app.route("/userregister", methods=["POST", "GET"])
def user_register():
    if current_user.is_authenticated:
        return render_template("userdashboard")
    if request.method == "POST":
        pid = uuid.uuid4().int
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
        users.append(user)
        with open("./data/users.json", "w") as f:
            json.dump(users, f, default=lambda x: x.__dict__())
        login_user(user)
        return render_template("userlogin")
    return render_template("userregister.html")


@app.route("/userdashboard")
@login_required
def user_dashboard():
    return render_template("userdashboard.html", qrcode=gen_qrcode(current_user.pid))

@app.route("/logout")
@login_required
def logout():
    if not current_user.is_authenticated:
        return redirect(url_for("user_login"))
    logout_user()
    return render_template("index")

@app.route("/profile/<int:pid>")
def profile(pid):
    with open("./data/users.json", "r") as f:
        users = json.load(f)
    for user in users:
        if user["pid"] == pid:
            return jsonify(user)
    return "User not found", 404