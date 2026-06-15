import os
import json
import requests
from flask import Flask, request, jsonify
from datetime import datetime
import openai

app = Flask(__name__)

openai.api_key = os.environ.get("OPENAI_API_KEY")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")


def analyze_call_with_ai(transcript: str) -> dict:
    prompt = f"""Ты получаешь транскрипт телефонного разговора на немецком языке.

Проанализируй разговор и ответь СТРОГО в JSON формате.

Определи:

1. Имя человека, если он представился. Если имени нет, напиши "Не представился".

2. Приоритет звонка:

- "wichtig" → если звонок требует обязательного контакта (потєнциальный или имеющийся клиент, Finanzamt, Behörden, банк, адвокат, официальный запрос, важный деловой контакт).
- "normal" → если человек лично знает Антона, друг, знакомый, родственник, просит связаться лично, звонок по оставленному резюме, опрос и тп., что не требут срочного обратного звонка или может быть проигнорировано.
- "spam" → мошенники, реклама, навязывание услуг, холодные продажи, подозрительные звонки.

3. Причину звонка — коротко на русском (1 предложение).

4. Сделай дословный перевод речи звонящего на русский язык. Не сокращай. Передай максимально близко к оригиналу.

5. Выдели оригинальную речь звонящего на немецком языке. Не сокращай.

Ответь строго так:

{{
  "name": "",
  "priority": "",
  "reason": "",
  "russian_transcript": "",
  "german_transcript": ""
}}

Транскрипт:

{transcript}

Отвечай только JSON без дополнительных слов."""

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.choices[0].message.content.strip()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        data = {
            "kategorie": "Sonstiges",
            "was_wollte": raw,
            "original_aussage": "Nicht verfügbar"
        }
    return data


def send_telegram_message(text: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    requests.post(url, json=payload)


@app.route("/webhook", methods=["POST"])
def vapi_webhook():
    data = request.json or {}

    message = data.get("message", {})
    if message.get("type") != "end-of-call-report":
        return jsonify({"status": "ignored"}), 200

    call = message.get("call", {})
    transcript = message.get("transcript", "Нет транскрипта")

    caller_number = call.get("customer", {}).get("number", "Неизвестен")
    duration_seconds = int(message.get("durationSeconds", 0))

    duration_min = duration_seconds // 60
    duration_sec = duration_seconds % 60

    if transcript and transcript != "Нет транскрипта":
        ai_result = analyze_call_with_ai(transcript)
    else:
        ai_result = {
            "name": "Не представился",
            "priority": "normal",
            "reason": "Транскрипт недоступен",
            "russian_transcript": "—",
            "german_transcript": "—"
        }

    priority_map = {
    "wichtig": "🔴 Важно",
    "normal": "🟡 Обычный",
    "spam": "⚫ Спам"
    }

    priority = ai_result.get("priority", "").strip().lower()
    
    msg = f"""📞 <b>Новый звонок</b>

👤 <b>Имя:</b> {ai_result.get('name', '—')}
📱 <b>Номер:</b> <code>{caller_number}</code>

🚨 <b>Приоритет:</b> {priority_map.get(priority, '🟡 Обычный')}

📌 <b>Причина звонка:</b>
{ai_result.get('reason', '—')}

🇷🇺 <b>Транскрипт (RU):</b>
{ai_result.get('russian_transcript', '—')}

🇩🇪 <b>Транскрипт (DE):</b>
<i>{ai_result.get('german_transcript', '—')}</i>"""

    send_telegram_message(msg)
    return jsonify({"status": "ok"}), 200


@app.route("/", methods=["GET", "POST"])
def health():
    print("POST OR GET HIT ROOT")
    return "OK", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
