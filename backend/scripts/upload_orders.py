"""
Script to upload orders from JSON to RetailCRM
Usage: python -m scripts.upload_orders
"""

import sys
import json
import time
import requests
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import config


def get_first_site():
    """Get site code from RetailCRM"""
    endpoints = [
        f"{config.RETAILCRM_URL}/api/v5/account",
        f"{config.RETAILCRM_URL}/api/v5/settings",
    ]
    
    for url in endpoints:
        try:
            print(f"  Trying {url.split('/')[-1]}...")
            r = requests.get(url, params={"apiKey": config.RETAILCRM_API_KEY}, timeout=5)
            data = r.json()
            
            if data.get("success"):
                print(f"  ✓ API is working")
                return config.RETAILCRM_SITE_CODE
        except requests.Timeout:
            print(f"  Timeout on {url}")
        except Exception as e:
            print(f"  Error: {str(e)[:100]}")
    
    print(f"  ⚠️  Using configured site code: '{config.RETAILCRM_SITE_CODE}'")
    return config.RETAILCRM_SITE_CODE


def get_order_statuses():
    """Get available order statuses"""
    url = f"{config.RETAILCRM_URL}/api/v5/reference/statuses"
    try:
        r = requests.get(url, params={"apiKey": config.RETAILCRM_API_KEY}, timeout=5)
        data = r.json()
        statuses = data.get("statuses", {})
        if statuses:
            code = list(statuses.keys())[0]
            print(f"  ℹ️  Found status: {code}")
            return code
    except Exception as e:
        print(f"  Warning: Could not get statuses: {e}")
    return "new"


def get_orders_list(limit=100):
    """Get list of orders from RetailCRM"""
    url = f"{config.RETAILCRM_URL}/api/v5/orders"
    try:
        params = {
            "apiKey": config.RETAILCRM_API_KEY,
            "limit": limit,
            "sortOrder": "desc"
        }
        r = requests.get(url, params=params, timeout=5)
        data = r.json()
        
        if data.get("success"):
            orders = data.get("orders", [])
            return {
                "success": True,
                "orders": orders,
                "count": len(orders)
            }
        else:
            return {
                "success": False,
                "error": data.get("error", "Unknown error"),
                "orders": [],
                "count": 0
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "orders": [],
            "count": 0
        }


def calculate_summ(items):
    """Calculate total sum from items"""
    total = 0
    for item in items:
        total += item.get("initialPrice", 0) * item.get("quantity", 1)
    return total


def upload_order(order, number, site_code, status_code):
    """Upload single order to RetailCRM"""
    url = f"{config.RETAILCRM_URL}/api/v5/orders/create"
    params = {"apiKey": config.RETAILCRM_API_KEY, "site": site_code}

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
    
    if order.get("orderMethod"):
        order_data["orderMethod"] = order.get("orderMethod")

    data = {"order": json.dumps(order_data, ensure_ascii=False)}
    response = requests.post(url, params=params, data=data, timeout=5)
    return response.json()


def main():
    """Main function to upload orders"""
    print("🔍 Loading RetailCRM settings...\n")

    # Validate config
    if not config.RETAILCRM_API_KEY:
        print("❌ Error: RETAILCRM_API_KEY not set in .env")
        return False
    
    if not config.RETAILCRM_URL:
        print("❌ Error: RETAILCRM_URL not set in .env")
        return False

    site_code = get_first_site()
    status_code = get_order_statuses()
    
    print(f"\n✅ Using: site='{site_code}', status='{status_code}'\n")
    time.sleep(0.5)

    # Load orders from JSON
    orders_file = Path(__file__).parent.parent.parent / "data" / "mock_orders.json"
    if not orders_file.exists():
        print(f"❌ Error: {orders_file} not found")
        return False

    with open(orders_file, "r", encoding="utf-8") as f:
        orders = json.load(f)

    print(f"📦 Found {len(orders)} orders. Starting upload...\n")

    success_count = 0
    error_count = 0

    for i, order in enumerate(orders, start=1):
        result = upload_order(order, i, site_code, status_code)
        name = f"{order.get('firstName')} {order.get('lastName')}"
        summ = calculate_summ(order.get("items", []))

        if result.get("success"):
            success_count += 1
            print(f"  ✅ [{i:02d}] ORD-{i:03d} | {name} | {summ:,} ₸")
        else:
            error_count += 1
            err = result.get("errorMsg") or str(result.get("errors", "unknown error"))
            print(f"  ❌ [{i:02d}] ORD-{i:03d} | {name} | Error: {err}")

        time.sleep(0.4)

    print(f"\n{'='*60}")
    print(f"✅ Successfully uploaded: {success_count}")
    print(f"❌ Errors: {error_count}")
    
    if success_count > 0:
        print(f"\n🔗 Check in RetailCRM:")
        print(f"   {config.RETAILCRM_URL}/orders/list")
    
    return success_count == len(orders)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
