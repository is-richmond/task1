"""
ШАГ 5: Telegram-бот — уведомления о заказах > 50,000 ₸
Запуск: python 4_telegram_bot.py

Установка:
    pip install requests
"""

import requests
import time
import json
from datetime import datetime, timedelta

# ─── Настройки ─────────────────────────────────────────────────────────────────
RETAILCRM_URL    = "https://narimandilovarov11.retailcrm.ru"
RETAILCRM_API_KEY = "0maOkI6x4sko84a82gwiJ7LSkWLVw1Uq"

TELEGRAM_TOKEN   = "8581023039:AAETaZUL7SwX5VlvxL9PfTLe8zmHzsGHmNQ"
TELEGRAM_CHAT_ID = "894877615"

THRESHOLD        = 50_000   # ₸ — порог уведомления
CHECK_INTERVAL   = 60       # секунд между проверками
LOOKBACK_MINUTES = 6        # смотрим заказы за последние N минут
# ────────────────────────────────────────────────────────────────────────────────

notified_ids = set()  # храним ID уже отправленных заказов


def send_telegram(text: str):
    """Отправляем сообщение в Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    r = requests.post(url, json=payload, timeout=10)
    return r.json()


def calculate_summ(order: dict) -> float:
    """Считаем сумму заказа"""
    # Если RetailCRM вернул summ — берём его
    if order.get("summ"):
        return float(order["summ"])
    # Иначе считаем из items
    total = 0
    for item in order.get("items", []):
        total += item.get("initialPrice", 0) * item.get("quantity", 1)
    return total


def get_recent_orders() -> list:
    """Получаем заказы за последние LOOKBACK_MINUTES минут"""
    since = (datetime.utcnow() - timedelta(minutes=LOOKBACK_MINUTES)).strftime("%Y-%m-%d %H:%M:%S")
    url = f"{RETAILCRM_URL}/api/v5/orders"
    params = {
        "apiKey": RETAILCRM_API_KEY,
        "filter[createdAtFrom]": since,
        "limit": 100
    }
    r = requests.get(url, params=params, timeout=15)
    r.raise_for_status()
    return r.json().get("orders", [])


def format_items(items: list) -> str:
    """Форматируем список товаров"""
    lines = []
    for item in items:
        name = item.get("productName", "Товар")
        qty  = item.get("quantity", 1)
        price = item.get("initialPrice", 0)
        lines.append(f"  • {name} × {qty} = {price * qty:,} ₸")
    return "\n".join(lines) if lines else "  • нет данных"


def check_and_notify():
    """Проверяем новые заказы и отправляем уведомления"""
    orders = get_recent_orders()
    new_notifications = 0

    for order in orders:
        order_id = order.get("id")
        total = calculate_summ(order)

        # Уведомляем только если: сумма > порога И ещё не уведомляли
        if total >= THRESHOLD and order_id not in notified_ids:
            notified_ids.add(order_id)
            new_notifications += 1

            name    = f"{order.get('firstName', '')} {order.get('lastName', '')}".strip() or "Неизвестно"
            phone   = order.get("phone") or "—"
            email   = order.get("email") or "—"
            number  = order.get("number") or f"#{order_id}"
            status  = order.get("status") or "—"
            city    = (order.get("delivery") or {}).get("address", {}).get("city", "—")
            utm     = (order.get("customFields") or {}).get("utm_source", "—")
            items   = format_items(order.get("items", []))

            msg = (
                f"🔔 <b>Крупный заказ!</b>\n"
                f"{'─'*30}\n"
                f"📋 Заказ: <b>{number}</b>\n"
                f"👤 Клиент: <b>{name}</b>\n"
                f"📞 Телефон: {phone}\n"
                f"📧 Email: {email}\n"
                f"🏙️ Город: {city}\n"
                f"📣 Источник: {utm}\n"
                f"{'─'*30}\n"
                f"🛍️ Товары:\n{items}\n"
                f"{'─'*30}\n"
                f"💰 Итого: <b>{total:,.0f} ₸</b>\n"
                f"📦 Статус: {status}\n"
                f"🕐 {datetime.now().strftime('%d.%m.%Y %H:%M')}"
            )

            result = send_telegram(msg)
            if result.get("ok"):
                print(f"  📨 Уведомление отправлено: {number} | {name} | {total:,.0f} ₸")
            else:
                print(f"  ⚠️ Ошибка Telegram: {result}")

    return new_notifications


def main():
    print("=" * 50)
    print("🤖 Nova Telegram Bot запущен!")
    print(f"   Порог уведомлений: {THRESHOLD:,} ₸")
    print(f"   Интервал проверки: {CHECK_INTERVAL} сек")
    print(f"   RetailCRM: {RETAILCRM_URL}")
    print("=" * 50)

    # Стартовое сообщение
    send_telegram(
        f"✅ <b>Nova Bot запущен!</b>\n"
        f"Слежу за заказами больше <b>{THRESHOLD:,} ₸</b>\n"
        f"Проверяю каждые {CHECK_INTERVAL} секунд 🚀"
    )

    iteration = 1
    while True:
        try:
            now = datetime.now().strftime("%H:%M:%S")
            print(f"\n[{now}] Итерация #{iteration} — проверяю заказы...")
            count = check_and_notify()
            if count == 0:
                print(f"  ℹ️  Новых крупных заказов нет")
            else:
                print(f"  ✅ Отправлено уведомлений: {count}")
        except requests.exceptions.RequestException as e:
            print(f"  ❌ Сетевая ошибка: {e}")
        except Exception as e:
            print(f"  ❌ Неожиданная ошибка: {e}")

        iteration += 1
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
