# Vapi → Claude AI → Telegram Webhook

## Файлы
- `main.py` — основной скрипт
- `requirements.txt` — зависимости
- `Procfile` — команда запуска для Railway

## Деплой на Railway

### 1. GitHub
Создай репозиторий на github.com и загрузи все 4 файла.

### 2. Railway
- New Project → GitHub Repository → выбери репо
- После деплоя Railway даст URL вида: `https://твой-проект.up.railway.app`

### 3. Переменные окружения (Variables в Railway)
Добавь три переменные:
```
ANTHROPIC_API_KEY=sk-ant-...
TELEGRAM_BOT_TOKEN=123456:ABC...
TELEGRAM_CHAT_ID=твой_chat_id
```

### 4. Vapi
- Dashboard → Assistant → Server URL
- Вставь: `https://твой-проект.up.railway.app/webhook`
- Включи только: End of Call Report

## Как получить TELEGRAM_CHAT_ID
1. Напиши боту @userinfobot в Telegram
2. Он пришлёт твой chat_id

## Пример сообщения в Telegram
```
📞 Новый звонок

📅 Дата: 15.06.2026
🕐 Время: 14:32
👤 Номер: +49123456789
⏱ Длительность: 2м 15с

🏷 Категория: Anfrage

🇷🇺 Что хотел (перевод):
Клиент хотел узнать о стоимости создания сайта для кафе. Интересовался сроками и возможностью добавить меню онлайн.

🇩🇪 Оригинал (Deutsch):
Ich möchte eine Website für mein Café erstellen lassen, was kostet das ungefähr?
```
