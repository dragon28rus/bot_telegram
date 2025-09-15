# 📡 Telegram-бот для провайдера

Этот бот позволяет абонентам:
- Авторизоваться по договору
- Проверять баланс и тариф
- Получать новости
- Общаться с технической поддержкой 👨‍💻
- Уведомлять абонентов о балансе и новостях со стороны биллинга

## 🚀 Возможности поддержки
- Абонент входит в чат с поддержкой по кнопке **✉️ Техподдержка**
- Все сообщения (текст, фото, документы, голосовые, видео и др.) пересылаются оператору
- Оператор отвечает **через reply**, и абонент получает ответ с цитатой
- Поддерживаются **неавторизованные пользователи** (отмечаются как "Не авторизованный пользователь")
- История сообщений хранится в базе SQLite

---

## ⚙️ Установка

для быстрой установки можно воспользоваться deploy.sh

### 1. Установите зависимости
sudo apt update
sudo apt install -y python3.9 python3.9-venv python3.9-dev sqlite3

### 2. Создайте виртуальное окружение
python3.9 -m venv venv
source venv/bin/activate

### 3. Установите библиотеки
pip install --upgrade pip
pip install -r requirements.txt

requirements.txt содержит:
aiogram>=3.0.0
aiohttp>=3.8.0
aiosqlite
python-dotenv>=0.20.0
html2text==2020.1.16
beautifulsoup4>=4.12.0

## 🔑 Настройки
Переименуйте файл .env_original в .env в корне проекта и заполните все параметры

## 🗂 Структура проекта
bot_telegram/
│── main.py                # Точка входа
│── config.py              # Загрузка настроек из .env
│── logger.py              # Логирование
│── keyboards/
│   └── main_menu.py       # Основное меню бота
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
│── db/
│   ├── __init__.py
│   ├── support.py         # Работа с техподдержкой
│   └── users.py           # Пользователи
│── services/              # Взаимодействие с внешними API
│   ├── __init__.py
│   ├── bgbilling.py       # API-клиент к /jsonWebApi/*
│   └── utils.py           # Вспомогательные функции (например очистка html)
│── webhooks/              # Вебхуки от биллинга
│   ├── __init__.py
│   └── billing.py         # Handlers для уведомлений от биллинга
│── .env                   # Настройки
│── requirements.txt       # Зависимости

## Особенности вебхуков биллинга
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

## ▶️ Запуск
cd bot_telegram
source ../venv/bin/activate
python main.py

## 📲 Сценарий работы

## ⚡ Автозапуск бота через systemd

### 1. Создайте сервисный файл
Создайте файл `/etc/systemd/system/cable_bot.service`:

```ini
[Unit]
Description=Telegram Bot for Cable Provider
After=network.target

[Service]
# Путь до Python в виртуальном окружении
ExecStart=/opt/cable_bot/venv/bin/python /opt/cable_bot/main.py
WorkingDirectory=/opt/cable_bot
Environment="BOT_TOKEN=ваш_токен"
Environment="SUPPORT_CHAT_ID=123456789"
Restart=always
RestartSec=10
User=botuser
Group=botuser

[Install]
WantedBy=multi-user.target

⚠️ Замените:
/opt/cable_bot → путь до вашего проекта
botuser → пользователя Linux, от имени которого должен работать бот

### 2. Перезапустите systemd
sudo systemctl daemon-reload

### 3. Запустите бота
sudo systemctl start cable_bot

### 4. Включите автозапуск
sudo systemctl enable cable_bot

### 5. Проверяйте статус и логи
sudo systemctl status cable_bot
journalctl -u cable_bot -f

Теперь бот работает в фоне и будет запускаться при старте системы 🚀