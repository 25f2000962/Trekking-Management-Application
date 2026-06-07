from app import app
from .model import db, Admin,User,Staff,Trek,Booking
from flask import render_template, request, redirect, session
from sqlalchemy import or_

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


    return render_template(
        "admin/admin_dashboard.html",
        users=User.query.count(),
        staff=Staff.query.count(),
        treks=Trek.query.count(),
        bookings=Booking.query.count())


@app.route("/admin/users/blacklist/<int:id>")
def blacklist_user(id):
    

    user = User.query.get(id)

    user.is_blacklisted = True
    
    user.status = "Blacklisted"

    db.session.commit()
    return redirect("/admin/users")


@app.route("/admin/users/approve/<int:id>")
def approve_user(id):
    

    user = User.query.get(id)

    user.is_blacklisted = False
    
    user.status = "Approved"

    db.session.commit()
    return redirect("/admin/users")


@app.route("/admin/staff/approve/<int:id>")
def approve_staff(id):
    staff = Staff.query.get(id)
    staff.is_blacklisted = False
    staff.status = "Approved"

    db.session.commit()
    return redirect("/admin/staff")

@app.route("/admin/staff/remove/<int:id>")
def remove_staff(id):
    staff = Staff.query.get(id)
    db.session.delete(staff)
    db.session.commit()
    return redirect("/admin/staff")


@app.route("/admin/staff/blacklist/<int:id>")
def blacklist_staff(id):
    staff = Staff.query.get(id)

    staff.is_blacklisted = True
    db.session.commit()

    
    return redirect("/admin/staff")


@app.route("/admin/staff")
def admin_staff():
    search = request.args.get("search", "")

    if search:
        staff = Staff.query.filter(
            or_(
                Staff.staff_name.ilike(f"%{search}%"),
                Staff.staff_id == search if search.isdigit() else False
            )
        ).all()
    else:
        
        staff = Staff.query.all()

    return render_template(
        "admin/staff.html", staff=staff,search=search)


@app.route("/admin/staff/create_staff", methods=["GET", "POST"])
def create_staff():
    if request.method == "GET":
        return render_template("admin/create_staff.html")
    if request.method == "POST":
        name = request.form.get("staff_name")
        contact_details=request.form.get("contact_details")
        email = request.form.get("email")
        password = request.form.get("password")
        staff = Staff.query.filter_by(email=email).first()
        if staff:
            
            return redirect("/admin/staff/create_staff")
        
        existing_user = User.query.filter_by(email=email).first()

        if existing_user: 
            return redirect("/login")
    
        staff = Staff(staff_name=name, email=email, password=password, contact_details=contact_details)
        db.session.add(staff)
        db.session.commit()

    
        return redirect("/admin/staff")





@app.route("/admin/users")
def admin_users():
    search = request.args.get("search", "")

    if search:
        users = User.query.filter(
            or_(
                User.user_name.ilike(f"%{search}%"),
                User.user_id == search if search.isdigit() else False
            )
        ).all()
    else:
        users = User.query.all()

    return render_template(
        "admin/user.html",
        users=users,
        search=search)


@app.route("/admin/treks")
def admin_treks():
    search = request.args.get("search", "")
    staff=Staff.query.all()
    if search:
        treks = Trek.query.filter(
            or_(
                Trek.trek_name.ilike(f"%{search}%"),
                Trek.trek_id == search if search.isdigit() else False
            )
        ).all()
    else:
        treks = Trek.query.all()

    return render_template(
        "admin/trek.html",
        treks=treks,
        search=search,
        staff=staff)
    

@app.route("/admin/trek/create_trek", methods=["GET", "POST"])
def create_trek():
    staff_members = Staff.query.all()
    if request.method == "GET":
        return render_template("admin/create_trek.html",staff_members=staff_members)
    if request.method == "POST":
        name = request.form.get("trek_name")
        location=request.form.get("location")
        difficulty= request.form.get("difficulty")
        duration = request.form.get("duration")
        available_slots = request.form.get("available_slots")
        staff_id = request.form.get("staff_id")
        trek = Trek.query.filter_by(trek_name=name).first()
        if trek:
            return redirect("/admin/trek/create_trek")
        
        
    
        trek = Trek( trek_name=name,
    location=location,
    difficulty=difficulty,
    duration=duration,
    available_slots=available_slots,
    assigned_staff_id=staff_id if staff_id else None)
        db.session.add(trek)
        db.session.commit()

    
        return redirect("/admin/treks")
    


@app.route("/admin/trek/edit/<int:id>", methods=["GET", "POST"])
def edit_trek(id):
    
    staff_members = Staff.query.all()
    trek = Trek.query.get(id)

    if request.method == "POST":
        trek.trek_name = request.form.get("trek_name")
        trek.location=request.form.get("location")
        trek.difficulty= request.form.get("difficulty")
        trek.duration = request.form.get("duration")
        trek.available_slots = request.form.get("available_slots")
        staff_id = request.form.get("staff_id")
        trek.assigned_staff_id = staff_id if staff_id else None
        db.session.commit()

        return redirect("/admin/treks")
    
    return render_template("admin/edit_trek.html", trek=trek,staff_members=staff_members)

@app.route("/admin/trek/remove/<int:id>")
def remove_trek(id):
    trek = Trek.query.get(id)
    db.session.delete(trek)
    db.session.commit()
    return redirect("/admin/treks")


@app.route("/admin/bookings")
def admin_bookings():

    bookings = Booking.query.order_by(
        Booking.booking_date.desc()
    ).all()

    return render_template(
        "admin/view_bookings.html",
        bookings=bookings
    )

    