from flask import Flask, request, jsonify, session, redirect, url_for, render_template
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import json
from typing import TypedDict
import datetime
import uuid

# define a user class using typeddict
class User(TypedDict):
    pid: int = uuid.uuid4().int
    name: str = ""
    email: str = ""
    password: str = ""
    phone_no: int = 0
    gender: str = ""
    DOB: datetime.date = None

app = Flask(__name__)

login_manager = LoginManager(app)
# login_manager.init_app(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/userlogin", methods=["POST", "GET"])
def user_login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    with open("./data/users.json", "r") as f:
        users = json.load(f)
    if request.method == "POST":
        email: str = request.form["email"]
        password: str = request.form["password"]
        for user in users:
            if user["email"] == email and user["password"] == password:
                user_obj = User(**user)
                login_user(user_obj)
                return redirect(url_for("index"))
            return render_template("index.html", error="Invalid email or password")
    return render_template("userlogin.html")

@app.route("/userregister", methods=["POST", "GET"])
def user_register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    if request.method == "POST":
        name: str = request.form["name"]
        email: str = request.form["email"]
        password: str = request.form["password"]
        phone_no: int = request.form["phone_no"]
        gender: str = request.form["gender"]
        DOB: datetime.date = request.form["DOB"]
        user = User(
            pid=uuid.uuid4().int,
            name=name,
            email=email,
            password=password,
            phone_no=phone_no,
            gender=gender,
            DOB=DOB
        )
        with open("./data/users.json", "r") as f:
            users = json.load(f)
        users.append(user)
        with open("./data/users.json", "w") as f:
            json.dump(users, f)
        login_user(user)
        return redirect(url_for("index"))
    return render_template("userregister.html")
