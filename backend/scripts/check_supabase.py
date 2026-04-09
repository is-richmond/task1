"""
Check Supabase orders count
Usage: python scripts/check_supabase.py
"""

import sys
from pathlib import Path
from supabase import create_client

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import config


def check_supabase():
    """Check Supabase orders table"""
    try:
        print("🔗 Connecting to Supabase...")
        supabase = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
        
        print("📊 Counting orders...\n")
        
        # Get all rows with count
        response = supabase.table("orders").select("count", count='exact').execute()
        
        count = response.count if response.count is not None else len(response.data)
        
        print(f"✅ Total orders in Supabase: {count}")
        
        # Get status breakdown
        response = supabase.table("orders").select("status").execute()
        
        if response.data:
            status_counts = {}
            for order in response.data:
                status = order.get("status", "unknown")
                status_counts[status] = status_counts.get(status, 0) + 1
            
            print("\n📈 Orders by status:")
            for status, count in sorted(status_counts.items()):
                print(f"  • {status}: {count}")
        
        # Sample of latest orders
        response = supabase.table("orders").select("number,first_name,last_name,total,status").order("id", desc=True).limit(5).execute()
        
        if response.data:
            print("\n📋 Latest 5 orders:")
            for order in response.data:
                print(f"  • {order['number']}: {order['first_name']} {order['last_name']} - {order['total']} ₸ ({order['status']})")
        
        return True
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    check_supabase()
