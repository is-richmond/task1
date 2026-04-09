"""
ШАГ 3: Синхронизация RetailCRM → Supabase
Запуск: python 2_sync_to_supabase.py

Установка зависимостей:
    pip install requests supabase
"""

import requests
import json
from datetime import datetime

RETAILCRM_URL = "https://narimandilovarov11.retailcrm.ru"
RETAILCRM_API_KEY = "0maOkI6x4sko84a82gwiJ7LSkWLVw1Uq"

SUPABASE_URL = "https://mudmipuwcfcgsgqxuahj.supabase.co"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im11ZG1pcHV3Y2ZjZ3NncXh1YWhqIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NTcyNTM0OCwiZXhwIjoyMDkxMzAxMzQ4fQ.ngduV4qA1A93tY05cVUhlxvhYJTzopwE-Hx9WkcNsQA"

SUPABASE_HEADERS = {
    "apikey": SUPABASE_SERVICE_KEY,
    "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates"
}


def get_orders_from_crm(page=1, limit=100):
    """Забираем заказы из RetailCRM"""
    url = f"{RETAILCRM_URL}/api/v5/orders"
    params = {
        "apiKey": RETAILCRM_API_KEY,
        "limit": limit,
        "page": page
    }
    r = requests.get(url, params=params)
    r.raise_for_status()
    return r.json()


def upsert_to_supabase(rows):
    """Вставляем/обновляем строки в Supabase"""
    url = f"{SUPABASE_URL}/rest/v1/orders"
    r = requests.post(url, headers=SUPABASE_HEADERS, json=rows)
    r.raise_for_status()
    return r


def sync_orders():
    print("🔄 Начинаю синхронизацию RetailCRM → Supabase...\n")
    page = 1
    total_synced = 0

    while True:
        print(f"  📄 Получаю страницу {page}...")
        data = get_orders_from_crm(page=page)
        orders = data.get("orders", [])

        if not orders:
            print("  ℹ️  Заказы закончились.")
            break

        rows = []
        for o in orders:
            # Считаем сумму
            items = o.get("items", [])
            total = sum(
                i.get("initialPrice", 0) * i.get("quantity", 1)
                for i in items
            )
            # Если в заказе уже есть summ — берём его
            if o.get("summ"):
                total = float(o.get("summ"))

            rows.append({
                "id": str(o.get("id")),
                "number": o.get("number"),
                "status": o.get("status"),
                "created_at": o.get("createdAt"),
                "first_name": o.get("firstName", ""),
                "last_name": o.get("lastName", ""),
                "phone": o.get("phone", ""),
                "email": o.get("email", ""),
                "city": (o.get("delivery") or {}).get("address", {}).get("city", ""),
                "utm_source": (o.get("customFields") or {}).get("utm_source", ""),
                "total": total,
                "currency": o.get("currency", "KZT"),
                "items": json.dumps(items, ensure_ascii=False),
                "synced_at": datetime.utcnow().isoformat()
            })

        upsert_to_supabase(rows)
        total_synced += len(rows)
        print(f"  ✅ Синхронизировано {len(rows)} заказов со страницы {page}")

        pagination = data.get("pagination", {})
        if page >= pagination.get("totalPageCount", 1):
            break
        page += 1

    print(f"\n{'='*50}")
    print(f"✅ Итого синхронизировано: {total_synced} заказов")
    print(f"\n🔗 Проверь в Supabase:")
    print(f"   {SUPABASE_URL.replace('https://', 'https://app.supabase.com/project/')}/editor")


if __name__ == "__main__":
    sync_orders()
