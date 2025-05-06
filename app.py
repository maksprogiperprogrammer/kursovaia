from flask import Flask, render_template, request, session, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

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
    all_posts = db.relationship("ForumPosts", backref="user_author", cascade="all, delete-orphan")
    all_comments = db.relationship("ForumComments", backref="user_author")

class ForumSections(db.Model):
    __tablename__ = 'forum_sections'
    id = db.Column(db.Integer, primary_key=True)
    section = db.Column(db.String(32), unique=True, nullable=False)
    category = db.relationship('ForumCategory', backref='section', lazy=True)
    posts = db.relationship('ForumPosts', backref='section', lazy=True)

class ForumCategory(db.Model):
    __tablename__ = 'forum_categories'
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(32), unique=True, nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('forum_sections.id'), nullable=False)
    posts = db.relationship('ForumPosts', backref='category', lazy=True)

class ForumPosts(db.Model):
    __tablename__ = 'forum_posts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    theme = db.Column(db.String(124), nullable=False)
    text = db.Column(db.Text, nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('forum_sections.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('forum_categories.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    user = db.relationship("Users", backref="posts")
    sections = db.relationship("ForumSections")
    categories = db.relationship("ForumCategory")
    all_comments = db.relationship("ForumComments", backref="forum_post", cascade="all, delete-orphan")

class ForumComments(db.Model):
    __tablename__ = 'forum_comments'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    post_id = db.Column(db.Integer, db.ForeignKey('forum_posts.id'), nullable=False)
    user = db.relationship("Users", backref="comments")
    post = db.relationship('ForumPosts', backref='comments')

class BannedUsers(db.Model):
    __tablename__ = 'banned_users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, nullable=False)

@app.route('/get-admin')
def getAdmin():
    if 'user' in session:
        try:
            user = Users.query.filter_by(id=session['user']).first()
            user.access = 'admin'
            db.session.commit()
            return redirect(url_for('main'))
        except:
            return redirect(url_for('main'))

@app.route('/')
def main():
    new_posts = ForumPosts.query.order_by(ForumPosts.created_at.desc()).limit(5).all()
    if 'user' in session:
        try:
            access = (Users.query.filter_by(id=session['user']).first()).access
        except:
            return redirect(url_for('logout'))
        return render_template('main.html', new_posts = new_posts, access=access)
    else:
        return render_template('main.html', new_posts = new_posts)

@app.route('/profile')
def profile():
    if 'user' in session:
        user = Users.query.filter_by(id=session['user']).first()
        user_posts =  ForumPosts.query.filter_by(user_id=session['user']).order_by(ForumPosts.created_at.desc()).limit(5).all()
        user_comments = ForumComments.query.filter_by(user_id=session['user']).order_by(ForumComments.created_at.desc()).limit(5).all()
        c_total = ForumComments.query.filter_by(user_id=session['user']).count()
        p_total = ForumPosts.query.filter_by(user_id=session['user']).count()
        return render_template('profile.html', user = user, posts=user_posts, 
                               comments=user_comments, c_total=c_total,p_total=p_total)
    return render_template('profile.html')

@app.route('/user_posts')
def user_posts():
    if 'user' in session:
        user_posts =  ForumPosts.query.filter_by(user_id=session['user']).order_by(ForumPosts.created_at.desc()).all()
        return render_template('user_posts.html', posts=user_posts)
    return render_template('profile.html')

@app.route('/user_comments')
def user_comments():
    if 'user' in session:
        user_comments = ForumComments.query.filter_by(user_id=session['user']).order_by(ForumComments.created_at.desc()).all()
        return render_template('user_comments.html', comments=user_comments)
    return render_template('profile.html')

@app.route('/ban_user/<int:user_id>', methods=['DELETE'])
def ban_user(user_id):
    if 'user' in session:
        userToBan = Users.query.filter_by(id=user_id).first()
        if not userToBan:
            return jsonify({'message': 'Нет такого пользователя'}) 
        if (Users.query.filter_by(id=session['user']).first()).access =='admin':
            db.session.delete(userToBan)
            userToBan = BannedUsers(email=userToBan.email)
            db.session.add(userToBan)
            db.session.commit()
            return jsonify({'message': 'Успешно забанен'}) 

@app.route('/delete_comment/<int:id>', methods=['DELETE'])
def delete_comment(id):
    if 'user' in session:
        comment = ForumComments.query.filter_by(id=id).first()
        if not comment:
            return jsonify({'answer': False,'message': 'Нет такого комментария'}) 
        if comment.user_id == session['user'] or (Users.query.filter_by(id=session['user']).first()).access =='admin':
            db.session.delete(comment)
            db.session.commit()
            return jsonify({'answer': True,'message': 'Успешно удалено'}) 
        
@app.route('/delete_post/<int:id>', methods=['DELETE'])
def delete_post(id):
    if 'user' in session:
        post = ForumPosts.query.filter_by(id=id).first()
        if not post:
            return jsonify({'answer': False,'message': 'Нет такого поста'}) 
        if post.user_id == session['user'] or (Users.query.filter_by(id=session['user']).first()).access =='admin':
            db.session.delete(post)
            db.session.commit()
            return jsonify({'answer': True,'message': 'Успешно удалено'}) 
        
@app.route('/edit_post/<int:id>', methods=['POST'])
def edit_post(id):
    if 'user' in session:
        new = request.get_json()
        new_theme = new.get('theme')
        new_text = new.get('text')
        post = ForumPosts.query.filter_by(id=id).first()
        if not post:
            return jsonify({'answer': False,'message': 'Нет такого поста'}) 
        if post.user_id == session['user']:
            post.theme = new_theme
            post.text = new_text
            db.session.commit()
            return jsonify({'answer': True}) 
        
@app.route('/edit_comment/<int:id>', methods=['POST'])
def edit_comment(id):
    if 'user' in session:
        new = request.get_json()
        new_text = new.get('text')
        comment = ForumComments.query.filter_by(id=id).first()
        if not comment:
            return jsonify({'answer': False,'message': 'Нет такого комментария'}) 
        if comment.user_id == session['user']:
            comment.text = new_text
            db.session.commit()
            return jsonify({'answer': True}) 

@app.route('/posts')
def posts():
    sections = ForumSections.query.all()
    category = ForumCategory.query.all()
    posts = ForumPosts.query.all()
    if 'user' in session:
        try:
            access = (Users.query.filter_by(id=session['user']).first()).access
        except:
            return redirect(url_for('logout'))
        return render_template('posts.html', posts=posts, category=category, sections=sections, access=access)
    else:
        return render_template('posts.html', posts=posts, category=category, sections=sections)

@app.route('/post/<int:post>', methods=['GET','POST'])
def post(post):
    comments = ForumComments.query.filter_by(post_id=post).order_by(ForumComments.created_at.desc()).all()
    sections = ForumSections.query.all()
    category = ForumCategory.query.all()
    posts = ForumPosts.query.all()
    post = ForumPosts.query.get_or_404(post)
    if 'user' in session:
        try:
            access = (Users.query.filter_by(id=session['user']).first()).access
        except:
            return redirect(url_for('logout'))
        return render_template('post.html', post=post, posts=posts, category=category, sections=sections, comments=comments, access=access)
    else:
        return render_template('post.html', post=post, posts=posts, category=category, sections=sections, comments=comments)

@app.route('/post-creation')
def create():
    if 'user' in session:
        sections = ForumSections.query.all()
        if not sections:
            sections = ('Электроника', "Игры", "Общение")
            for i in sections:
                new_section = ForumSections(section=i)
                db.session.add(new_section)
            db.session.commit()
        category = ForumCategory.query.all()
        if not category:
            category1 = ('Микроволновки', "Ноутбуки", "Пылесосы")
            category2 = ('Экшен', "Стратегии", "2Д")
            category3 = ('Еда', "Спорт", "Новости")
            for i in category1:
                new_category = ForumCategory(category=i, section_id=1)
                db.session.add(new_category)
            for i in category2:
                new_category = ForumCategory(category=i, section_id=2)
                db.session.add(new_category)
            for i in category3:
                new_category = ForumCategory(category=i, section_id=3)
                db.session.add(new_category)
            db.session.commit()
        return render_template('post-creation.html', category=category, sections=sections)
    return render_template('post-creation.html')

@app.route('/create', methods=['POST'])
def create_post():
    if 'user' in session:
        section = request.form['post-section']
        category = request.form['post-category']
        theme = request.form['post-title']
        text = request.form['post-content']
        user = session['user']
        section_exist = ForumSections.query.filter_by(id=section).first()
        category_exist = ForumCategory.query.filter_by(id=category).first()
        if not section_exist:
            return jsonify({'answer': False,'message': 'Выберите раздел'}) 
        elif not category_exist:
            return jsonify({'answer': False,'message': 'Выберите категорию'}) 
        elif not theme.strip():
            return jsonify({'answer': False,'message': 'Создайте заголовок'}) 
        elif not text.strip():
            return jsonify({'answer': False,'message': 'Напишите текст'}) 
        new_post = ForumPosts(user_id=user, theme=theme, text=text, section_id=section, category_id=category)
        try:
            db.session.add(new_post)
            db.session.commit()
            return jsonify({'answer': True,'message': 'Пост успешно создан'})
        except Exception as err:
            db.session.rollback()
            return jsonify({'answer': False,'message': 'Возникла ошибка'}) 

@app.route('/comment', methods=['POST'])
def comment():
    if 'user' in session:
        page = request.form['post']
        comment = request.form['comment']

        if not page.strip():
            return jsonify({'answer': False,'message': 'Возникла ошибка'}) 
        elif not comment.strip():
            return jsonify({'answer': False,'message': 'Напишите текст'}) 
        
        new_comment = ForumComments(user_id=session['user'], text=comment, post_id=page)
        try:
            db.session.add(new_comment)
            db.session.commit()
            return jsonify({'answer': True,'message': 'Комментарий опубликован'})
        except Exception as err:
            db.session.rollback()
            return jsonify({'answer': False,'message': 'Возникла ошибка'}) 

@app.route('/reg', methods=['POST'])
def reg():
    username = request.form['loginreg']
    email = request.form['emailreg']
    isBanned = BannedUsers.query.filter_by(email=email).first()
    if isBanned:
        return jsonify({'answer': False,'message': 'Эта почта заблокирована'})
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