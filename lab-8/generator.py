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
        "timestamp": str(datetime.now()),  # Дата и время в момент генерации
        "category": random.choice(categories),  # Случайная категория
        "amount": round(random.uniform(10, 5000), 2)  # Сумма от 10 до 5000
    }


# Сохраняет список транзакций в JSON-файл
async def save_transactions_to_file(transactions, file_index):
    # Задаем имя для каждого файла по индексу пакета
    file_name = f"transactions_{file_index}.json"

    # Записываем данные в файл
    with open(file_name, "w") as file:
        json.dump(transactions, file)

    # Выводим информацию о сохранении
    print(f"Сохранено {len(transactions)} транзакций в файл {file_name}")
    return file_name


# Асинхронно генерирует транзакции и сохраняет их пакетами по 10
async def generate_transactions(total_count):
    print(f"Начинаем генерацию {total_count} транзакций")

    transaction_package = []  # Текущий пакет транзакций
    file_index = 1  # Индекс для имен файлов

    for i in range(total_count):
        # Генерируем транзакцию
        transaction = generate_transaction()
        transaction_package.append(transaction)

        # Каждые 10 транзакций сохраняем в файл
        if len(transaction_package) == 10:
            # Создаем задачу для асинхронного сохранения
            await save_transactions_to_file(transaction_package, file_index)

            # Очищаем пакет и увеличиваем индекс файла
            transaction_package.clear()
            file_index += 1

    # Сохраняем оставшиеся транзакции (если их меньше 10)
    if transaction_package:
        await save_transactions_to_file(transaction_package, file_index)

    print("Генерация транзакций завершена!")


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