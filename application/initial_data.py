from .model import db, Admin,User,Staff,Trek,Booking
from app import app


with app.app_context():
    print("Before create_all")
    db.create_all()
    print("After create_all")


    if not db.session.query(Admin).first():
        admin=Admin(email="admin@g.com",password="pass")
        db.session.add(admin)
        db.session.commit()


    
    if not db.session.query(User).first():
        user1=User(user_name="shri",email="shri@g.com",password="pass",mobile="1234567890")
        user2=User(user_name="mayank",email="mayank@g.com",password="pass",mobile="1234567890")
        db.session.add_all([user1,user2])
        db.session.commit()
    
    
    if not db.session.query(Staff).first():
        staff1=Staff(staff_name="sam",email="sam@g.com",password="pass")
        staff2=Staff(staff_name="ran",email="ran@g.com",password="pass")
        db.session.add_all([staff1,staff2])
        db.session.commit()

    
    if not db.session.query(Trek).first():
        trek1=Trek(trek_name="japan",location="hgj",available_slots=100,difficulty="Easy",assigned_staff_id=1)
        trek2=Trek(trek_name="kathmandu",location="hgj",available_slots=100,difficulty="Easy",assigned_staff_id=2)
        db.session.add_all([trek1,trek2])
        db.session.commit()
