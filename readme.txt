структура

bot_telegram/
│── main.py                # Точка входа, запуск бота
│── config.py              # Загрузка настроек из .env
│── logger.py              # Логирование
│── keyboards/             # Кнопки (Reply и Inline)
│   ├── main_menu.py
│   └── support_menu.py
│── handlers/              # Обработчики команд и событий
│   ├── __init__.py
│   ├── start.py           # /start и главное меню
│   ├── auth.py            # Авторизация (номер договора + пароль)
│   ├── balance.py         # Запрос баланса
│   ├── news.py            # Новости (с очисткой html)
│   ├── tariff.py          # Текущий тариф
│   ├── payments.py        # Последние платежи
│   ├── support.py         # Техподдержка (текст + медиа, ответы)
│   ├── calls.py           # Кнопки «Позвонить»
│   ├── payments_stub.py   # Заглушка «Оплатить услуги»
│   ├── unlink.py          # Отвязать договор
│   └── admin.py           # Команды для админа (/stop, /restart, /status)
│── services/              # Взаимодействие с внешними API
│   ├── __init__.py
│   ├── bgbilling.py       # API-клиент к /jsonWebApi/*
│   └── utils.py           # Вспомогательные функции (например очистка html)
│── db/                    
│   ├── __init__.py
│   ├── database.py        # Подключение к SQLite
│   ├── models.py          # SQL-запросы (создание таблиц)
│   ├── users.py           # Работа с пользователями (авторизация, отвязка)
│   └── support.py         # Работа с сообщениями техподдержки
│── webhooks/              # Вебхуки от биллинга
│   ├── __init__.py
│   └── billing.py         # Handlers для уведомлений от биллинга
│── .env                   # Настройки окружения
│── requirements.txt       # Зависимости

Особенности вебхуков биллинга
handle_billing_notification
Принимает JSON вида:

{
  "contract_id": 703,
  "message": "Ваш баланс изменился"
}

По contract_id находит chat_id пользователя в БД.
Отправляет сообщение конкретному пользователю.
handle_broadcast_notification
Принимает JSON:

{
  "message": "Уважаемые абоненты, плановые работы..."
}

Получает список всех chat_id из БД.
Рассылает сообщение каждому.
Авторизация запросов
Все запросы требуют заголовка:
Authorization: Bearer <BILLING_API_TOKEN>
Токен хранится в .env.