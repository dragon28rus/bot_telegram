# Telegram-бот провайдера: обзор проекта

## 1) Назначение
Этот проект — асинхронный Telegram-бот (aiogram 3 + aiohttp), который работает как самообслуживание абонента провайдера и как канал связи с техподдержкой.

Бот позволяет абоненту:
- авторизоваться по номеру договора и паролю статистики;
- получать баланс, тариф и последние платежи;
- смотреть новости из биллинга;
- запрашивать «обещанный платеж»;
- формировать ссылку на оплату;
- писать в техподдержку (в т.ч. с медиа).

Дополнительно бот принимает HTTP-уведомления от биллинга:
- персональные (по `contract_id`);
- массовые (рассылка всем `chat_id` из БД).

---

## 2) Быстрый архитектурный обзор
- **Точка входа:** `main.py`.
- **Бот-часть:** long polling через aiogram Dispatcher.
- **HTTP-часть:** встроенный aiohttp-сервер для webhook-уведомлений биллинга.
- **Хранилище:** SQLite (`aiosqlite`) с таблицами `users`, `support_sessions`, `support_messages`.
- **Интеграции:** BGBilling Web API (стандартные `/jsonWebApi/*` + кастомные `/api/rest/0/telegramApi/*`).

Запуск двух подсистем сделан параллельно через `asyncio.gather(...)`:
1. polling Telegram;
2. aiohttp-приложение для эндпоинтов биллинга.

---

## 3) Структура проекта

```text
bot_telegram/
├─ main.py                         # запуск бота + aiohttp сервера
├─ config.py                       # переменные окружения
├─ logger.py                       # логирование + context chat_id
├─ requirements.txt
├─ deploy.sh                       # скрипт деплоя (systemd)
├─ nginx/
│  └─ cable_bot.conf               # пример nginx-конфига
│
├─ handlers/
│  ├─ start.py                     # /start
│  ├─ auth.py                      # FSM-авторизация по договору
│  ├─ balance.py                   # баланс
│  ├─ tariff.py                    # текущий тариф + рекомендованный платеж
│  ├─ payments.py                  # последние платежи
│  ├─ payments_stub.py             # ссылка на оплату (FSM)
│  ├─ news.py                      # новости + очистка HTML
│  ├─ limit.py                     # обещанный платеж
│  ├─ support.py                   # режим техподдержки и reply-мэппинг
│  ├─ calls.py                     # телефоны отделов
│  ├─ unlink.py                    # отвязка договора
│  ├─ admin.py                     # /stop /restart /status /help_admin
│  ├─ status.py                    # /check_bot
│  ├─ sum_tariff.py                # пустой файл (не используется)
│  └─ check.py_нужно_будет _добавить  # дубль check_bot (технический мусор)
│
├─ keyboards/
│  ├─ main_menu.py                 # основная/служебные клавиатуры
│  └─ support_menu.py              # (файл есть, фактически не используется)
│
├─ services/
│  ├─ bgbilling.py                 # стандартные методы API биллинга
│  ├─ bgbilling_custom.py          # кастомные методы API биллинга
│  └─ utils.py                     # clean_html()
│
├─ db/
│  ├─ users.py                     # пользователи и привязки договоров
│  └─ support.py                   # поддержка: сессии и мэппинг сообщений
│
├─ webhooks/
│  └─ billing.py                   # /billing/notify и /billing/broadcast
│
└─ docs/
   └─ technical_spec_other_messenger.md  # детальное ТЗ для портирования
```

---

## 4) Функционал бота (по модулям)

### Пользовательские сценарии
1. **/start**
   - проверяет пользователя в БД;
   - показывает разное приветствие для авторизованных / неавторизованных / аккаунта поддержки.

2. **Авторизация (FSM)**
   - шаг 1: ввод номера договора (3–6 цифр);
   - шаг 2: ввод пароля статистики;
   - вызов API `authenticate(...)`;
   - сохранение `chat_id`, `contract_id`, `contract_title`, `password` в БД;
   - возврат в главное меню.

3. **Баланс / тариф / платежи / новости**
   - каждый раздел требует активной привязки договора (`contract_id` в БД);
   - данные подтягиваются из BGBilling API.

4. **Обещанный платеж**
   - подтверждение через отдельную клавиатуру;
   - вызов кастомного API `lowerLimit`.

5. **Оплата услуг (заглушка-поток)**
   - FSM запрашивает сумму;
   - валидация суммы (число, минимум 20 руб);
   - генерация URL оплаты.

6. **Техподдержка**
   - пользователь включает режим поддержки;
   - все сообщения пересылаются оператору;
   - оператор отвечает reply-сообщением, бот возвращает ответ пользователю с привязкой по `support_message_id`.

### Служебные сценарии
1. **Команды администратора** `/stop`, `/restart`, `/status`, `/help_admin`.
2. **Billing webhooks**
   - `POST /billing/notify` — уведомить пользователей по `contract_id`;
   - `POST /billing/broadcast` — массовая рассылка всем чатам из БД.

---

## 5) Как устроена авторизация

1. Пользователь запускает `/auth` или кнопку «🔑 Авторизоваться».
2. Бот переводит в состояние `waiting_for_contract_id`.
3. Проверка номера договора:
   - только цифры;
   - длина от 3 до 6 символов.
4. Далее состояние `waiting_for_password`.
5. Бот вызывает `services.bgbilling.authenticate(contract, password)`.
6. Из ответа забираются поля договора (с поддержкой разных форматов ключей).
7. Данные сохраняются в таблицу `users`.
8. Состояние FSM очищается.

**Особенность:** чат техподдержки (`SUPPORT_CHAT_ID`) считается специальным аккаунтом и не проходит обычную авторизацию по договору.

---

## 6) Проверки и нормализации в проекте

### Проверки входных данных
- Номер договора: `isdigit()` + длина 3..6 (`handlers/auth.py`).
- Сумма оплаты: regex на число, парсинг в `float`, минимум 20 руб (`handlers/payments_stub.py`).
- Перед вызовом большинства бизнес-методов есть guard: пользователь должен иметь `contract_id` (`balance`, `tariff`, `payments`, `news`, `limit`).

### Нормализации
- В `authenticate(...)` данные приводятся к унифицированным ключам:
  - `contractId`/`contract_id` → `contract_id` (строка),
  - `contractTitle`/`contract_title` → `contract_title`.
- Новости очищаются от HTML через `clean_html(...)`:
  - `html.unescape`,
  - удаление тегов,
  - нормализация переносов.
- В поддержке есть нормализация preview контента reply (`format_reply_info`) для разных типов сообщений.

### Защитные проверки
- Проверка прав администратора через `ADMIN_CHAT_IDS`.
- Обработка `None`/ошибок при запросах к API с пользовательскими сообщениями «попробуйте позже».
- В webhook-процедурах проверяется наличие обязательных полей JSON.

---

## 7) Что можно улучшить (приоритетный backlog)

### P0 — безопасность и корректность
1. **Webhook-аутентификация от биллинга не реализована**
   - В `config.py` есть `BILLING_API_TOKEN`, но в `webhooks/billing.py` нет проверки `Authorization`.
   - Нужно добавить middleware/проверку заголовка Bearer-токена.

2. **Безопасность хранения пароля**
   - Для сценариев, где пароль нужен при повторных запросах в биллинг, хранить только в шифрованном виде.
   - Рекомендуемый вариант: симметричное шифрование (Fernet/AES-GCM) с ключом из окружения/secret-store.

3. **Отключена SSL-проверка (`ssl=False`) во всех запросах aiohttp**
   - Хорошо для self-signed в тесте, но риск в проде.

### P1 — стабильность
4. **Ошибка/странность в `main.py`**
   - middleware объявлен, но фактически не подключается к `app` до запуска.
   - Логику setup middleware лучше вынести выше и реально вызвать.

5. **`db/users.py::add_chat` открывает соединение с БД дважды**
   - Можно оптимизировать в одно подключение.

6. **`logout_user` сбрасывает данные в пустые строки**
   - Лучше хранить `NULL` (или унифицированную модель) и добавить миграции.

### P2 — качество кода
7. **Технический мусор в репозитории**
   - `handlers/check.py_нужно_будет _добавить` — невалидное имя файла и дублирует `status.py`.
   - `handlers/sum_tariff.py` пустой.
   - `keyboards/support_menu.py` не используется.

8. **Непоследовательность типов `chat_id`**
   - Где-то `int`, где-то `str`; лучше стандартизировать по слоям.

9. **Наблюдаемость**
   - Добавить метрики (успешные/ошибочные запросы к биллингу, latency, количество активных support sessions).

---

## 8) Переменные окружения
Пример `.env`:

```dotenv
BOT_TOKEN=...
DB_PATH=./data/bot.db

BGBILLING_API_URL=https://billing.example.com
BGBILLING_USER=api_user
BGBILLING_PASSWORD=api_password
BILLING_API_TOKEN=super_secret_token

BILLING_WEBHOOK_PORT=8443
SUPPORT_CHAT_ID=123456789

ADMIN_CHAT_IDS=111111111,222222222
SUPPORT_PHONE=+7XXXXXXXXXX
BILLING_PHONE=+7YYYYYYYYYY
PAYMENT_SHOP_ID=12345
PASSWORD_ENCRYPTION_KEY=base64_fernet_key
APP_ENV=dev

LOG_LEVEL=INFO
LOG_DIR=./logs
LOG_FILE=bot.log
```

При старте бот проверяет обязательные переменные окружения и завершится с ошибкой, если они отсутствуют (в т.ч. дополнительные проверки для `APP_ENV=production`). 

---

## 9) Локальный запуск

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

### Миграция ранее сохранённых plaintext-паролей
После добавления `PASSWORD_ENCRYPTION_KEY` выполните одноразовую миграцию:

```bash
python -m scripts.migrate_encrypt_passwords
```

---

## 10) Docker / Docker Compose

### Сборка и запуск

```bash
docker compose up -d --build
```

### Остановка

```bash
docker compose down
```

### Важные переменные для контейнера
- `APP_ENV=production` — включает strict-проверку шифрования при старте.
- `PASSWORD_ENCRYPTION_KEY=...` — ключ шифрования паролей (обязателен для production).
- `BILLING_WEBHOOK_HOST=0.0.0.0` — обязательно для приёма webhook извне контейнера.
- `BILLING_WEBHOOK_PORT=8443` — порт aiohttp-сервера (пробрасывается в compose).
- `TZ=Etc/UTC` (или `Europe/Moscow`) — таймзона контейнера/логов.
- `RUN_PASSWORD_MIGRATION_ON_START=true` — одноразово прогоняет миграцию plaintext-паролей перед запуском бота.

> Рекомендуется включать `RUN_PASSWORD_MIGRATION_ON_START=true` только на первый старт после выкладки ключа.
> В compose дополнительно проброшены `/etc/localtime` и `/etc/timezone` в read-only для согласования времени контейнера с хостом.

---

## 11) Деплой
- Базовый автоматический деплой: `deploy.sh`.
- Пример nginx: `nginx/cable_bot.conf`.
- Для production рекомендуется:
  - запуск через systemd;
  - reverse proxy (nginx);
  - TLS с валидным сертификатом;
  - ограничение доступа к billing-webhook endpoint по IP и Bearer-токену.
  - хранение `PASSWORD_ENCRYPTION_KEY` в секрет-хранилище (не в git).
  - `APP_ENV=production`: бот не стартует без валидного `PASSWORD_ENCRYPTION_KEY`.

---

## 12) Документ для портирования в другой мессенджер
Детальное ТЗ находится в файле:

- `docs/technical_spec_other_messenger.md`
