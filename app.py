from flask import Flask, render_template, request, session, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///proninchan.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  
db = SQLAlchemy(app)
app.secret_key = 'proniproni322'


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


@app.route('/post-creation')
def create():
    return render_template('post-creation.html')


@app.route('/reg', methods=['POST'])
def reg():
    username = request.form['loginreg']
    email = request.form['emailreg']
    password = request.form['passwordreg']
    if len(password) < 8:
        return jsonify({'answer': False,'message': 'Пароль должен содеражать минимум 8 символов'})
    password = generate_password_hash(password)
    username_occupied =db.session.query(Users).filter_by(username=username).first()
    email_occupied =db.session.query(Users).filter_by(email=email).first()
    if username_occupied:
        return jsonify({'answer': False,'message': 'Имя занято'})
    elif email_occupied:
        return jsonify({'answer': False,'message': 'Почта занята'})
    new_user = Users(username=username, email=email, password=password)
    try:
        db.session.add(new_user)
        db.session.commit()
        session['user'] =  db.session.query(Users).filter_by(username=username).first().id
        return jsonify({'answer': True, 'message': 'Успешно'})
    except Exception as err:
        db.session.rollback()
        return jsonify({'answer': False,'message': 'Возникла ошибка'}) 
    
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main'))

@app.route('/log', methods=['POST'])
def log():
    username = request.form['login']
    password = request.form['password']
    user = db.session.query(Users).filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        session['user']=user.id
        return jsonify({'answer': True, 'message': 'Успешно'})
    else:
        return jsonify({'answer': False,'message': 'Неверный логин или пароль'})

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)