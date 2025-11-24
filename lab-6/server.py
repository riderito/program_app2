from flask import Flask, jsonify
import sys

app = Flask(__name__)


# Эндпоинт для проверки состояния сервера
@app.route('/health')
def health():
    return jsonify({
        "status": "ОК",
        "port": port
    })


# Эндпоинт для обработки запросов, возвращает порт сервера
@app.route('/process')
def process():
    return jsonify({
        "message": "Запрос обработан",
        "port": port
    })


# Тест перехвата запросов
@app.route('/<path:path>')
def test(path):
    return jsonify({
        "message": f"Мы любим РПП❤️ Обработан путь: /{path}",
        "port": port
    })


if __name__ == '__main__':
    # Проверяем, что порт передан как аргумент командной строки
    if len(sys.argv) != 2:
        print("Используй команду: python server.py <порт>")
        sys.exit(1)

    port = int(sys.argv[1])
    app.run(port=port)