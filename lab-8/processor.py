import asyncio
import json
import glob


# Загружает все транзакции из JSON-файлов
def load_transactions_from_files():
    # Находим все файлы с транзакциями по шаблону
    transaction_files = glob.glob("transactions_*.json")

    if not transaction_files:
        print("Файлы с транзакциями не найдены")
        return []

    all_transactions = []

    # Загружаем транзакции из каждого файла
    for file_name in transaction_files:
        try:
            with open(file_name, "r") as file:
                transactions = json.load(file)
                # extend распаковывает и добавляет элементы по одному в общий список
                all_transactions.extend(transactions)
        except Exception as e:
            print(f"Ошибка при чтении файла {file_name}: {e}")

    return all_transactions


# Прибавляет сумму одной транзакции к итогам по соответствующей категории
async def process_transaction(transaction, category_totals):
    category = transaction["category"]
    amount = transaction["amount"]

    # Если операций данной категории ещё не было
    if category not in category_totals:
        category_totals[category] = 0

    category_totals[category] += amount


# Асинхронно обрабатывает список транзакций
async def process_transactions_async(transactions):
    print(f"Начинаем обработку {len(transactions)} транзакций")

    # Словарь для хранения сумм по категориям
    category_totals = {}

    # Создаем задачи для обработки каждой транзакции
    tasks = []
    for transaction in transactions:
        task = asyncio.create_task(process_transaction(transaction, category_totals))
        tasks.append(task)

    # Запускаем задачи и ждем завершения, * распаковывает список задач по одной
    await asyncio.gather(*tasks)

    return category_totals


# Проверяет, какие категории превысили порог
def check_warnings(category_totals, warning_threshold=4500):
    warnings_count = 0

    # items() превращает словарь в список кортежей
    for category, amount in category_totals.items():
        if amount > warning_threshold:
            print(f"Внимание: расходы в категории '{category}' превысили {warning_threshold} руб.")
            warnings_count += 1

    if warnings_count == 0:
        print("Превышений порога расходов не обнаружено")


# Выводит итоговую информацию по категориям
def print_summary(category_totals):
    print("\nИтоги по категориям:")

    if not category_totals:
        print("Нет данных для отображения")
        return

    total_all_categories = 0

    # Считаем общую сумму - values() возвращает только суммы без ключей
    for amount in category_totals.values():
        total_all_categories += amount

    # Выводим каждую категорию
    for category, amount in category_totals.items():
        print(f"{category} - {amount:.2f} руб.")

    print(f"\nОбщая сумма: {total_all_categories:.2f} руб.")


async def main():
    # Загружаем транзакции из файлов
    transactions = load_transactions_from_files()

    if not transactions:
        print("Нет транзакций для обработки")
        return

    # Асинхронно обрабатываем транзакции
    category_totals = await process_transactions_async(transactions)

    # Проверяем превышение порога (один раз для каждой категории)
    check_warnings(category_totals)

    # Выводим итоговую информацию
    print_summary(category_totals)


if __name__ == "__main__":
    # Запускаем асинхронную обработку
    asyncio.run(main())