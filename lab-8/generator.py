import asyncio
import json
import random
from datetime import datetime


# Генерирует одну финансовую транзакцию
def generate_transaction():
    # Список возможных категорий расходов
    categories = ["Супермаркеты", "Кафе и рестораны", "Одежда и обувь",
                  "Цифровой контент", "Образование", "Сотовая связь"]

    return {
        # Дата и время в момент генерации
        "timestamp": str(datetime.now()),
        # Случайная категория
        "category": random.choice(categories),
        # Сумма от 10 до 5000 с двумя знаками после запятой
        "amount": round(random.uniform(10, 5000), 2)
    }


# Загружает существующие транзакции из файла
def load_existing_transactions(file_name):
    try:
        with open(file_name, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []  # Файл не существует, возвращаем пустой список


# Сохраняет список транзакций в JSON-файл
async def save_transactions_to_file(transactions, file_name):
    # Загружаем существующие транзакции
    existing_transactions = load_existing_transactions(file_name)

    # Объединяем старые и новые транзакции
    all_transactions = existing_transactions + transactions

    # Записываем все транзакции в файл в JSON-формате
    with open(file_name, "w") as file:
        # indent дает отступы для читаемости
        json.dump(all_transactions, file, indent=1)

    # Выводим информацию о сохранении
    print(f"Добавлено {len(transactions)} транзакций, всего в файле: {len(all_transactions)}")


# Асинхронно генерирует транзакции и сохраняет их пакетами по 10
async def generate_transactions(total_count):
    print(f"Начинаем генерацию {total_count} транзакций")

    # Текущий пакет транзакций
    transaction_package = []
    # Файл для всех транзакций
    file_name = "transactions.json"
    # Счетчик пакетов
    package_count = 0

    for i in range(total_count):
        # Генерируем транзакцию
        transaction = generate_transaction()
        transaction_package.append(transaction)

        # Каждые 10 транзакций сохраняем в файл
        if len(transaction_package) == 10:
            package_count += 1

            # Создаем задачу для асинхронного сохранения
            await save_transactions_to_file(transaction_package, file_name)

            # Очищаем пакет
            transaction_package.clear()

    # Сохраняем оставшиеся транзакции (если их меньше 10)
    if transaction_package:
        package_count += 1
        await save_transactions_to_file(transaction_package, file_name)

    print(f"Генерация завершена. Создано {package_count} пакетов, всего {total_count} транзакций")


async def main():
    # Запрашиваем количество транзакций у пользователя
    try:
        total_count = int(input("Введите количество транзакций для генерации: "))
        if total_count <= 0:
            print("Количество должно быть положительным числом")
            return
    except ValueError:
        print("Пожалуйста, введите целое число")
        return

    # Запускаем генерацию транзакций
    await generate_transactions(total_count)


if __name__ == "__main__":
    # Запускаем асинхронную программу
    asyncio.run(main())