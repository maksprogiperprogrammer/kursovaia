from flask import Flask, render_template, request, session, jsonify, redirect, url_for
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import os

# Создаём экземпляр Flask-приложения
app = Flask(__name__)

# Конфигурация базы данных SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///proninchan.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  

# Папка для загрузки изображений (фото пользователей)
app.config['UPLOAD_FOLDER'] = 'static/img'

# Инициализация расширения SQLAlchemy
db = SQLAlchemy(app)

# Секретный ключ для сессий
app.secret_key = 'proniproni322'

# Настройка миграций базы данных
migrate = Migrate(app, db)


# ----------------------------------------
# Определение моделей для базы данных
# ----------------------------------------

class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)                                 # Уникальный идентификатор пользователя
    username = db.Column(db.String(32), unique=True, nullable=False)             # Логин пользователя (уникальный)
    photo = db.Column(db.String(124))                                            # Путь до фото пользователя
    email = db.Column(db.String(64), unique=True, nullable=False)                # Электронная почта (уникальная)
    password = db.Column(db.String(30), nullable=False)                          # Захешированный пароль
    access = db.Column(db.String(64), nullable=False, default='user')            # Роль пользователя (user или admin)
    
    # Связь «один ко многим» с постами: у пользователя могут быть несколько таких записей
    all_posts = db.relationship("ForumPosts", backref="user_author", cascade="all, delete-orphan")
    # Связь «один ко многим» с комментариями
    all_comments = db.relationship("ForumComments", backref="user_author")


class ForumSections(db.Model):
    __tablename__ = 'forum_sections'
    id = db.Column(db.Integer, primary_key=True)                                 # Идентификатор раздела форума
    section = db.Column(db.String(32), unique=True, nullable=False)              # Название раздела
    
    # Связь «один ко многим» с категориями внутри раздела
    category = db.relationship('ForumCategory', backref='section', lazy=True, cascade="all, delete-orphan")
    # Связь «один ко многим» с постами внутри раздела
    posts = db.relationship('ForumPosts', backref='section', lazy=True, cascade="all, delete-orphan")


class ForumCategory(db.Model):
    __tablename__ = 'forum_categories'
    id = db.Column(db.Integer, primary_key=True)                                 # Идентификатор категории
    category = db.Column(db.String(32), unique=True, nullable=False)             # Название категории
    section_id = db.Column(db.Integer, db.ForeignKey('forum_sections.id'), nullable=False)  # Внешний ключ на раздел
    
    # Связь «один ко многим» с постами внутри категории
    posts = db.relationship('ForumPosts', backref='category', lazy=True, cascade="all, delete-orphan")


class ForumPosts(db.Model):
    __tablename__ = 'forum_posts'
    id = db.Column(db.Integer, primary_key=True)                                 # Идентификатор поста
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)   # Внешний ключ на автора (пользователя)
    theme = db.Column(db.String(124), nullable=False)                             # Тема/заголовок поста
    text = db.Column(db.Text, nullable=False)                                     # Текст поста
    section_id = db.Column(db.Integer, db.ForeignKey('forum_sections.id'), nullable=False)  # Внешний ключ на раздел
    category_id = db.Column(db.Integer, db.ForeignKey('forum_categories.id'), nullable=False)  # Внешний ключ на категорию
    created_at = db.Column(db.DateTime, default=datetime.now)                     # Дата и время создания
    
    # Связи для удобного доступа из кода:
    user = db.relationship("Users", backref="posts")                              # Автор поста
    sections = db.relationship("ForumSections")                                    # Раздел поста
    categories = db.relationship("ForumCategory")                                  # Категория поста
    
    # «Один ко многим» — к каждому посту могут быть комментарии
    all_comments = db.relationship("ForumComments", backref="forum_post", cascade="all, delete-orphan")


class ForumComments(db.Model):
    __tablename__ = 'forum_comments'
    id = db.Column(db.Integer, primary_key=True)                                 # Идентификатор комментария
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)    # Внешний ключ на пользователя-автора
    text = db.Column(db.Text, nullable=False)                                     # Текст комментария
    created_at = db.Column(db.DateTime, default=datetime.now)                     # Дата и время создания
    post_id = db.Column(db.Integer, db.ForeignKey('forum_posts.id'), nullable=False)  # Внешний ключ на пост
    
    # Связи для удобного доступа:
    user = db.relationship("Users", backref="comments")                           # Пользователь-автор комментария
    post = db.relationship('ForumPosts', backref='comments')                       # Пост, к которому относится комментарий


class BannedUsers(db.Model):
    __tablename__ = 'banned_users'
    id = db.Column(db.Integer, primary_key=True)                                  # Идентификатор забаненного пользователя
    email = db.Column(db.String(64), unique=True, nullable=False)                 # Почта заблокированного пользователя


# ----------------------------------------
# Маршруты (роутинги) приложения
# ----------------------------------------

@app.route('/get-admin')
def getAdmin():
    """
    Маршрут для выдачи роли 'admin' пользователю в сессии.
    Доступен только если есть пользователь в сессии.
    """
    if 'user' in session:
        try:
            user = Users.query.filter_by(id=session['user']).first()
            user.access = 'admin'
            db.session.commit()
        except:
            db.session.rollback()
        # После попытки обновления доступа возвращаемся на главную
        return redirect(url_for('main'))


@app.route('/')
def main():
    """
    Главная страница.
    Показывает 5 самых свежих постов форума.
    Если пользователь в сессии, передаём его роль (access) в шаблон.
    """
    # Получаем 5 самых свежих постов
    new_posts = ForumPosts.query.order_by(ForumPosts.created_at.desc()).limit(5).all()

    if 'user' in session:
        try:
            # Узнаём роль текущего пользователя
            access = (Users.query.filter_by(id=session['user']).first()).access
        except:
            # Если возникает ошибка, например, пользователь удалён, разлогиниваем
            return redirect(url_for('logout'))
        return render_template('main.html', new_posts=new_posts, access=access)
    else:
        return render_template('main.html', new_posts=new_posts)


@app.route('/profile')
def profile():
    """
    Страница профиля пользователя.
    Если пользователь в сессии, показываем его данные, последние 5 постов и комментариев,
    а также общее количество постов и комментариев.
    Иначе просто рендерим шаблон без данных.
    """
    if 'user' in session:
        try:
            access = (Users.query.filter_by(id=session['user']).first()).access
        except:
            return redirect(url_for('logout'))
        user = Users.query.filter_by(id=session['user']).first()

        # Последние 5 постов этого пользователя
        user_posts = ForumPosts.query.filter_by(user_id=session['user']).order_by(
            ForumPosts.created_at.desc()
        ).limit(5).all()

        # Последние 5 комментариев этого пользователя
        user_comments = ForumComments.query.filter_by(user_id=session['user']).order_by(
            ForumComments.created_at.desc()
        ).limit(5).all()

        # Общее количество комментариев и постов пользователя
        c_total = ForumComments.query.filter_by(user_id=session['user']).count()
        p_total = ForumPosts.query.filter_by(user_id=session['user']).count()

        return render_template(
            'profile.html',
            user=user,
            posts=user_posts,
            comments=user_comments,
            c_total=c_total,
            p_total=p_total,
            access=access
        )
    # Если нет пользователя в сессии, показываем пустую форму профиля
    return render_template('profile.html')


@app.route('/set_photo', methods=['POST'])
def set_photo():
    """
    Маршрут для загрузки фото пользователя.
    Ожидает файл в поле 'photo'.
    Если фото уже было загружено ранее, удаляет старое.
    """
    if 'user' in session:
        try:
            user = Users.query.filter_by(id=session['user']).first()
            if not user:
                return jsonify({'answer': False, 'message': 'Пользователь не найден'})

            # Если в запросе нет файлов, возвращаем ошибку
            if 'photo' not in request.files:
                return jsonify({'answer': False, 'message': 'Нет файла'})

            file = request.files.get('photo')

            # Если у пользователя уже есть фото, удаляем старый файл
            if file and user.photo:
                old_filepath = os.path.join(app.config['UPLOAD_FOLDER'], os.path.basename(user.photo))
                if os.path.exists(old_filepath):
                    os.remove(old_filepath)

            # Проверка, выбрано ли имя файла
            if not file or file.filename == '':
                return jsonify({'answer': False, 'message': 'Нет выбранного файла'})

            # Сохраняем файл в папку UPLOAD_FOLDER
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Обновляем путь к фото в профиле пользователя
            user.photo = 'img/' + filename
            db.session.commit()
            return jsonify({'answer': True, 'message': 'Фотография успешно загружена'})
        except:
            db.session.rollback()
            return jsonify({'answer': False, 'message': 'Ошибка при загрузке'})


@app.route('/user_posts')
def user_posts():
    """
    Страница со всеми постами текущего пользователя.
    Если в сессии нет пользователя — отдаем шаблон профиля.
    """
    if 'user' in session:
        try:
            access = (Users.query.filter_by(id=session['user']).first()).access
        except:
            return redirect(url_for('logout'))
        user_posts = ForumPosts.query.filter_by(
            user_id=session['user']
        ).order_by(ForumPosts.created_at.desc()).all()
        return render_template('user_posts.html', posts=user_posts, access=access)
    return render_template('profile.html')


@app.route('/user_comments')
def user_comments():
    """
    Страница со всеми комментариями текущего пользователя.
    Если в сессии нет пользователя — отдаем шаблон профиля.
    """
    if 'user' in session:
        try:
            access = (Users.query.filter_by(id=session['user']).first()).access
        except:
            return redirect(url_for('logout'))
        user_comments = ForumComments.query.filter_by(
            user_id=session['user']
        ).order_by(ForumComments.created_at.desc()).all()
        return render_template('user_comments.html', comments=user_comments, access=access)
    return render_template('profile.html')


@app.route('/ban_user/<int:user_id>', methods=['DELETE'])
def ban_user(user_id):
    """
    Маршрут для бана пользователя (админом).
    Удаляет запись из Users и добавляет email в таблицу BannedUsers.
    """
    if 'user' in session:
        userToBan = Users.query.filter_by(id=user_id).first()
        if not userToBan:
            return jsonify({'message': 'Нет такого пользователя'})
        # Проверяем, что текущий пользователь — админ
        if (Users.query.filter_by(id=session['user']).first()).access == 'admin':
            db.session.delete(userToBan)
            userToBan = BannedUsers(email=userToBan.email)
            db.session.add(userToBan)
            db.session.commit()
            return jsonify({'message': 'Успешно забанен'})


@app.route('/delete_comment/<int:id>', methods=['DELETE'])
def delete_comment(id):
    """
    Удаление комментария.
    Пользователь может удалить только свой комментарий, админ — любой.
    """
    if 'user' in session:
        comment = ForumComments.query.filter_by(id=id).first()
        if not comment:
            return jsonify({'answer': False, 'message': 'Нет такого комментария'})
        # Проверяем авторство или права админа
        if comment.user_id == session['user'] or (Users.query.filter_by(id=session['user']).first()).access == 'admin':
            db.session.delete(comment)
            db.session.commit()
            return jsonify({'answer': True, 'message': 'Успешно удалено'})


@app.route('/delete_post/<int:id>', methods=['DELETE'])
def delete_post(id):
    """
    Удаление поста.
    Пользователь может удалить только свой пост, админ — любой.
    """
    if 'user' in session:
        post = ForumPosts.query.filter_by(id=id).first()
        if not post:
            return jsonify({'answer': False, 'message': 'Нет такого поста'})
        # Проверяем авторство или права админа
        if post.user_id == session['user'] or (Users.query.filter_by(id=session['user']).first()).access == 'admin':
            db.session.delete(post)
            db.session.commit()
            return jsonify({'answer': True, 'message': 'Успешно удалено'})


@app.route('/edit_post/<int:id>', methods=['POST'])
def edit_post(id):
    """
    Редактирование поста (только автор может редактировать).
    Получает JSON с новыми значениями 'theme' и 'text'.
    """
    if 'user' in session:
        new = request.get_json()
        new_theme = new.get('theme')
        new_text = new.get('text')
        post = ForumPosts.query.filter_by(id=id).first()
        if not post:
            return jsonify({'answer': False, 'message': 'Нет такого поста'})
        # Проверяем, что текущий пользователь — автор
        if post.user_id == session['user']:
            post.theme = new_theme
            post.text = new_text
            db.session.commit()
            return jsonify({'answer': True})


@app.route('/edit_comment/<int:id>', methods=['POST'])
def edit_comment(id):
    """
    Редактирование комментария (только автор может редактировать).
    Получает JSON с новым 'text'.
    """
    if 'user' in session:
        new = request.get_json()
        new_text = new.get('text')
        comment = ForumComments.query.filter_by(id=id).first()
        if not comment:
            return jsonify({'answer': False, 'message': 'Нет такого комментария'})
        # Проверяем, что текущий пользователь — автор
        if comment.user_id == session['user']:
            comment.text = new_text
            db.session.commit()
            return jsonify({'answer': True})


@app.route('/create-section', methods=['POST'])
def create_section():
    """
    Создание нового раздела форума (только админ).
    Ожидает поле 'create-section' с названием нового раздела.
    """
    if 'user' in session and (Users.query.filter_by(id=session['user']).first()).access == 'admin':
        section = request.form['create-section']
        if not section:
            return jsonify({'answer': False, 'message': 'Впишите название секции'})
        new_section = ForumSections(section=section)
        try:
            db.session.add(new_section)
            db.session.commit()
            return jsonify({'answer': True, 'message': 'Успешно'})
        except:
            db.session.rollback()
            return jsonify({'answer': False, 'message': 'Возникла ошибка'})


@app.route('/create-category', methods=['POST'])
def create_category():
    """
    Создание новой категории внутри раздела (только админ).
    Ожидает поля 'create-category' (название) и 'create-category-section' (id раздела).
    """
    if 'user' in session and (Users.query.filter_by(id=session['user']).first()).access == 'admin':
        category = request.form['create-category']
        section = request.form['create-category-section']
        if not category:
            return jsonify({'answer': False, 'message': 'Впишите название категории'})
        if not section:
            return jsonify({'answer': False, 'message': 'Выберите секцию'})
        new_category = ForumCategory(category=category, section_id=section)
        try:
            db.session.add(new_category)
            db.session.commit()
            return jsonify({'answer': True, 'message': 'Успешно'})
        except:
            db.session.rollback()
            return jsonify({'answer': False, 'message': 'Возникла ошибка'})


@app.route('/delete-section', methods=['POST'])
def delete_section():
    """
    Удаление раздела (только админ).
    Ожидает поле 'delete-section' с id раздела для удаления.
    """
    if 'user' in session and (Users.query.filter_by(id=session['user']).first()).access == 'admin':
        section = request.form['delete-section']
        if not section:
            return jsonify({'answer': False, 'message': 'Секция не найдена'})
        try:
            delete_section = ForumSections.query.filter_by(id=section).first()
            db.session.delete(delete_section)
            db.session.commit()
            return jsonify({'answer': True, 'message': 'Успешно'})
        except:
            db.session.rollback()
            return jsonify({'answer': False, 'message': 'Возникла ошибка'})


@app.route('/delete-category', methods=['POST'])
def delete_category():
    """
    Удаление категории (только админ).
    Ожидает поле 'delete-category' с id категории для удаления.
    """
    if 'user' in session and (Users.query.filter_by(id=session['user']).first()).access == 'admin':
        category = request.form['delete-category']
        if not category:
            return jsonify({'answer': False, 'message': 'Категория не найдена'})
        try:
            delete_category = ForumCategory.query.filter_by(id=category).first()
            db.session.delete(delete_category)
            db.session.commit()
            return jsonify({'answer': True, 'message': 'Успешно'})
        except:
            db.session.rollback()
            return jsonify({'answer': False, 'message': 'Возникла ошибка'})


@app.route('/posts')
def posts():
    """
    Страница со списком всех постов форума.
    Подготавливаем данные для отображения: все разделы, категории и посты.
    Если пользователь в сессии — добавляем в шаблон его роль.
    """
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


@app.route('/post/<int:post>', methods=['GET', 'POST'])
def post(post):
    """
    Просмотр одного поста по id.
    Выводим пост, список комментариев, а также список всех разделов и категорий.
    Если пользователь в сессии — передаём его роль.
    """
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
        return render_template(
            'post.html',
            post=post,
            posts=posts,
            category=category,
            sections=sections,
            comments=comments,
            access=access
        )
    else:
        return render_template(
            'post.html',
            post=post,
            posts=posts,
            category=category,
            sections=sections,
            comments=comments
        )


@app.route('/post-creation')
def create():
    """
    Страница создания нового поста.
    Если в базе нет разделов и категорий, заполняем их шаблонными данными.
    """
    if 'user' in session:
        try:
            access = (Users.query.filter_by(id=session['user']).first()).access
        except:
            return redirect(url_for('logout'))

        # Проверяем, есть ли разделы, если нет — создаём несколько по умолчанию
        sections = ForumSections.query.all()
        if not sections:
            sections = ('Электроника', "Игры", "Общение")
            for i in sections:
                new_section = ForumSections(section=i)
                db.session.add(new_section)
            db.session.commit()

        # Проверяем, есть ли категории, если нет — создаём несколько по умолчанию
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

        return render_template('post-creation.html', category=category, sections=sections, access=access)

    return render_template('post-creation.html')


@app.route('/create', methods=['POST'])
def create_post():
    """
    Обработка создания нового поста (отправка формы).
    Проверяем, что выбран раздел и категория, введён заголовок и текст.
    """
    if 'user' in session:
        section = request.form['post-section']
        category = request.form['post-category']
        theme = request.form['post-title']
        text = request.form['post-content']
        user = session['user']

        # Проверяем существование выбранного раздела и категории
        section_exist = ForumSections.query.filter_by(id=section).first()
        category_exist = ForumCategory.query.filter_by(id=category).first()

        if not section_exist:
            return jsonify({'answer': False, 'message': 'Выберите раздел'})
        elif not category_exist:
            return jsonify({'answer': False, 'message': 'Выберите категорию'})
        elif not theme.strip():
            return jsonify({'answer': False, 'message': 'Создайте заголовок'})
        elif not text.strip():
            return jsonify({'answer': False, 'message': 'Напишите текст'})

        new_post = ForumPosts(
            user_id=user,
            theme=theme,
            text=text,
            section_id=section,
            category_id=category
        )
        try:
            db.session.add(new_post)
            db.session.commit()
            return jsonify({'answer': True, 'message': 'Пост успешно создан'})
        except Exception as err:
            db.session.rollback()
            return jsonify({'answer': False, 'message': 'Возникла ошибка'})


@app.route('/comment', methods=['POST'])
def comment():
    """
    Обработка создания комментария к посту.
    Ожидает форму с полем 'post' (id поста) и 'comment' (текст комментария).
    """
    if 'user' in session:
        page = request.form['post']
        comment = request.form['comment']

        if not page.strip():
            return jsonify({'answer': False, 'message': 'Возникла ошибка'})
        elif not comment.strip():
            return jsonify({'answer': False, 'message': 'Напишите текст'})

        new_comment = ForumComments(
            user_id=session['user'],
            text=comment,
            post_id=page
        )
        try:
            db.session.add(new_comment)
            db.session.commit()
            return jsonify({'answer': True, 'message': 'Комментарий опубликован'})
        except Exception as err:
            db.session.rollback()
            return jsonify({'answer': False, 'message': 'Возникла ошибка'})


@app.route('/reg', methods=['POST'])
def reg():
    """
    Регистрация нового пользователя.
    Ожидает форму с полями 'loginreg', 'emailreg' и 'passwordreg'.
    Проверяем, что почта не заблокирована, пароль >= 8 символов, а логин/почта не заняты.
    """
    username = request.form['loginreg']
    email = request.form['emailreg']

    # Проверяем, что почта не заблокирована
    isBanned = BannedUsers.query.filter_by(email=email).first()
    if isBanned:
        return jsonify({'answer': False, 'message': 'Эта почта заблокирована'})

    password = request.form['passwordreg']
    if len(password) < 8:
        return jsonify({'answer': False, 'message': 'Пароль должен содержать минимум 8 символов'})

    # Хешируем пароль
    password = generate_password_hash(password)

    # Проверяем занятость логина и почты
    username_occupied = Users.query.filter_by(username=username).first()
    email_occupied = Users.query.filter_by(email=email).first()
    if username_occupied:
        return jsonify({'answer': False, 'message': 'Имя занято'})
    elif email_occupied:
        return jsonify({'answer': False, 'message': 'Почта занята'})

    # Создаём нового пользователя
    new_user = Users(username=username, email=email, password=password)
    try:
        db.session.add(new_user)
        db.session.commit()
        # Сохраняем id пользователя в сессии
        session['user'] = Users.query.filter_by(username=username).first().id
        return jsonify({'answer': True, 'message': 'Успешно'})
    except Exception as err:
        db.session.rollback()
        return jsonify({'answer': False, 'message': 'Возникла ошибка'})


@app.route('/logout')
def logout():
    """
    Разлогинивание пользователя: очищаем сессию и перенаправляем на главную.
    """
    session.clear()
    return redirect(url_for('main'))


@app.route('/log', methods=['POST'])
def log():
    """
    Авторизация пользователя.
    Проверяем введённый логин и пароль, сверяем с захешированным в базе.
    """
    username = request.form['login']
    password = request.form['password']
    user = Users.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        session['user'] = user.id
        return jsonify({'answer': True, 'message': 'Успешно'})
    else:
        return jsonify({'answer': False, 'message': 'Неверный логин или пароль'})


# При запуске приложения автоматически создаём все таблицы (если их нет)
with app.app_context():
    db.create_all()


if __name__ == "__main__":
    # Запускаем приложение в режиме отладки (debug=True)
    app.run(debug=True)
