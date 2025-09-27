#!/bin/bash
# config.sh - файл конфигурации мигратора

# Параметры подключения к базе данных
export DB_NAME="lab-2"
export DB_USER="postgres"
export DB_HOST="localhost"
export DB_PORT="5432"

# Путь к директории с миграциями
export MIGRATIONS_DIR="./migrations"

# Пароль (рекомендуется использовать .pgpass файл)
# export PGPASSWORD="your_password"