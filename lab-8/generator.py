import asyncio
import json
import random
from datetime import datetime

# Название файла со всеми транзакциями
file_name = "transactions.json"


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
        # Сумма от 1 до 5000 с двумя знаками после запятой
        "amount": round(random.uniform(1, 5000), 2)
    }


# Загружает существующие транзакции из файла
def load_existing_transactions():
    try:
        with open(file_name, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []  # Файл не существует, возвращаем пустой список


# Сохраняет пакет транзакций в файл, когда накопилось 10 штук
async def save_transaction_package(transactions):
    # Загружаем существующие транзакции
    existing_transactions = load_existing_transactions()

    # Добавляем новые транзакции к существующим
    all_transactions = existing_transactions + transactions

    # Сохраняем обновленные данные в файл, indent делает json читабельным в файле
    with open(file_name, "w") as file:
        json.dump(all_transactions, file, indent=1)

    # Вывод в консоль после сохранения
    print(f"Сохранено {len(transactions)} транзакций. Всего в файле: {len(all_transactions)}")


# Генерирует транзакции и помещает их в очередь (источник данных в реактивном потоке)
async def transaction_publisher(transaction_queue, total_count):
    print(f"Начинаем генерацию {total_count} транзакций...")

    for i in range(total_count):
        # Генерируем одну транзакцию
        transaction = generate_transaction()

        # Помещаем транзакцию в очередь
        # "Потребитель" будет забирать транзакции отсюда
        await transaction_queue.put(transaction)

    # Отправляем сигнал завершения в очередь
    await transaction_queue.put(None)
    print(f"Генерация завершена. Создано {total_count} транзакций")


# Обрабатывает транзакции из очереди (потребитель данных в реактивном потоке)
async def transaction_subscriber(transaction_queue):
    # Хранилище для накопления транзакций
    storage = []

    while True:
        # Ждем следующую транзакцию из очереди
        # Выполняется, когда появляются данные
        transaction = await transaction_queue.get()

        # Если получили None, это сигнал завершения
        if transaction is None:
            break

        # Добавляем транзакцию в хранилище
        storage.append(transaction)

        # Если накопилось 10 транзакций, сохраняем их
        if len(storage) >= 10:
            await save_transaction_package(storage)
            storage = []  # Очищаем буфер

    # Сохраняем оставшиеся транзакции (если они есть)
    if storage:
        await save_transaction_package(storage)


async def main():
    # Создаем очередь для транзакций
    # Главный элемент реактивной системы - через него передаются данные
    transaction_queue = asyncio.Queue()

    # Запрашиваем количество транзакций у пользователя
    try:
        total_count = int(input("Введите количество транзакций для генерации: "))

        if total_count <= 0:
            print("Количество должно быть положительным числом")
            return
    except ValueError:
        print("Пожалуйста, введите целое число")
        return

    try:
        # Запускаем производителя и потребителя параллельно
        # Работают одновременно и общаются через очередь
        await asyncio.gather(
            transaction_publisher(transaction_queue, total_count),
            transaction_subscriber(transaction_queue)
        )

    except Exception as error:
        print(f"Произошла ошибка: {error}")


if __name__ == "__main__":
    # Запускаем асинхронную программу
    asyncio.run(main())