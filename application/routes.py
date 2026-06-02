from app import app
from .model import db, Admin,User,Staff,Trek,Booking
from flask import render_template, request, redirect, session

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/register",methods=["GET","POST"])
def register():
    if request.method == "GET":
        return render_template("user/register.html")
    if request.method == "POST":
        user_name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        password = request.form.get("password")
        
    

        existing_user = User.query.filter_by(email=email).first()

        if existing_user: 
            return redirect("/login")
    
        user = User(user_name=user_name, email=email, password=password, mobile=phone)
        db.session.add(user)
        db.session.commit()

    
        return redirect("/login")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "GET":
        return render_template("user/login.html")
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()

        if not user or user.password != password:
            return redirect("/login")
        session["user_id"] = user.user_id
        return redirect("/user_dashboard")


@app.route("/admin_login", methods=["GET","POST"])
def admin_login():
    if request.method == "GET":
        return render_template("admin/admin_login.html")
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        admin = Admin.query.filter_by(email=email).first()

        if not admin or admin.password != password:
            return redirect("/login")
        session["user_id"] = admin.id
        
        
        return redirect("/admin_dashboard")


@app.route("/staff_login", methods=["GET","POST"])
def staff_login():
    if request.method == "GET":
        return render_template("staff/staff_login.html")
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        staff = Staff.query.filter_by(email=email).first()

        if not staff or staff.password != password:
            return redirect("/login")
        session["user_id"] = staff.staff_id
        
        
        return redirect("/staff_dashboard")

@app.route("/user_dashboard")
def user_dashboard():

    user_id = session.get("user_id")

    if not user_id:
        return redirect("/login")

    user = User.query.get(user_id)

    treks = Trek.query.all()

    return render_template(
        "user/user_dashboard.html",
        user=user,
        treks=treks
    )


@app.route("/staff_dashboard")
def staff_dashboard():

    staff_id = session.get("user_id")

    if not staff_id:
        return redirect("/login")

    staff = Staff.query.get(staff_id)

    treks = Trek.query.all()

    return render_template(
        "staff/staff_dashboard.html",
        staff=staff,
        treks=treks
    )

@app.route("/admin_dashboard")
def admin_dashboard():

    admin_id = session.get("user_id")

    if not admin_id:
        return redirect("/login")

    admin = Admin.query.get(admin_id)

    treks = Trek.query.all()

    return render_template(
        "Admin/admin_dashboard.html",
        user= admin,
        treks=treks
    )