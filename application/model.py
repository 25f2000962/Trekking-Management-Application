
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime 
db=SQLAlchemy()

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100),unique=True, nullable = False)
    password=db.Column(db.String(200),nullable=False)

class User(db.Model):
    user_id=db.Column(db.Integer,primary_key=True)
    user_name = db.Column(db.String(100),nullable = False)
    email=db.Column(db.String(100),unique=True, nullable=False)
    password=db.Column(db.String(200),nullable=False)
    mobile = db.Column(db.String(15), nullable=False)
    is_blacklisted = db.Column(db.Boolean, default=False)
    created_at= db.Column(db.DateTime, default=datetime.utcnow)
    status=db.Column(db.String,default="Approved" )
    bookings = db.relationship("Booking", backref="user")

class Staff(db.Model):
    staff_id=db.Column(db.Integer,primary_key=True)
    staff_name = db.Column(db.String, nullable = False)
    contact_details=db.Column(db.String(15))
    
    status=db.Column(db.String,default="Pending" )
    email = db.Column(db.String(100), unique=True,nullable = False)
    password = db.Column(db.String(100), nullable=False)
    is_added = db.Column(db.Boolean, default=False)
    is_blacklisted = db.Column(db.Boolean, default=False)
    treks=db.relationship("Trek",backref="staff")
class Booking(db.Model):
    booking_id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey("user.user_id"),nullable = False)
    trek_id=db.Column(db.Integer,db.ForeignKey("trek.trek_id"), nullable = False)
    booking_date=db.Column(db.DateTime,default=datetime.utcnow, nullable=False)
    status=db.Column(db.String,default="Booked")


class Trek(db.Model):
    trek_id=db.Column(db.Integer,primary_key=True)
    trek_name = db.Column(db.String,nullable = False)
    location = db.Column(db.String,nullable = False)
    difficulty = db.Column(db.String,nullable = False)
    duration =db.Column(db.Integer)
    available_slots =db.Column(db.Integer, nullable=False)
    assigned_staff_id =db.Column(db.Integer,db.ForeignKey("staff.staff_id"), nullable=True)
    status=db.Column(db.String(100),default="Open")
    start_date=db.Column(db.DateTime)
    end_date=db.Column(db.DateTime)
    payment_status = db.Column(db.String,default="Pending")
    is_closed = db.Column(db.Boolean, default=False)
    created_at =  db.Column(db.DateTime, default=datetime.utcnow)
    bookings = db.relationship("Booking", backref="trek")