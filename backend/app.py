"""Backend API for RetailCRM Orders"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import sys
import threading
from pathlib import Path

# Add current dir to path
sys.path.insert(0, str(Path(__file__).parent))

from config import config
from scripts.upload_orders import upload_order, get_order_statuses, get_orders_list
from scripts import telegram_bot
from scripts import sync_to_supabase

app = Flask(__name__)
CORS(app)


@app.route("/api/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "message": "API is running"
    })


@app.route("/api/config", methods=["GET"])
def get_config():
    """Get non-sensitive configuration"""
    return jsonify({
        "retailcrm_url": config.RETAILCRM_URL,
        "supabase_url": config.SUPABASE_URL,
    })


@app.route("/api/orders/upload", methods=["POST"])
def upload_orders():
    """Upload orders endpoint"""
    try:
        data = request.get_json()
        orders = data.get("orders", [])
        
        if not orders:
            return jsonify({"success": False, "error": "No orders provided"}), 400
        
        site_code = config.RETAILCRM_SITE_CODE
        status_code = get_order_statuses()
        
        results = []
        for i, order in enumerate(orders, 1):
            result = upload_order(order, i, site_code, status_code)
            results.append(result)
        
        success_count = sum(1 for r in results if r.get("success"))
        
        return jsonify({
            "success": True,
            "uploaded": success_count,
            "total": len(orders),
            "results": results
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/api/orders/status", methods=["GET"])
def get_orders_status():
    """Get order statuses and list of orders"""
    try:
        result = get_orders_list()
        return jsonify(result)
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "orders": [],
            "count": 0
        }), 500


@app.route("/api/orders/supabase", methods=["GET"])
def get_orders_from_supabase():
    """Get orders from Supabase (synced data)"""
    try:
        from supabase import create_client
        import json as json_lib
        
        supabase = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
        response = supabase.table("orders").select("*").execute()
        
        orders = response.data if response.data else []
        
        # Parse items JSON if needed
        for order in orders:
            if isinstance(order.get("items"), str):
                try:
                    order["items"] = json_lib.loads(order["items"])
                except:
                    order["items"] = []
            if not order.get("items"):
                order["items"] = []
        
        return jsonify({
            "success": True,
            "orders": orders,
            "count": len(orders)
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "orders": [],
            "count": 0
        }), 500


if __name__ == "__main__":
    port = config.API_PORT
    debug = config.FLASK_DEBUG
    print(f"🚀 Starting API server on http://localhost:{port}")
    
    # Start Telegram bot in a separate thread
    print("📱 Starting Telegram bot...")
    bot_thread = threading.Thread(target=telegram_bot.main, daemon=True)
    bot_thread.start()
    
    # Start Supabase sync in a separate thread
    print("🔄 Starting Supabase sync monitor...")
    sync_thread = threading.Thread(target=sync_to_supabase.monitor_sync, daemon=True)
    sync_thread.start()
    
    app.run(host="0.0.0.0", port=port, debug=debug)
