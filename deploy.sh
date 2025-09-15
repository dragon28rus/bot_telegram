#!/bin/bash
set -e

# === Настройки ===
APP_NAME="cable_bot"
APP_DIR="/opt/${APP_NAME}"
PYTHON_BIN="/usr/bin/python3.9"
USER="botuser"    # укажите пользователя, под которым будет работать бот
GROUP="botuser"
REPO="git@github.com:dragon28rus/bot_telegram.git"
BRANCH="main"     # можно заменить на нужную ветку

# === Установка зависимостей ОС ===
echo ">>> Устанавливаю системные зависимости..."
sudo apt update
sudo apt install -y python3.9 python3.9-venv python3.9-dev sqlite3 git

# === Клонирование или обновление проекта ===
echo ">>> Загружаю проект в ${APP_DIR}..."
if [ ! -d "${APP_DIR}/.git" ]; then
  sudo mkdir -p ${APP_DIR}
  sudo chown -R $USER:$GROUP ${APP_DIR}
  sudo -u $USER git clone -b ${BRANCH} ${REPO} ${APP_DIR}
else
  cd ${APP_DIR}
  sudo -u $USER git fetch origin
  sudo -u $USER git checkout ${BRANCH}
  sudo -u $USER git pull origin ${BRANCH}
fi

# === Виртуальное окружение ===
echo ">>> Настраиваю виртуальное окружение..."
cd ${APP_DIR}
if [ ! -d "venv" ]; then
  sudo -u $USER $PYTHON_BIN -m venv venv
fi
source venv/bin/activate

# === Установка зависимостей ===
echo ">>> Ставлю зависимости..."
pip install --upgrade pip
pip install -r requirements.txt

# === Systemd сервис ===
echo ">>> Создаю systemd unit..."
SERVICE_FILE="/etc/systemd/system/${APP_NAME}.service"

sudo bash -c "cat > ${SERVICE_FILE}" <<EOL
[Unit]
Description=Telegram Bot for Cable Provider
After=network.target

[Service]
ExecStart=${APP_DIR}/venv/bin/python ${APP_DIR}/main.py
WorkingDirectory=${APP_DIR}
Restart=always
RestartSec=10
User=${USER}
Group=${GROUP}
EnvironmentFile=${APP_DIR}/.env

[Install]
WantedBy=multi-user.target
EOL

# === Перезапуск systemd ===
echo ">>> Перезапускаю systemd..."
sudo systemctl daemon-reload
sudo systemctl enable ${APP_NAME}
sudo systemctl restart ${APP_NAME}

# === Проверка ===
echo ">>> Статус сервиса:"
sudo systemctl status ${APP_NAME} --no-pager
