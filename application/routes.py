from app import app
from .model import db, Admin,User,Staff,Trek,Booking
from flask import render_template, request, redirect, session,url_for,flash
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
            flash("You are already registered! Please login.", "warning")
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
        if user.is_blacklisted:
             flash("You are blacklisted")
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
            flash("Wrong credentials","warning ")
            return redirect("/admin_login")
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

from datetime import datetime

@app.route("/user_dashboard")
def user_dashboard():

    user_id = session.get("user_id")

    if not user_id:
        return redirect("/login")

    location = request.args.get("location", "")
    difficulty = request.args.get("difficulty", "")

    query = Trek.query.filter(
        Trek.available_slots > 0,
        Trek.booking_status == "Open",
        Trek.is_closed == False
    )
                            
    if location:
        query = query.filter(
            Trek.location.ilike(f"%{location}%")
        )

    if difficulty:
        query = query.filter(
            Trek.difficulty == difficulty
        )

    treks = query.all()

    user = User.query.get(user_id)

    applied = {
        a.trek_id
        for a in Booking.query.filter_by(user_id=user_id).all()
    }

    locations = db.session.query(Trek.location).distinct().all()

    return render_template(
        "user/user_dashboard.html",
        user=user,
        treks=treks,
        locations=locations,
        location=location,
        difficulty=difficulty,
        applied=applied
    )

@app.route("/staff_dashboard")
def staff_dashboard():

    staff_id = session.get("user_id")

    if not staff_id:
        return redirect("/login")

    staff = Staff.query.get(staff_id)

    treks = Trek.query.filter_by(assigned_staff_id=staff_id).all()
    trek_count = len(treks)
    trekker_count = 0

    for trek in treks:
        trekker_count += len(trek.bookings)
    return render_template(
        "staff/staff_dashboard.html",
        staff=staff,
        treks=treks,
        trek_count=trek_count,
        trekker_count=trekker_count
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
    staff.status = "Blacklisted"
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
            flash("Trek already registered")
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
    bookings = Booking.query.filter_by(trek_id=id).all()

    for b in bookings:
        db.session.delete(b)
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


@app.route("/staff/my_treks/")
def my_treks():

    
    staff_id = session.get("user_id")

    
    staff = Staff.query.get(staff_id)

    treks = Trek.query.filter_by(assigned_staff_id=staff_id).all()
    
    return render_template(
        "staff/my_treks.html",
        staff=staff,
        treks=treks,
    )


@app.route("/staff/trek/<int:trek_id>")
def view_trek(trek_id):

    staff_id = session.get("user_id")

    if not staff_id:
        return redirect("/login")

    trek = Trek.query.get_or_404(trek_id)

    # Security check: guide can only view their own treks
    if trek.assigned_staff_id != staff_id:
        return "Unauthorized", 403

    return render_template(
        "staff/view_trek.html",
        trek=trek,
        
    )

@app.route("/staff/remove_participant/<int:booking_id>",
           methods=["POST"])
def remove_participant(booking_id):

    booking = Booking.query.get_or_404(booking_id)

    trek_id = booking.trek_id

    db.session.delete(booking)
    db.session.commit()

    return redirect(url_for("view_trek", trek_id=trek_id))
    
@app.route("/staff/edit_staff/",methods=["Get","Post"])
def edit_staff():
    staff_id = session.get("user_id")
    staff=Staff.query.get(staff_id)

    if request.method == "POST":
        staff.staff_name = request.form.get("staff_name")
        staff.contact_details=request.form.get("phone")
        staff.email= request.form.get("email")
        
    
        db.session.commit()

        return redirect("/staff_dashboard")
    
    return render_template("staff/edit_staff.html", staff=staff)



@app.route("/staff/trek/<int:id>/booking_status", methods=["POST"])
def change_booking_status(id):

    trek = Trek.query.get_or_404(id)

    trek.booking_status = request.form.get("status")

    db.session.commit()

    return redirect(url_for("view_trek", trek_id=id))


@app.route("/staff/trek/<int:id>/slots", methods=["GET","POST"])
def update_slots(id):

    trek = Trek.query.get_or_404(id)

    if request.method == "POST":
        trek.available_slots = request.form.get("slots")
        db.session.commit()

        
        return redirect(url_for("view_trek", trek_id=id))

    return render_template(
        "staff/update_slots.html",
        trek=trek
    )

@app.route("/staff/trek/<int:id>/status", methods=["POST"])
def change_trek_status(id):

    trek = Trek.query.get_or_404(id)

    if trek.assigned_staff_id != session.get("user_id"):
        return "Unauthorized", 403

    trek.trek_status = request.form.get("status")

    db.session.commit()

    return redirect(url_for("view_trek", trek_id=id))



@app.route("/user/apply/<int:trek_id>", methods=["POST"])
def apply_trek(trek_id):

    
    user_id = session.get("user_id")

    existing = Booking.query.filter_by(
        trek_id=trek_id,
        user_id=user_id
    ).first()


    booking = Booking(
        trek_id=trek_id,
        user_id=user_id
        )

    db.session.add(booking)
    db.session.commit()

       

    return redirect("/user_dashboard")


@app.route("/user/edit_profile/<int:id>", methods=["GET", "POST"])
def edit_profile(id):

    user_id = session.get("user_id")

    if not user_id:
        return redirect("/login")

    if user_id != id:
        return "Unauthorized", 403

    user = User.query.get_or_404(id)

    if request.method == "POST":
        user.user_name = request.form.get("user_name")
        user.email = request.form.get("email")
        user.mobile = request.form.get("mobile")

        db.session.commit()

        return redirect("/user_dashboard")

    return render_template(
        "user/edit_profile.html",
        user=user
    )


@app.route("/user/bookings")
def user_bookings():

    user_id = session.get("user_id")

    bookings = Booking.query.filter_by(
        user_id=user_id
    ).all()

    return render_template(
        "user/history.html",
        bookings=bookings
    )