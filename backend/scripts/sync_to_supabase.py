"""
Script to sync orders from RetailCRM to Supabase
Usage: python scripts/sync_to_supabase.py
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime

import requests
from supabase import create_client

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import config

# ─── Настройки ─────────────────────────────────────────────────────────────────
SYNC_INTERVAL = 10  # секунд между синхронизациями (5 минут)
# ────────────────────────────────────────────────────────────────────────────────


def get_orders_from_retailcrm():
    """Fetch all orders from RetailCRM with pagination"""
    url = f"{config.RETAILCRM_URL}/api/v5/orders"
    all_orders = []
    page = 1
    
    try:
        while True:
            params = {
                "apiKey": config.RETAILCRM_API_KEY,
                "limit": 100,  # Max per page
                "page": page
            }
            print(f"  📄 Fetching page {page}...")
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("success"):
                orders = data.get("orders", [])
                if not orders:
                    break  # No more pages
                all_orders.extend(orders)
                print(f"    Got {len(orders)} orders")
                page += 1
            else:
                print(f"❌ RetailCRM API Error: {data.get('errorMsg')}")
                break
        
        return all_orders
    except Exception as e:
        print(f"❌ Error fetching from RetailCRM: {e}")
        return []


def sync_to_supabase(orders):
    """Sync orders to Supabase"""
    if not config.SUPABASE_URL or not config.SUPABASE_KEY:
        print("❌ Error: SUPABASE_URL or SUPABASE_KEY not set in .env")
        return False
    
    try:
        print("🔗 Connecting to Supabase...")
        supabase = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
        print("✅ Connected to Supabase")
        
        synced_count = 0
        for i, order in enumerate(orders, 1):
            try:
                order_record = {
                    "id": order.get("id"),
                    "number": order.get("number"),
                    "status": order.get("status"),
                    "created_at": order.get("createdAt"),
                    "first_name": order.get("firstName"),
                    "last_name": order.get("lastName"),
                    "phone": order.get("phone"),
                    "email": order.get("email"),
                    "total": order.get("summ", 0),
                    "currency": order.get("currency", "KZT"),
                    "items": json.dumps(order.get("items", [])),
                    "synced_at": datetime.now().isoformat(),
                }
                
                # Upsert (insert or update)
                supabase.table("orders").upsert(order_record).execute()
                synced_count += 1
                
                if i % 10 == 0:
                    print(f"  📤 Synced {i}/{len(orders)} orders...")
            
            except Exception as e:
                print(f"  ⚠️  Error syncing order {order.get('number')}: {e}")
                continue
        
        print(f"\n✅ Successfully synced {synced_count}/{len(orders)} orders to Supabase")
        return synced_count > 0
    except Exception as e:
        print(f"❌ Error connecting to Supabase: {e}")
        return False


def main():
    """Main sync function (one-time)"""
    print("=" * 60)
    print("🔄 Syncing orders from RetailCRM to Supabase")
    print("=" * 60)
    print(f"🔗 RetailCRM: {config.RETAILCRM_URL}")
    print(f"🗄️  Supabase: {config.SUPABASE_URL[:50]}...")
    print("=" * 60 + "\n")
    
    orders = get_orders_from_retailcrm()
    if not orders:
        print("⚠️  No orders found in RetailCRM")
        return False
    
    print(f"📦 Found {len(orders)} orders in RetailCRM\n")
    
    return sync_to_supabase(orders)


def monitor_sync():
    """Continuously sync orders from RetailCRM to Supabase"""
    print("=" * 60)
    print("🔄 Supabase Sync Monitor запущен!")
    print("=" * 60)
    print(f"🔗 RetailCRM: {config.RETAILCRM_URL}")
    print(f"🗄️  Supabase: {config.SUPABASE_URL[:50]}...")
    print(f"⏱️  Интервал синхронизации: {SYNC_INTERVAL} сек")
    print("=" * 60 + "\n")
    
    iteration = 1
    while True:
        try:
            now = datetime.now().strftime("%H:%M:%S")
            print(f"[{now}] Итерация #{iteration} — синхронизирую заказы...")
            
            orders = get_orders_from_retailcrm()
            if not orders:
                print("  ℹ️  No orders found")
            else:
                print(f"  📦 Found {len(orders)} orders")
                sync_to_supabase(orders)
            
        except requests.exceptions.RequestException as e:
            print(f"  ❌ Сетевая ошибка: {e}")
        except Exception as e:
            print(f"  ❌ Ошибка: {e}")
        
        iteration += 1
        time.sleep(SYNC_INTERVAL)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
