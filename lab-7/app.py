import json
import os
from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Инициализация Flask-приложения
app = Flask(__name__)

# Настройка ограничителя запросов (flask-limiter)
limiter = Limiter(
    # Функция для идентификации пользователей по их IP-адресу
    get_remote_address,
    app=app,
    # Общее ограничение для всех маршрутов: 100 запросов в сутки
    default_limits=["100 per day"]
)

# Переменная с именем файла для хранения данных
file_name = 'data.json'


# Загрузка данных из файла при старте приложения
def load_data():
    # Проверяем существование файла data.json
    if os.path.exists(file_name):
        # Открываем файл в режиме чтения
        with open(file_name, 'r') as file:
            # Загружаем JSON данные из файла
            return json.load(file)
    # Возвращаем пустой словарь если файл не существует
    return {}


# Загрузка данных при запуске приложения
data = load_data()


# Сохранение данных в файл
# Вызывается после каждой операции добавления или удаления
def save_data():
    with open(file_name, 'w') as file:
        # Преобразуем текущий словарь в JSON и записываем в файл
        json.dump(data, file)


# Маршрут для сохранения ключа и значения
@app.route('/set', methods=['POST'])
@limiter.limit("10 per minute")  # 10 запросов в минуту только для этого маршрута
def set_value():
    if not request.is_json:
        return jsonify({'error': 'Content-Type должен быть application/json'}), 400
    # Ожидает JSON в теле запроса с полями 'key' и 'value'
    try:
        # Получаем ключ из тела запроса
        key = request.json.get('key')
        # Получаем значение из тела запроса
        value = request.json.get('value')

        # Проверяем, что ключ не пустой
        if not key:
            return jsonify({'error': 'Ключ является обязательным полем'}), 400

        # Сохраняем ключ-значение в словаре data
        data[key] = value
        # Сохраняем изменения в файл
        save_data()

        # Возвращаем сообщение об успешном выполнении
        return jsonify({'message': 'Данные успешно сохранены'}), 200
    except Exception as e:
        # Обрабатываем любые ошибки
        return jsonify({'error': f'Ошибка: {e}'}), 500


# Маршрут для получения значения по ключу
@app.route('/get/<key>', methods=['GET'])
def get_value(key):
    try:
        # Проверяем существование ключа в хранилище
        if key not in data:
            return jsonify({'error': 'Ключ не найден'}), 404

        # Возвращаем значение по ключу
        return jsonify({'value': data[key]}), 200
    except Exception as e:
        # Обрабатываем ошибки
        return jsonify({'error': f'Ошибка при получении данных: {e}'}), 500


# Маршрут для удаления ключа
@app.route('/delete/<key>', methods=['DELETE'])
@limiter.limit("10 per minute")  # 10 запросов в минуту только для этого маршрута
def delete_value(key):
    try:
        # Проверяем существование ключа перед удалением
        if key not in data:
            return jsonify({'error': 'Ключ не найден'}), 404

        # Удаляем ключ из словаря
        del data[key]
        # Сохраняем изменения в файл
        save_data()

        # Возвращаем сообщение об успешном удалении
        return jsonify({'message': 'Ключ успешно удален'}), 200
    except Exception as e:
        # Обрабатываем ошибки
        return jsonify({'error': f'Ошибка при удалении: {e}'}), 500


# Маршрут для проверки существования ключа
@app.route('/exists/<key>', methods=['GET'])
def check_exists(key):
    # Возвращает bool значение в exists
    try:
        # Проверяем наличие ключа в словаре
        exists = key in data
        # Возвращаем результат проверки
        return jsonify({'exists': exists}), 200
    except Exception as e:
        # Обрабатываем ошибки
        return jsonify({'error': f'Ошибка при проверке ключа: {e}'}), 500


if __name__ == '__main__':
    # Запускаем в режиме отладки
    app.run(debug=True)