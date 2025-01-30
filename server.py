from flask import Flask, render_template, request, redirect, session, url_for
from sqlalchemy.orm import Session
from database.models import *
import hashlib
from datetime import timedelta
from cryptography.fernet import Fernet
import json


key = b'_oY01wmobI0Kez1TRcYLvWDo4Cqi8HS9mnASyZaZoxQ='
secure_obj = Fernet(key)
session1 = Session(engine)
server = Flask(__name__)
server.secret_key = "consortmentalization"
server.permanent_session_lifetime = timedelta(minutes=1440)

@server.route("/")
def homepage():
    results = session1.query(Passwords).all()
    return render_template("home.html", is_loggedin=session.get("is_logged_in"), name=session.get("username"))
    
@server.route("/home")
def homepage_alt():
    return render_template("home.html")

@server.route("/login", methods=["GET", "POST"])
def login_page():
    global session
    if request.method == "POST":
        userid = request.form.get("username2")
        pswrd = hashlib.sha256(request.form.get("password2").encode("utf-8")).hexdigest()
        if session1.query(Users).filter_by(username=userid, password=pswrd).first() != None:
            session["username"] = userid
            session["is_logged_in"] = True
            return redirect(f'/users/{session.get("username")}')
        else:
            session["is_logged_in"] = False
            return render_template("login_error.html")
    else:
        return render_template("login.html")
    
@server.route("/register", methods=["GET", "POST"])
def register_page():
    if request.method == "POST":
        userid = request.form.get("username")
        pswrd = request.form.get("password")
        if session1.query(Users).filter(Users.username == userid).first() == None:
            new_user = Users(username=userid, password = hashlib.sha256(pswrd.encode("utf-8")).hexdigest())
            session1.add(new_user)
            session1.commit()
            return render_template("reg_success.html")
        else:
            return render_template("reg_error.html")
    else:
        return render_template("register.html")

@server.route("/users/<username>")
def user_page(username):
    global session
    if session.get("is_logged_in")==True:
        return render_template("userpage.html", userid=session["username"])
    else:
        return render_template("user_error.html")

@server.route("/users/<username>/addpasses", methods=["GET", "POST"])
def addpasses_page(username):
    global session
    if session.get("is_logged_in"):
        if request.method=="POST":
            token1 = secure_obj.encrypt(request.form["input1"].encode())
            token2 = secure_obj.encrypt(request.form["input2"].encode())
            new_pass = Passwords(website=token1.decode(), pswrd=token2.decode(), user=session["username"])
            session1.add(new_pass)
            session1.commit()
            return render_template("addpasses.html", user=session["username"])
        else:
            return render_template("addpasses.html", user=session["username"])
    else:
        return render_template("user_error.html")
    
@server.route("/users/<username>/showpasses", methods=["GET", "DELETE"])
def showpasses_page(username):
    
    if request.method=="GET":
        results = session1.query(Passwords).filter_by(user=session.get("username"))
        pswrds = []
        websites = []
        for result in results:
            websites.append(secure_obj.decrypt(result.website.encode()).decode())
            pswrds.append(secure_obj.decrypt(result.pswrd.encode()).decode())
        return render_template("showpasses.html", len=len(pswrds), user=session.get("username"), passwords=pswrds, website=websites)
    elif request.method=="DELETE":
        incoming = request.get_json()
        print(request.get_json())
        to_delete = session1.query(Passwords).filter_by(user=session.get("username")).all()
        for result in to_delete:
            if secure_obj.decrypt(result.website.encode()).decode() == incoming["website1"] and secure_obj.decrypt(result.pswrd.encode()).decode()==incoming["password1"]:
                session1.delete(result)
        session1.commit()
        results = session1.query(Passwords).filter_by(user=session.get("username"))
        pswrds = []
        websites = []
        for result in results:
            websites.append(secure_obj.decrypt(result.website.encode()).decode())
            pswrds.append(secure_obj.decrypt(result.pswrd.encode()).decode())
        return render_template("showpasses.html", len=len(pswrds), user=session.get("username"), passwords=pswrds, website=websites)
    