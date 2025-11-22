import os
from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2

# Функция для подключения к базе данных
def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        port=5432,
        database="rpp_lab5",
        user="postgres",
        password=os.getenv('DATABASE_PASSWORD')
    )


# Модель для данных пользователя
class User(UserMixin):
    # Делает из строки БД объект, который flask-login может использовать
    def __init__(self, user_id, email, password, name):
        self.id = user_id
        self.email = email
        self.password = password
        self.name = name

    # Поиск пользователя в БД по email и возврат объекта User
    @classmethod # Позволяет создавать объект класса внутри метода
    def find_by_email(cls, email):
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, email, password, name FROM users WHERE email = %s;",
                    (email,)
                )
                row = cur.fetchone()
                if row:
                    # Преобразуем строку из БД в объект User (новый экземпляр)
                    return cls(row[0], row[1], row[2], row[3])
                return None
        finally:
            conn.close()

    # Вставляем нового пользователя в БД
    @classmethod
    def create(cls, name, email, password):
        # Хэшируем пароль перед записью в БД
        password_hash = generate_password_hash(password)
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO users (name, email, password) VALUES (%s, %s, %s) RETURNING id;",
                    (name, email, password_hash)
                )
                new_id = cur.fetchone()[0]
            conn.commit()
            # Загружаем созданного пользователя из БД и возвращаем объект
            return cls.find_by_id(new_id)
        finally:
            conn.close()

    # Поиск пользователя по id
    @classmethod
    def find_by_id(cls, user_id):
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, email, password, name FROM users WHERE id = %s;",
                    (user_id,)
                )
                row = cur.fetchone()
                if row:
                    return cls(row[0], row[1], row[2], row[3])
                return None
        finally:
            conn.close()


# Объект Flask-приложения
app = Flask(__name__)
# Секрет для защиты данных сессии (хранится id в куки)
app.secret_key = "secret_for_lab"

# Настройка менеджера логина, интегрирует flask-login с приложением
login_manager = LoginManager()
login_manager.init_app(app)


# Функция, которую flask-login вызывает по id из сессии
# Вновь создаёт объект User для current_user при каждом запросе
@login_manager.user_loader
def load_user(user_id):
    return User.find_by_id(int(user_id))


# Корневая страница GET /
@app.route("/", methods=["GET"])
def index():
    # Если в сессии нет user_id, пользователя перенаправляют на страницу входа
    if not current_user.is_authenticated:
        return redirect(url_for("login_get"))
    # Для авторизованных - страница с текстом, данными пользователя и кнопкой "Выход"
    return render_template("index.html", user=current_user)


# Страница входа GET /login
@app.route("/login", methods=["GET"])
def login_get():
    # Если уже авторизован - перенаправляем на корень
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    # Отдаем форму входа
    return render_template("login.html", message=None)


# Авторизация POST /login
@app.route("/login", methods=["POST"])
def login_post():
    # Получаем данные из формы, strip убирает лишние пробелы
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "").strip()

    # Проверка обязательных полей
    if not email or not password:
        return render_template("login.html", message="Поля email и password обязательны для заполнения")

    # Поиск пользователя по email в БД
    user = User.find_by_email(email)
    if user is None:
        return render_template("login.html", message="Пользователь с таким email не найден")

    # Сравниваем введённый пароль с хранимым хэшем
    if not check_password_hash(user.password, password):
        return render_template("login.html", message="Неправильный пароль")

    # Вызывает user.get_id(), записывает значение в сессию
    # В следующих запросах flask-login по этому id восстанавливает объект через user_loader
    login_user(user)
    return redirect(url_for("index"))


# Страница регистрации GET /signup
@app.route("/signup", methods=["GET"])
def signup_get():
    # Если уже авторизован - редирект на корень
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    return render_template("signup.html", message=None)


# Регистрация POST /signup
@app.route("/signup", methods=["POST"])
def signup_post():
    # Получаем данные из формы
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "").strip()

    # Проверка обязательных полей
    if not name or not email or not password:
        return render_template("signup.html", message="Все поля обязательны для заполнения")

    # Проверяем, есть ли уже пользователь с таким email
    user = User.find_by_email(email)
    if user is not None:
        return render_template("signup.html", message="Пользователь с таким email уже существует")

    # Создаём пользователя и перенаправляем на страницу входа
    User.create(name, email, password)
    return redirect(url_for("login_get"))


# Выход GET /logout
@app.route("/logout", methods=["GET"])
def logout():
    if current_user.is_authenticated:
        # Удаляем информацию о пользователе из сессии (current_user становится анонимным)
        logout_user()
    # После выхода - на страницу входа
    return redirect(url_for("login_get"))


if __name__ == "__main__":
    app.run(debug=True)
