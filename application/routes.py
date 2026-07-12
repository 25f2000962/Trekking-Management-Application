from datetime import datetime

from app import app
from .model import db, Admin, User, Staff, Trek, Booking

from flask import (
    render_template,
    request,
    redirect,
    session,
    flash,
    url_for,
)

from sqlalchemy import or_

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "GET":
        return render_template("user/register.html")

    user_name = request.form.get("name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    password = request.form.get("password")

    existing = User.query.filter_by(email=email).first()

    if existing:
        flash("You are already registered. Please login.", "warning")
        return redirect("/login")

    user = User(
        user_name=user_name,
        email=email,
        password=password,
        mobile=phone,
    )

    db.session.add(user)
    db.session.commit()

    flash("Registration successful.", "success")

    return redirect("/login")


# -------------------------------------------------------
# STAFF REGISTER
# -------------------------------------------------------

@app.route("/staff_register", methods=["GET", "POST"])
def staff_register():

    if request.method == "GET":
        return render_template("staff/staff_register.html")

    name = request.form.get("staff_name")
    contact = request.form.get("contact_details")
    email = request.form.get("email")
    password = request.form.get("password")

    existing = Staff.query.filter_by(email=email).first()

    if existing:
        flash("Email already registered.", "warning")
        return redirect("/staff_register")

    staff = Staff(
        staff_name=name,
        contact_details=contact,
        email=email,
        password=password,
    )

    db.session.add(staff)
    db.session.commit()

    flash("Registration successful. Wait for admin approval.", "success")

    return redirect("/login")


# -------------------------------------------------------
# USER / GUIDE LOGIN
# -------------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "GET":
        return render_template("user/login.html")

    email = request.form.get("email")
    password = request.form.get("password")
    role = request.form.get("role")

    session.clear()

    # ---------------- TREKKER ----------------

    if role == "trekker":

        user = User.query.filter_by(email=email).first()

        if not user:
            flash("User not found.", "danger")
            return redirect("/login")

        if user.password != password:
            flash("Incorrect password.", "danger")
            return redirect("/login")

        if user.is_blacklisted:
            flash("Your account is blacklisted.", "danger")
            return redirect("/login")

        session["user_id"] = user.user_id

        

        return redirect("/user_dashboard")

    # ---------------- GUIDE ----------------

    elif role == "guide":

        staff = Staff.query.filter_by(email=email).first()

        if not staff:
            flash("Guide not found.", "danger")
            return redirect("/login")

        if staff.password != password:
            flash("Incorrect password.", "danger")
            return redirect("/login")

        if staff.is_blacklisted:
            flash("You are blacklisted.", "danger")
            return redirect("/login")

        if not staff.is_added:
            flash("Waiting for admin approval.", "warning")
            return redirect("/login")

        session["staff_id"] = staff.staff_id

        return redirect("/staff_dashboard")

    flash("Please select a valid role.", "danger")
    return redirect("/login")


# -------------------------------------------------------
# ADMIN LOGIN
# -------------------------------------------------------

@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():

    if request.method == "GET":
        return render_template("admin/admin_login.html")

    email = request.form.get("email")
    password = request.form.get("password")

    admin = Admin.query.filter_by(email=email).first()

    if not admin or admin.password != password:
        flash("Wrong credentials.", "danger")
        return redirect("/admin_login")

    session.clear()

    session["admin_id"] = admin.id

   

    return redirect("/admin_dashboard")


# -------------------------------------------------------
# USER DASHBOARD
# -------------------------------------------------------

@app.route("/user_dashboard")
def user_dashboard():

    user_id = session.get("user_id")

    if not user_id:
        return redirect("/login")

    user = User.query.get_or_404(user_id)

    location = request.args.get("location", "")
    difficulty = request.args.get("difficulty", "")

    query = Trek.query.filter(
        Trek.available_slots > 0,
        Trek.booking_status == "Open",
        Trek.is_closed == False,
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

    applied = {
        b.trek_id
        for b in Booking.query.filter_by(user_id=user_id).all()
    }

    locations = db.session.query(Trek.location).distinct().all()

    return render_template(
        "user/user_dashboard.html",
        user=user,
        treks=treks,
        applied=applied,
        locations=locations,
        location=location,
        difficulty=difficulty,
    )


# -------------------------------------------------------
# STAFF DASHBOARD
# -------------------------------------------------------

@app.route("/staff_dashboard")
def staff_dashboard():

    staff_id = session.get("staff_id")

    if not staff_id:
        return redirect("/login")

    staff = Staff.query.get_or_404(staff_id)

    if not staff.is_added:
        session.clear()
        flash("Your account is awaiting admin approval.", "warning")
        return redirect("/login")

    # Check if guide is blacklisted
    if staff.is_blacklisted:
        session.clear()
        flash("Your account has been blacklisted.", "danger")
        return redirect("/login")

    treks = Trek.query.filter_by(
        assigned_staff_id=staff_id
    ).all()

    trek_count = len(treks)

    trekker_count = 0

    for trek in treks:
        trekker_count += len(trek.bookings)

    return render_template(
        "staff/staff_dashboard.html",
        staff=staff,
        treks=treks,
        trek_count=trek_count,
        trekker_count=trekker_count,
    )


# -------------------------------------------------------
# ADMIN DASHBOARD
# -------------------------------------------------------

@app.route("/admin_dashboard")
def admin_dashboard():

    admin_id = session.get("admin_id")

    if not admin_id:
        return redirect("/admin_login")

    return render_template(
        "admin/admin_dashboard.html",
        users=User.query.count(),
        staff=Staff.query.count(),
        treks=Trek.query.count(),
        bookings=Booking.query.count(),
    )





@app.route("/admin/users")
def admin_users():

    if "admin_id" not in session:
        return redirect("/admin_login")

    search = request.args.get("search", "")

    if search:
        users = User.query.filter(
            or_(
                User.user_name.ilike(f"%{search}%"),
                User.user_id == int(search) if search.isdigit() else False
            )
        ).all()
    else:
        users = User.query.all()

    return render_template(
        "admin/user.html",
        users=users,
        search=search
    )


@app.route("/admin/users/blacklist/<int:id>")
def blacklist_user(id):

    if "admin_id" not in session:
        return redirect("/admin_login")

    user = User.query.get_or_404(id)

    user.is_blacklisted = True
    user.status = "Blacklisted"

    db.session.commit()

    flash("User blacklisted successfully.", "success")

    return redirect("/admin/users")


@app.route("/admin/users/approve/<int:id>")
def approve_user(id):

    if "admin_id" not in session:
        return redirect("/admin_login")

    user = User.query.get_or_404(id)

    user.is_blacklisted = False
    user.status = "Approved"

    db.session.commit()

    flash("User approved.", "success")

    return redirect("/admin/users")











@app.route("/admin/staff")
def admin_staff():

    if "admin_id" not in session:
        return redirect("/admin_login")

    search = request.args.get("search", "")

    if search:
        staff = Staff.query.filter(
            or_(
                Staff.staff_name.ilike(f"%{search}%"),
                Staff.staff_id == int(search) if search.isdigit() else False
            )
        ).all()
    else:
        staff = Staff.query.all()

    return render_template(
        "admin/staff.html",
        staff=staff,
        search=search
    )


@app.route("/admin/staff/added/<int:id>")
def add_staff(id):

    if "admin_id" not in session:
        return redirect("/admin_login")

    staff = Staff.query.get_or_404(id)

    staff.is_added = True
    staff.status = "Added"

    db.session.commit()

    flash("Guide added successfully.", "success")

    return redirect("/admin/staff")



@app.route("/admin/staff/remove/<int:id>")
def remove_staff(id):

    if "admin_id" not in session:
        return redirect("/admin_login")

    staff = Staff.query.get_or_404(id)

    
    db.session.delete(staff)
    db.session.commit()

    flash("Guide removed.", "warning")

    return redirect("/admin/staff")

@app.route("/admin/staff/approve/<int:id>")
def approve_staff(id):

    if "admin_id" not in session:
        return redirect("/admin_login")

    staff = Staff.query.get_or_404(id)

    staff.is_blacklisted = False
    staff.status = "Approved"

    db.session.commit()

    flash("Guide approved successfully.", "success")

    return redirect("/admin/staff")


@app.route("/admin/staff/blacklist/<int:id>")
def blacklist_staff(id):

    if "admin_id" not in session:
        return redirect("/admin_login")

    staff = Staff.query.get_or_404(id)

    staff.is_blacklisted = True
    staff.status = "Blacklisted"

    db.session.commit()

    flash("Guide blacklisted.", "success")

    return redirect("/admin/staff")


@app.route("/admin/treks")
def admin_treks():

    if "admin_id" not in session:
        return redirect("/admin_login")

    search = request.args.get("search", "")

    staff = Staff.query.filter_by(
        is_added=True,
        is_blacklisted=False
    ).all()

    if search:
        treks = Trek.query.filter(
            or_(
                Trek.trek_name.ilike(f"%{search}%"),
                Trek.trek_id == int(search) if search.isdigit() else False
            )
        ).all()
    else:
        treks = Trek.query.all()

    return render_template(
        "admin/trek.html",
        treks=treks,
        staff=staff,
        search=search,
    )



@app.route("/admin/trek/create_trek", methods=["GET", "POST"])
def create_trek():

    if "admin_id" not in session:
        return redirect("/admin_login")

    staff_members = Staff.query.filter_by(
        is_added=True,
        is_blacklisted=False
    ).all()

    if request.method == "GET":
        return render_template(
            "admin/create_trek.html",
            staff_members=staff_members
        )

    trek = Trek.query.filter_by(
        trek_name=request.form.get("trek_name")
    ).first()

    if trek:
        flash("Trek already exists.", "warning")
        return redirect("/admin/trek/create_trek")

    trek = Trek(
        trek_name=request.form.get("trek_name"),
        location=request.form.get("location"),
        difficulty=request.form.get("difficulty"),
        duration=request.form.get("duration"),
        available_slots=request.form.get("available_slots"),
        assigned_staff_id=request.form.get("staff_id") or None,
    )

    db.session.add(trek)
    db.session.commit()

    flash("Trek created successfully.", "success")

    return redirect("/admin/treks")


@app.route("/admin/trek/edit/<int:id>", methods=["GET", "POST"])
def edit_trek(id):

    if "admin_id" not in session:
        return redirect("/admin_login")

    trek = Trek.query.get_or_404(id)

    staff_members = Staff.query.filter_by(
        is_added=True,
        is_blacklisted=False
    ).all()

    if request.method == "POST":

        trek.trek_name = request.form.get("trek_name")
        trek.location = request.form.get("location")
        trek.difficulty = request.form.get("difficulty")
        trek.duration = request.form.get("duration")
        trek.available_slots = request.form.get("available_slots")
        trek.assigned_staff_id = request.form.get("staff_id") or None

        db.session.commit()

        flash("Trek updated successfully.", "success")

        return redirect("/admin/treks")

    return render_template(
        "admin/edit_trek.html",
        trek=trek,
        staff_members=staff_members
    )



@app.route("/admin/trek/remove/<int:id>")
def remove_trek(id):

    if "admin_id" not in session:
        return redirect("/admin_login")

    trek = Trek.query.get_or_404(id)

    Booking.query.filter_by(trek_id=id).delete()

    db.session.delete(trek)

    db.session.commit()

    flash("Trek removed successfully.", "success")

    return redirect("/admin/treks")



@app.route("/admin/bookings")
def admin_bookings():

    if "admin_id" not in session:
        return redirect("/admin_login")

    bookings = Booking.query.order_by(
        Booking.booking_date.desc()
    ).all()

    return render_template(
        "admin/view_bookings.html",
        bookings=bookings
    )



@app.route("/staff/my_treks/")
def my_treks():

    staff_id = session.get("staff_id")

    if not staff_id:
        return redirect("/login")

    staff = Staff.query.get_or_404(staff_id)

    treks = Trek.query.filter_by(
        assigned_staff_id=staff_id
    ).all()

    return render_template(
        "staff/my_treks.html",
        staff=staff,
        treks=treks
    )



@app.route("/staff/trek/<int:trek_id>")
def view_trek(trek_id):

    staff_id = session.get("staff_id")

    if not staff_id:
        return redirect("/login")

    trek = Trek.query.get_or_404(trek_id)

    if trek.assigned_staff_id != staff_id:
        flash("Unauthorized access.", "danger")
        return redirect("/staff_dashboard")

    return render_template(
        "staff/view_trek.html",
        trek=trek
    )




@app.route("/staff/remove_participant/<int:booking_id>", methods=["POST"])
def remove_participant(booking_id):

    staff_id = session.get("staff_id")

    if not staff_id:
        return redirect("/login")

    booking = Booking.query.get_or_404(booking_id)

    trek = Trek.query.get_or_404(booking.trek_id)

    if trek.assigned_staff_id != staff_id:
        flash("Unauthorized.", "danger")
        return redirect("/staff_dashboard")

    trek.available_slots += 1

    db.session.delete(booking)
    db.session.commit()

    flash("Participant removed.", "success")

    return redirect(url_for("view_trek", trek_id=trek.trek_id))




@app.route("/staff/edit_staff/", methods=["GET", "POST"])
def edit_staff():

    staff_id = session.get("staff_id")

    if not staff_id:
        return redirect("/login")

    staff = Staff.query.get_or_404(staff_id)

    if request.method == "POST":

        staff.staff_name = request.form.get("staff_name")
        staff.contact_details = request.form.get("phone")
        staff.email = request.form.get("email")

        db.session.commit()

        flash("Profile updated.", "success")

        return redirect("/staff_dashboard")

    return render_template(
        "staff/edit_staff.html",
        staff=staff
    )




@app.route("/staff/trek/<int:id>/booking_status", methods=["POST"])
def change_booking_status(id):

    staff_id = session.get("staff_id")

    if not staff_id:
        return redirect("/login")

    trek = Trek.query.get_or_404(id)

    if trek.assigned_staff_id != staff_id:
        flash("Unauthorized.", "danger")
        return redirect("/staff_dashboard")

    trek.booking_status = request.form.get("status")

    db.session.commit()

    flash("Booking status updated.", "success")

    return redirect(url_for("view_trek", trek_id=id))




@app.route("/staff/trek/<int:id>/slots", methods=["GET", "POST"])
def update_slots(id):

    staff_id = session.get("staff_id")

    if not staff_id:
        return redirect("/login")

    trek = Trek.query.get_or_404(id)

    if trek.assigned_staff_id != staff_id:
        flash("Unauthorized.", "danger")
        return redirect("/staff_dashboard")

    if request.method == "POST":

        trek.available_slots = int(request.form.get("slots"))

        db.session.commit()

        flash("Slots updated.", "success")

        return redirect(url_for("view_trek", trek_id=id))

    return render_template(
        "staff/update_slots.html",
        trek=trek
    )




@app.route("/staff/trek/<int:id>/status", methods=["POST"])
def change_trek_status(id):

    staff_id = session.get("staff_id")

    if not staff_id:
        return redirect("/login")

    trek = Trek.query.get_or_404(id)

    if trek.assigned_staff_id != staff_id:
        flash("Unauthorized.", "danger")
        return redirect("/staff_dashboard")

    trek.trek_status = request.form.get("status")

    db.session.commit()

    flash("Trek status updated.", "success")

    return redirect(url_for("view_trek", trek_id=id))



@app.route("/user/apply/<int:trek_id>", methods=["POST"])
def apply_trek(trek_id):

    user_id = session.get("user_id")

    if not user_id:
        return redirect("/login")

    trek = Trek.query.get_or_404(trek_id)

    if trek.booking_status != "Open":
        flash("Bookings are closed.", "warning")
        return redirect("/user_dashboard")

    if trek.available_slots <= 0:
        flash("No slots available.", "danger")
        return redirect("/user_dashboard")

    existing = Booking.query.filter_by(
        trek_id=trek_id,
        user_id=user_id
    ).first()

    if existing:
        flash("You have already applied for this trek.", "warning")
        return redirect("/user_dashboard")

    booking = Booking(
        trek_id=trek_id,
        user_id=user_id
    )

    trek.available_slots -= 1

    db.session.add(booking)
    db.session.commit()

    flash("Booking successful!", "success")

    return redirect("/user_dashboard")




@app.route("/user/edit_profile/<int:id>", methods=["GET", "POST"])
def edit_profile(id):

    user_id = session.get("user_id")

    if not user_id:
        return redirect("/login")

    if id != user_id:
        flash("Unauthorized.", "danger")
        return redirect("/user_dashboard")

    user = User.query.get_or_404(id)

    if request.method == "POST":

        user.user_name = request.form.get("user_name")
        user.email = request.form.get("email")
        user.mobile = request.form.get("mobile")

        db.session.commit()

        flash("Profile updated successfully.", "success")

        return redirect("/user_dashboard")

    return render_template(
        "user/edit_profile.html",
        user=user
    )





@app.route("/user/bookings")
def user_bookings():

    user_id = session.get("user_id")

    if not user_id:
        return redirect("/login")

    bookings = Booking.query.filter_by(
        user_id=user_id
    ).order_by(
        Booking.booking_date.desc()
    ).all()

    return render_template(
        "user/history.html",
        bookings=bookings
    )



@app.route("/logout")
def logout():

    session.clear()

    flash("Logged out successfully.", "success")

    return redirect("/")