from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///proninchan.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  
db = SQLAlchemy(app)

class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True, nullable=False)
    photo = db.Column(db.BLOB)
    email = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(30), nullable=False)
    access = db.Column(db.String(64), nullable=False, default='user')

@app.route('/')
def main():
    return render_template('main.html')

if __name__ == "__main__":
    app.run(debug=True)