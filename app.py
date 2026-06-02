from flask import Flask , render_template
from application.model import db 

def create_app():
    app=Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///mydb.sqlite3"
    app.secret_key = "my_secret_key_123"
    db.init_app(app)
    app.app_context().push()
    return app

app=create_app()

from application.routes import * 
from application.initial_data import * 

if __name__ == "__main__":
    app.run(debug=True)