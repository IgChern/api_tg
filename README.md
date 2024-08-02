# FastApi + Aiogram

### Описание
Проект представляет собой приложение на FastApi с двумя эндпоинтами, куда можно отправлять get(получить список сообщений)/post(отправить сообщение) запросы. Так же этот функционал реализован в Телеграм боте.

### Структура проекта
Проект состоит из 2 модулей: bot и web.  

- bot Реализует телеграм бот  
- web Это API проекта, на эндпоинты которого ориентируется телеграм бот  
- nginx Определяет настройки для проксирования запросов к двум различным сервисам, работающим в Docker.
- mongodb Используется для хранения данных.
- redis Кэширование сообщений (кэш стирается при появлении нового сообщения, хранится 120 секунд).

При отправке сообщений через бота, записывается username пользователя и content текст. Так же реализована пагинация.  

## Требования для пользования приложением

Убедитесь, что Docker и Docker-Compose установлены на вашем ПК.


### 1. Склонируйте репозиторий:

    git clone https://github.com/IgChern/api_tg

### 2. Перейдите по пути проекта:

    cd api_tg

### 3. Создайте файл .env со своими собственными настройками:

    MONGODB_URL=<your_settings>
    REDIS_URL=<your_settings>
    TELEGRAM_TOKEN=<your_settings>
    REDIS_CACHE_KEY=<your_settings>

### 4. Соберите и запустите Docker контейнер:

    docker-compose build

    docker-compose up

### 5. Доступ к интерфейсу проекта:  
1. [http://127.0.0.1:8000/api/v1/messages/](http://127.0.0.1:8000/api/v1/messages/) - Адрес возврата списка сообщений (GET)
2. [http://127.0.0.1:8000/api/v1/message/](http://127.0.0.1:8000/api/v1/message/) - Адрес отправки сообщения (POST)  
{
  "author": "name",
  "text": "text"
}
API документация:  
3. [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)  

Получить Телеграм токен вы можете у бота @BotFather, отправив команду /newbot. Следуйте инструкции и в итоге вы получите token. Вы можете отправлять сообщения только что созданному боту, а так же получать список всех сообщений командой /show.

### 6. Остановка Docker контейнера:

    docker-compose down