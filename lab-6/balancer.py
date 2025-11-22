from flask import Flask, request, jsonify, redirect, render_template
import requests
import threading
import time

app = Flask(__name__)


# Класс для балансировки нагрузки между серверами
class LoadBalancer:
    def __init__(self):
        # Список всех серверов (инстансов)
        self.instances = []
        # Текущий индекс для алгоритма Round Robin
        self.current_index = 0

    # Добавляет новый сервер в пул
    def add_instance(self, ip, port):
        instance = {"ip": ip, "port": port, "active": False}
        self.instances.append(instance)
        # При добавлении сервера сразу проверяем его статус
        self.check_instance_health(instance)

    # Удаляет сервер из пула по индексу
    def remove_instance(self, index):
        if 0 <= index < len(self.instances):
            self.instances.pop(index)
            # Сбрасываем индекс, если он вышел за границы после удаления
            if self.current_index >= len(self.instances):
                self.current_index = 0

    # Возвращает следующий сервер по алгоритму Round Robin
    def get_next_instance(self):
        if not self.instances:
            return None

        # Сохраняем начальный индекс для проверки полного круга
        start_index = self.current_index

        # Ищем следующий активный сервер, проходя по кругу
        while True:
            instance = self.instances[self.current_index]
            # Увеличиваем индекс для каждого следующего вызова
            self.current_index = (self.current_index + 1) % len(self.instances)

            # Если сервер активен, возвращаем его
            if instance["active"]:
                return instance

            # Если прошли полный круг и все серверы неактивны, выходим
            if self.current_index == start_index:
                return None

    # Проверяет статус конкретного сервера
    @staticmethod
    def check_instance_health(instance):
        try:
            url = f"http://{instance['ip']}:{instance['port']}/health"
            response = requests.get(url, timeout=3)
            instance["active"] = (response.status_code == 200)
            return instance["active"]
        except requests.exceptions.RequestException:
            instance["active"] = False
            return False

    # Проверяет статус всех серверов
    def check_all_instances_health(self):
        for instance in self.instances:
            self.check_instance_health(instance)

    # Фоновая проверка здоровья всех серверов
    def health_check(self):
        while True:
            self.check_all_instances_health()
            time.sleep(5)


# Создаем экземпляр балансировщика
lb = LoadBalancer()


@app.route('/')
def index():
    # Рендерим главную страницу с Web UI для управления серверами
    return render_template("index.html", instances=lb.instances)


# Обрабатывает добавление нового сервера
@app.route('/add_instance', methods=['POST'])
def add_instance():
    ip = request.form['ip']
    port = int(request.form['port'])
    lb.add_instance(ip, port)
    return redirect('/')


# Обрабатывает удаление сервера
@app.route('/remove_instance', methods=['POST'])
def remove_instance():
    index = int(request.form['index'])
    lb.remove_instance(index)
    return redirect('/')


# Возвращает статус всех серверов в формате JSON
@app.route('/health')
def health():
    # При запросе статуса проверяем актуальное состояние
    lb.check_all_instances_health()
    return jsonify([{
        "ip": i["ip"],
        "port": i["port"],
        "active": i["active"]
    } for i in lb.instances])


# Обрабатывает запросы клиентов, перенаправляя их на серверы
@app.route('/process')
def process():
    # Если нет доступных серверов, возвращаем ошибку
    if not lb.instances:
        return "Нет доступных серверов", 500

    max_tries = len(lb.instances)
    tries = 0
    while tries < max_tries:
        # Получаем следующий сервер по алгоритму Round Robin
        instance = lb.get_next_instance()
        if not instance:
            break
        try:
            response = requests.get(
                f"http://{instance['ip']}:{instance['port']}/process",
                timeout=3
            )
            return response.json()
        except requests.exceptions.RequestException:
            # Помечаем этот инстанс как неактивный и пробуем следующий
            instance["active"] = False
            tries += 1

    return "Нет доступных серверов", 500


if __name__ == '__main__':
    # Запускаем поток для проверки здоровья серверов в фоне
    health_thread = threading.Thread(target=lb.health_check)
    health_thread.daemon = True  # Поток завершится при завершении main
    health_thread.start()

    # Запускаем Flask-приложение балансировщика
    app.run(port=5000, debug=True)