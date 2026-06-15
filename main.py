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
    prompt = f"""Du bekommst ein Transkript eines Telefongesprächs auf Deutsch. Analysiere es und antworte NUR auf Russisch im folgenden JSON-Format:

{{
  "kategorie": "eine der folgenden: Bestellung, Anfrage, Beschwerde, Rückruf, Spam, Sonstiges",
  "was_wollte": "kurze Zusammenfassung auf Russisch was der Anrufer wollte (2-3 Sätze)",
  "original_aussage": "die wichtigste originale Aussage des Anrufers auf Deutsch (1-2 Sätze)"
}}

Transkript:
{transcript}

Antworte NUR mit dem JSON-Objekt, ohne zusätzlichen Text."""

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
    start_time_str = call.get("startedAt", "")

    try:
        dt = datetime.fromisoformat(start_time_str.replace("Z", "+00:00"))
        date_formatted = dt.strftime("%d.%m.%Y")
        time_formatted = dt.strftime("%H:%M")
    except Exception:
        date_formatted = "—"
        time_formatted = "—"

    duration_min = duration_seconds // 60
    duration_sec = duration_seconds % 60

    if transcript and transcript != "Нет транскрипта":
        ai_result = analyze_call_with_ai(transcript)
    else:
        ai_result = {
            "kategorie": "Unbekannt",
            "was_wollte": "Транскрипт недоступен",
            "original_aussage": "—"
        }

    msg = f"""📞 <b>Новый звонок</b>

📅 <b>Дата:</b> {date_formatted}
🕐 <b>Время:</b> {time_formatted}
👤 <b>Номер:</b> <code>{caller_number}</code>
⏱ <b>Длительность:</b> {duration_min}м {duration_sec}с

🏷 <b>Категория:</b> {ai_result.get('kategorie', '—')}

🇷🇺 <b>Транскрипт + перевод звонка:</b>
{ai_result.get('was_wollte', '—')}

🇩🇪 <b>Оригинал (Deutsch):</b>
<i>{ai_result.get('original_aussage', '—')}</i>"""

    send_telegram_message(msg)
    return jsonify({"status": "ok"}), 200


@app.route("/", methods=["GET", "POST"])
def health():
    print("POST OR GET HIT ROOT")
    return "OK", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
