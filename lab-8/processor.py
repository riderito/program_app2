import asyncio
import json

# Название файла со всеми транзакциями
file_name = "transactions.json"


# Загружает все транзакции из файла
def load_transactions_from_file():
    try:
        with open(file_name, "r") as file:
            transactions = json.load(file)
            return transactions
    except FileNotFoundError:
        print(f"Файл {file_name} не найден")
        return []


# Выводит итоговую информацию по категориям
def print_summary(category_totals):
    print("\nИтоги по категориям:")

    if not category_totals:
        print("Нет данных для отображения")
        return

    total_all_categories = 0

    for amount in category_totals.values():
        total_all_categories += amount

    for category, amount in category_totals.items():
        print(f"{category} - {amount:.2f} руб.")

    print(f"\nОбщая сумма: {total_all_categories:.2f} руб.")


# Загружает транзакции из файла и отправляет их в очередь
async def transaction_loader(transaction_queue):

    transactions = load_transactions_from_file()

    if not transactions:
        print("Нет транзакций для обработки")
        await transaction_queue.put(None)
        return

    print(f"Загружено {len(transactions)} транзакций")

    for transaction in transactions:
        # Помещаем каждую транзакцию в очередь для обработки
        await transaction_queue.put(transaction)

    # Отправляем сигнал завершения загрузки
    await transaction_queue.put(None)


# Обрабатывает транзакции из очереди (реактивный обработчик)
async def transaction_processor(transaction_queue, warning_threshold=10000):
    print("Начинаем обработку транзакций...")

    # Словарь для хранения сумм по категориям
    category_totals = {}
    # Словарь для отслеживания, по каким категориям уже было предупреждение
    warned_categories = {}

    while True:
        # Ждем следующую транзакцию из очереди
        transaction = await transaction_queue.get()

        # Если получили None, это сигнал завершения
        if transaction is None:
            break

        # Извлекаем данные из транзакции
        category = transaction["category"]
        amount = transaction["amount"]

        # Добавляем сумму к категории
        if category not in category_totals:
            category_totals[category] = 0
            warned_categories[category] = False

        category_totals[category] += amount

        # Проверяем, не превысила ли категория порог
        if category_totals[category] > warning_threshold and not warned_categories[category]:
            print(f"\nВнимание: расходы в категории '{category}' превысили {warning_threshold} руб.")
            warned_categories[category] = True

    # После обработки всех транзакций выводим итоги
    print_summary(category_totals)


async def main():
    # Создаем очередь для транзакций
    # Главный элемент реактивной системы - через него передаются данные
    transaction_queue = asyncio.Queue()

    try:
        # Запускаем загрузку и обработку параллельно
        # Работают одновременно и общаются через очередь
        await asyncio.gather(
            transaction_loader(transaction_queue),
            transaction_processor(transaction_queue)
        )

    except Exception as error:
        print(f"Произошла ошибка: {error}")


if __name__ == "__main__":
    # Запускаем асинхронную программу
    asyncio.run(main())