#!/bin/bash

# Параметры подключения к базе данных
DB_NAME="lab-2"
DB_USER="postgres"
DB_HOST="localhost"
DB_PORT="5432"

# Путь к директории с миграциями
MIGRATIONS_DIR="./migrations"

# Функция для выполнения SQL из файла
run_sql() {
    local file_name="$1"
    echo "Выполнение файла: $file_name"

    if ! psql -U "$DB_USER" -d "$DB_NAME" -h "$DB_HOST" -p "$DB_PORT" -f "$file_name"; then
        echo "Ошибка при выполнении файла: $file_name"
        exit 1
    fi
}

# Функция для выполнения SQL команды
run_sql_c() {
    local sql_query="$1"

    if ! psql -U "$DB_USER" -d "$DB_NAME" -h "$DB_HOST" -p "$DB_PORT" -c "$sql_query"; then
        echo "Ошибка при выполнении SQL запроса: $sql_query"
        exit 1
    fi
}

# Функция для выполнения SQL команды с возвратом результата (без заголовков)
run_sql_c_t() {
    local sql_query="$1"

    psql -U "$DB_USER" -d "$DB_NAME" -h "$DB_HOST" -p "$DB_PORT" -t -c "$sql_query"
}

# Создание таблицы migrations, если она не существует
create_migrations_table() {
    local create_table_sql="CREATE TABLE IF NOT EXISTS migrations (
        id SERIAL PRIMARY KEY,
        migration_name VARCHAR(255) UNIQUE NOT NULL,
        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );"

    echo "Создание таблицы migrations (если не существует)..."
    run_sql_c "$create_table_sql"
}

# Получение списка примененных миграций
get_applied_migrations() {
    local sql_query="SELECT migration_name FROM migrations;"
    run_sql_c_t "$sql_query" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' | grep -v '^$'
}

# Применение миграций
apply_migrations() {
    echo "Поиск файлов миграций в директории: $MIGRATIONS_DIR"

    # Проверка существования директории
    if [ ! -d "$MIGRATIONS_DIR" ]; then
        echo "Ошибка: Директория $MIGRATIONS_DIR не существует"
        exit 1
    fi

    # Получение списка примененных миграций
    echo "Получение списка примененных миграций..."
    applied_migrations=$(get_applied_migrations)

    # Создание массива из примененных миграций
    declare -A applied_map
    while IFS= read -r migration; do
        if [ -n "$migration" ]; then
            applied_map["$migration"]=1
        fi
    done <<< "$applied_migrations"

    # Поиск и применение новых миграций
    echo "Поиск новых миграций..."
    migration_files=("$MIGRATIONS_DIR"/*.sql)

    if [ ${#migration_files[@]} -eq 1 ] && [ ! -f "${migration_files[0]}" ]; then
        echo "Файлы миграций не найдены в директории $MIGRATIONS_DIR"
        return 0
    fi

    # Сортировка файлов по имени для последовательного применения
    mapfile -t sorted_migration_files < <(printf '%s\n' "${migration_files[@]}" | sort)

    local applied_count=0
    for migration_file in "${sorted_migration_files[@]}"; do
        if [ ! -f "$migration_file" ]; then
            continue
        fi

        migration_name=$(basename "$migration_file")

        # Проверка, была ли миграция уже применена
        if [ -n "${applied_map[$migration_name]}" ]; then
            echo "Миграция уже применена: $migration_name"
        else
            echo "Применение миграции: $migration_name"

            # Выполнение миграции
            run_sql "$migration_file"

            # Запись информации о примененной миграции
            local escaped_name
            escaped_name=$(printf "%q" "$migration_name")
            local insert_sql="INSERT INTO migrations (migration_name) VALUES ($escaped_name);"

            run_sql_c "$insert_sql"
            echo "Миграция применена успешно: $migration_name"
            ((applied_count++))
        fi
    done

    if [ $applied_count -eq 0 ]; then
        echo "Новых миграций для применения не найдено."
    else
        echo "Применено новых миграций: $applied_count"
    fi
}

# Основная функция
main() {
    echo "Запуск мигратора PostgreSQL..."
    echo "База данных: $DB_NAME"
    echo "Пользователь: $DB_USER"
    echo "Хост: $DB_HOST"
    echo "Порт: $DB_PORT"
    echo "Директория миграций: $MIGRATIONS_DIR"
    echo ""

    # Создание таблицы миграций
    create_migrations_table

    # Применение миграций
    apply_migrations

    echo ""
    echo "Миграция завершена."
}

# Проверка зависимости psql
check_dependencies() {
    if ! command -v psql &> /dev/null; then
        echo "Ошибка: psql не найден. Убедитесь, что PostgreSQL установлен."
        exit 1
    fi
}

# Обработка аргументов командной строки
while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--database)
            DB_NAME="$2"
            shift 2
            ;;
        -u|--user)
            DB_USER="$2"
            shift 2
            ;;
        -h|--host)
            DB_HOST="$2"
            shift 2
            ;;
        -p|--port)
            DB_PORT="$2"
            shift 2
            ;;
        -dir|--directory)
            MIGRATIONS_DIR="$2"
            shift 2
            ;;
        *)
            echo "Неизвестный параметр: $1"
            echo "Использование: $0 [-d database] [-u user] [-h host] [-p port] [-dir directory]"
            exit 1
            ;;
    esac
done

# Запуск скрипта
check_dependencies
main