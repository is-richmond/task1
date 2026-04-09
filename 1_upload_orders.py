"""
ШАГ 2 (исправленный): Загрузка mock_orders.json в RetailCRM
Запуск: python3 1_upload_orders.py
"""

import requests
import json
import time

RETAILCRM_URL = "https://narimandilovarov11.retailcrm.ru"
RETAILCRM_API_KEY = "0maOkI6x4sko84a82gwiJ7LSkWLVw1Uq"


def get_first_site():
    """Узнаём символьный код сайта — он обязателен в RetailCRM"""
    # Try different endpoint approaches
    endpoints = [
        f"{RETAILCRM_URL}/api/v5/account",
        f"{RETAILCRM_URL}/api/v5/settings",
    ]
    
    for url in endpoints:
        try:
            print(f"  Trying {url.split('/')[-1]}...")
            r = requests.get(url, params={"apiKey": RETAILCRM_API_KEY}, timeout=5)
            data = r.json()
            print(f"  Response: {json.dumps(data, ensure_ascii=False)[:200]}...")
            
            # Try to extract site code from response
            if data.get("success"):
                # From account
                if "account" in data and "sites" in data["account"]:
                    sites = data["account"]["sites"]
                    if isinstance(sites, dict):
                        code = list(sites.keys())[0]
                    elif isinstance(sites, list) and len(sites) > 0:
                        code = sites[0].get("code")
                    if code:
                        print(f"  ℹ️  Найден сайт: {code}")
                        return code
        except requests.Timeout:
            print(f"  Timeout on {url}")
        except Exception as e:
            print(f"  Error: {str(e)[:100]}")
    
    # Fallback to trying just the store name
    possible_sites = ["narimandilovarov11"]  # Try the store name from the URL
    for site in possible_sites:
        print(f"  Trying with hardcoded site code: {site}")
        return site
    
    print(f"  ⚠️  Using default site code: 'default'")
    return "default"


def get_order_types():
    """Узнаём доступные типы заказов"""
    # Order types endpoint doesn't exist in this API, skip it
    return None


def get_order_statuses():
    """Узнаём доступные статусы заказов"""
    url = f"{RETAILCRM_URL}/api/v5/reference/statuses"
    try:
        r = requests.get(url, params={"apiKey": RETAILCRM_API_KEY}, timeout=5)
        data = r.json()
        statuses = data.get("statuses", {})
        if statuses:
            code = list(statuses.keys())[0]
            print(f"  ℹ️  Найден статус: {code}")
            return code
    except Exception as e:
        print(f"  Warning: Could not get statuses: {e}")
    return "new"


def calculate_summ(items):
    total = 0
    for item in items:
        total += item.get("initialPrice", 0) * item.get("quantity", 1)
    return total


def upload_order(order, number, site_code, status_code, order_type):
    url = f"{RETAILCRM_URL}/api/v5/orders/create"
    params = {"apiKey": RETAILCRM_API_KEY, "site": site_code}

    order_data = {
        "number": f"ORD-{number:03d}",
        "site": site_code,
        "status": status_code,
        "firstName": order.get("firstName", ""),
        "lastName": order.get("lastName", ""),
        "phone": order.get("phone", ""),
        "email": order.get("email", ""),
        "items": order.get("items", []),
        "delivery": order.get("delivery", {}),
        "customFields": order.get("customFields", {}),
        "summ": calculate_summ(order.get("items", [])),
    }
    
    # Don't send orderType - let RetailCRM use defaults
    # Only add orderMethod if provided in the order
    if order.get("orderMethod"):
        order_data["orderMethod"] = order.get("orderMethod")

    data = {"order": json.dumps(order_data, ensure_ascii=False)}
    response = requests.post(url, params=params, data=data, timeout=5)
    return response.json()


def main():
    print("🔍 Получаю настройки RetailCRM...\n")

    site_code = get_first_site()
    if not site_code:
        print("❌ Не удалось получить код сайта. Проверь API-ключ.")
        return

    order_type = get_order_types()
    status_code = get_order_statuses()
    type_str = f"тип='{order_type}'" if order_type else "тип=default"
    print(f"\n✅ Буду использовать: сайт='{site_code}', {type_str}, статус='{status_code}'\n")
    time.sleep(0.5)

    with open("mock_orders.json", "r", encoding="utf-8") as f:
        orders = json.load(f)

    print(f"📦 Найдено {len(orders)} заказов. Начинаю загрузку...\n")

    success_count = 0
    error_count = 0

    for i, order in enumerate(orders, start=1):
        result = upload_order(order, i, site_code, status_code, order_type)
        name = f"{order.get('firstName')} {order.get('lastName')}"
        summ = calculate_summ(order.get("items", []))

        if result.get("success"):
            success_count += 1
            print(f"  ✅ [{i:02d}/50] ORD-{i:03d} | {name} | {summ:,} ₸")
        else:
            error_count += 1
            err = result.get("errorMsg") or str(result.get("errors", "неизвестная ошибка"))
            print(f"  ❌ [{i:02d}/50] ORD-{i:03d} | {name} | Ошибка: {err}")
            if error_count == 1:
                print(f"       Полный ответ: {json.dumps(result, ensure_ascii=False)}")

        time.sleep(0.4)

    print(f"\n{'='*50}")
    print(f"✅ Успешно загружено: {success_count}")
    print(f"❌ Ошибок: {error_count}")
    if success_count > 0:
        print(f"\n🔗 Проверь в RetailCRM:")
        print(f"   {RETAILCRM_URL}/orders/list")


if __name__ == "__main__":
    main()