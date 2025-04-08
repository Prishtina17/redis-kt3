@echo off

pip install -r requirements.txt

:: Проверка, существует ли контейнер my-redis
docker inspect my-redis >nul 2>&1
if %errorlevel% equ 0 (
    echo Контейнер my-redis уже существует.
    :: Проверка, запущен ли контейнер
    docker inspect -f '{{.State.Running}}' my-redis | find "true" >nul
    if %errorlevel% equ 0 (
        echo Контейнер my-redis уже запущен.
    ) else (
        echo Запуск существующего контейнера my-redis...
        docker start my-redis
    )
) else (
    echo Создание и запуск нового контейнера my-redis...
    docker run --name my-redis -d -p 6379:6379 redis
)

python main.py