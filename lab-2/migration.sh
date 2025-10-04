#!/bin/bash

# Параметры подключения к базе данных
db_name="lab2"
db_user="postgres"
db_host="localhost"
db_port="5432"

# Путь к директории с миграциями
dir_migrate="./migrations"

# Функция для выполнения SQL из файла
run_sql() {
    # Принимаем путь к файлу в переменную
    file_name="$1"

    if psql -U "$db_user" -d "$db_name" -h "$db_host" -p "$db_port" -f "$file_name"; then
        echo "Файл $file_name выполнен"
    else
        echo "Ошибка при выполнении файла: $file_name"
        exit 1
    fi
}

# Функция для выполнения SQL-запроса без возврата результата
run_sql_c() {
    # Принимаем запрос с изолированием названия переменной
    local sql_query="$1"

    # Если psql завершится с ошибкой выводим сообщение и завершаем скрипт
    if ! psql -U "$db_user" -d "$db_name" -h "$db_host" -p "$db_port" -c "$sql_query"; then
        echo "Ошибка при выполнении SQL запроса: $sql_query"
        exit 1
    fi
}

# Функция для выполнения SQL-запроса с возвратом
run_sql_c_t() {
    local sql_query="$1"

    if ! psql -U "$db_user" -d "$db_name" -h "$db_host" -p "$db_port" -t -c "$sql_query"; then
        echo "Ошибка при выполнении SQL запроса: $sql_query"
        exit 1
    fi
}

# Создание таблицы migrations, если она не существует
create_migrations_table() {

    # Спросим пароль для работы с psql
    read -s -p "Введите пароль для пользователя ${db_user}: " DB_PASS
    echo

    # Экспортируем в нужную переменную
    export PGPASSWORD="$DB_PASS"

    echo "Создание таблицы migrations (если не существует)"
    run_sql_c "CREATE TABLE IF NOT EXISTS migrations (
        id SERIAL PRIMARY KEY,
        migration_name VARCHAR(255) UNIQUE NOT NULL,
        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );"
}

# Получение списка примененных миграций
get_applied_migrations() {
    run_sql_c_t "SELECT migration_name FROM migrations;"
}

# Применение миграций
apply_migrations() {
    echo "Поиск файлов миграций в директории: $dir_migrate"

    # Проверяем, существует ли директория
    if [ ! -d "$dir_migrate" ]; then
        echo "Ошибка: Директория $dir_migrate не существует"
        exit 1
    fi

    # Получение списка примененных миграций
    echo "Получение списка примененных миграций..."
    applied_migrations=$(run_sql_c_t "SELECT migration_name FROM migrations;")

    # Проверяем, пришёл ли успешный код 0 при получении списка
    if [ $? -ne 0 ]; then
        echo "Не удалось получить список применённых миграций"
        exit 1
    fi

    # Поиск и применение новых миграций
    echo "Поиск новых миграций..."
    applied_count=0
    found_any=0

    for migration_file in "$dir_migrate"/*.sql; do

        # Если шаблон не нашёл файлов, он может остаться как строка с '*'
        # Гарантируем, что обрабатываем только реальные файлы
        if [ ! -f "$migration_file" ]; then
            continue
        fi

        found_any=1

        Вопросы:
        1. строка с '*'
        2. {migration_file##*/}
        3. grep -Fxq
        4. printf "%q"
        5. Осталась ли важность нумерации файлов миграции

        # Получаем только имя файла (без пути)
        migration_name="${migration_file##*/}"

        # Проверяем, есть ли имя в списке уже применённых (точное совпадение строки)
        if echo "$applied_migrations" | grep -Fxq "$migration_name"; then
            echo "Миграция уже применена: $migration_name"
        else
            echo "Применение миграции: $migration_name"

            # Выполнение миграции
            run_sql "$migration_file"

            # Запись информации о примененной миграции
            escaped_name=$(printf "%q" "$migration_name")
            insert_sql="INSERT INTO migrations (migration_name) VALUES ('$escaped_name');"
            run_sql_c "$insert_sql"

            echo "Миграция применена успешно: $migration_name"
            applied_count=$((applied_count + 1))
        fi
    done

    if [ $found_any -eq 0 ]; then
        echo "Файлы миграций не найдены в директории $dir_migrate"
        return 0
    fi

    if [ $applied_count -eq 0 ]; then
        echo "Новых миграций для применения не найдено."
    else
        echo "Применено новых миграций: $applied_count"
    fi
}

# Основная функция
main() {
    echo "Запуск мигратора PostgreSQL"
    echo "База данных: $db_name"
    echo "Пользователь: $db_user"
    echo "Директория миграций: $dir_migrate"
    echo ""

    # Создание таблицы миграций
    create_migrations_table

    echo ""

    # Применение миграций
    apply_migrations

    echo ""
    echo "Миграция завершена)"
}

# Запуск скрипта
main