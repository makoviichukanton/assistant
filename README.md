# Vapi → Claude AI → Telegram Webhook

## Файлы
- `main.py` - основной скрипт
- `requirements.txt` - зависимости
- `Procfile` - команда запуска для Railway

### Переменные окружения (Variables в Railway)
```
ANTHROPIC_API_KEY=sk-ant-...
TELEGRAM_BOT_TOKEN=123456:ABC...
TELEGRAM_CHAT_ID=твой_chat_id
```

### Vapi
- Dashboard → Assistant → Server URL
- End of Call Report

## Cообщения в Telegram
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
