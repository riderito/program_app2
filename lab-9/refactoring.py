# Код 1
def send_email(to, subject, body):
    print(f"Connecting to SMTP server...")
    print(f"Sending email to {to} with subject '{subject}'...")
    print(f"Email sent.")
def send_sms(to, message):
    print(f"Connecting to SMS gateway...")
    print(f"Sending SMS to {to} with message '{message}'...")
    print(f"SMS sent.")

# Методы рефакторинга:
# 1. Удаление дублирующегося кода.
# 2. Вынесение общих частей в отдельную функцию.


# Функция для отправки сообщения (общая часть)
def send_message(recipient, content_type, content, content_label, service_name):
    print(f"Connecting to {service_name}...")
    print(f"Sending {content_type} to {recipient} with {content_label} '{content}'...")
    print(f"{content_type} sent.")


# Переделываем старые функции, используя общую функцию
def send_email(to, subject, body):
    send_message(to, "email", subject, "subject", "SMTP server")


def send_sms(to, message):
    send_message(to, "SMS", message, "message", "SMS gateway")


# Код 2
def process_order(order):
    total = 0
    for item in order["items"]:
        total += item["price"] * item["quantity"]
    print(f"Total: {total}")
    print("Processing payment...")
    print("Payment successful!")
    print("Sending confirmation email...")
    print("Order complete.")

# Методы рефакторинга:
# 1. Разделение длинной функции (Extract Method).
# 2. Введение промежуточных переменных для улучшения читаемости.


# Функция для расчета общей суммы
def calculate_total(order_items):
    total = 0
    for item in order_items:
        total += item["price"] * item["quantity"]
    return total


# Функция для обработки платежа
def process_payment():
    print("Processing payment...")
    print(f"Payment successful!")


# Функция для отправки подтверждения
def send_confirmation():
    print("Sending confirmation email...")
    print("Order complete.")


# Главная функция, которая использует все вспомогательные
def process_order(order):
    order_items = order["items"]
    order_total = calculate_total(order_items)
    print(f"Total: {order_total}")
    process_payment()
    send_confirmation()


# Код 3
def calculate_shipping(country, weight):
    if country == "USA":
        if weight < 5:
            return 10
        else:
            return 20
    elif country == "Canada":
        if weight < 5:
            return 15
        else:
            return 25
    else:
        if weight < 5:
            return 30
        else:
            return 50

# Методы рефакторинга:
# 1. Замена вложенных условий на плоскую структуру.
# 2. Использование словарей для хранения правил.


# Используем словарь для хранения стоимости доставки
shipping_rates = {
    "USA": {"light": 10, "heavy": 20},
    "Canada": {"light": 15, "heavy": 25},
    "default": {"light": 30, "heavy": 50}
}

# Константа порогового веса для определения его категории
weight_threshold = 5


def calculate_shipping(country, weight):
    # Определяем категорию веса
    if weight < weight_threshold:
        weight_category = "light"
    else:
        weight_category = "heavy"

    # Получаем ставки для страны или используем значения по умолчанию
    if country in shipping_rates:
        country_rates = shipping_rates[country]
    else:
        country_rates = shipping_rates["default"]

    # Возвращаем стоимость доставки по категории
    return country_rates[weight_category]


# Код 4
def calculate_tax(income):
    if income <= 10000:
        return income * 0.1
    elif income <= 20000:
        return income * 0.15
    else:
        return income * 0.2

# Методы рефакторинга:
# 1. Замена магических чисел на константы.
# 2. Улучшение читаемости путем пояснительных комментариев.


# Определяем константы для порогов уровня дохода
low_income_threshold = 10000
medium_income_threshold = 20000

low_tax_rate = 0.1  # 10% налог для низкого дохода
medium_tax_rate = 0.15  # 15% налог для среднего дохода
high_tax_rate = 0.2 # 20% налог для высокого дохода


def calculate_tax(income):
    # Проверяем низкий доход
    if income <= low_income_threshold:
        return income * low_tax_rate

    # Проверяем средний доход
    elif income <= medium_income_threshold:
        return income * medium_tax_rate

    # Все остальное - высокий доход
    else:
        return income * high_tax_rate


# Код 5
def create_report(name, age, department, salary, bonus, performance_score):
    print(f"Name: {name}")
    print(f"Age: {age}")
    print(f"Department: {department}")
    print(f"Salary: {salary}")
    print(f"Bonus: {bonus}")
    print(f"Performance Score: {performance_score}")

# Методы рефакторинга:
# 1. Упаковка аргументов в словарь.
# 2. Использование стандартных структур данных для передачи параметров.


# Используем словарь для передачи всех данных сотрудника
def create_report(employee_data):
    # Извлекаем данные из словаря
    name = employee_data.get("name", "Неизвестно")
    age = employee_data.get("age", 0)
    department = employee_data.get("department", "Неизвестно")
    salary = employee_data.get("salary", 0)
    bonus = employee_data.get("bonus", 0)
    performance_score = employee_data.get("performance_score", 0)

    # Выводим отчет
    print(f"Name: {name}")
    print(f"Age: {age}")
    print(f"Department: {department}")
    print(f"Salary: {salary}")
    print(f"Bonus: {bonus}")
    print(f"Performance Score: {performance_score}")


# Пример передаваемых параметров
employee1 = {
    "name": "Адалинская Степук",
    "age": 21,
    "department": "IT",
    "salary": 100000,
    "bonus": 10000,
    "performance_score": 5
}
