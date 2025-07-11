import pandas as pd
import random
from datetime import datetime, timedelta

# ------------------------------
# 🧠 Simulated Buyer Profiles
# ------------------------------
buyer_profiles = [
    {"name": "Tandoori Express", "zone": "Zone A", "channel": "WhatsApp", "distance_km": 1, "engagement_score": 8, "last_engaged": "2025-07-09"},
    {"name": "Green Leaf NGO", "zone": "Zone A", "channel": "Email", "distance_km": 3, "engagement_score": 5, "last_engaged": "2025-07-07"},
    {"name": "Hostel Delight", "zone": "Zone B", "channel": "SMS", "distance_km": 2, "engagement_score": 6, "last_engaged": "2025-07-10"},
    {"name": "Anna Daana NGO", "zone": "Zone B", "channel": "WhatsApp", "distance_km": 4, "engagement_score": 7, "last_engaged": "2025-07-08"},
    {"name": "Kitchen 360", "zone": "Zone C", "channel": "Slack", "distance_km": 5, "engagement_score": 4, "last_engaged": "2025-07-05"},
    {"name": "Feed Forward Foundation", "zone": "Zone C", "channel": "Email", "distance_km": 1, "engagement_score": 9, "last_engaged": "2025-07-10"}
]

# ------------------------------
# 🔁 Retry Queue for Unsold SKUs
# ------------------------------
retry_queue = []

# ------------------------------
# 🧠 Buyer Ranking Function
# ------------------------------
def rank_buyers_for_sku(zone):
    today = datetime.today().date()

    def score(buyer):
        distance_score = -buyer["distance_km"] * 2
        engagement = buyer["engagement_score"] * 3
        last_engaged_days = (today - datetime.strptime(buyer["last_engaged"], "%Y-%m-%d").date()).days
        recency_score = max(0, 10 - last_engaged_days) * 1.5
        channel_bonus = {"WhatsApp": 5, "Email": 3, "SMS": 2, "Slack": 1}
        return distance_score + engagement + recency_score + channel_bonus.get(buyer["channel"], 0)

    zone_buyers = [b for b in buyer_profiles if b["zone"] == zone]
    return sorted(zone_buyers, key=score, reverse=True)

# ------------------------------
# 🎯 Dynamic Discount Logic
# ------------------------------
def get_discount_rate(days_to_expiry):
    if days_to_expiry <= 1:
        return 0.50
    elif days_to_expiry == 2:
        return 0.40
    elif days_to_expiry == 3:
        return 0.30
    elif days_to_expiry <= 5:
        return 0.20
    else:
        return 0.10

# ------------------------------
# 🚀 Core Redistribution Agent
# ------------------------------
def run_redistribution(inventory_path):
    random.seed(42)
    df = pd.read_csv(inventory_path, parse_dates=['expiry_date'])
    today = pd.to_datetime(datetime.today().date())
    threshold = today + timedelta(days=2)

    expiring_items = df[df['expiry_date'] <= threshold].copy()
    results = []
    total_stock_saved = 0

    for _, row in expiring_items.iterrows():
        days_left = (row['expiry_date'] - today).days
        discount_rate = get_discount_rate(days_left)

        original_price = random.randint(30, 100)
        new_price = round(original_price * (1 - discount_rate), 2)
        zone = row['location']

        top_buyers = rank_buyers_for_sku(zone)
        best_buyer = top_buyers[0] if top_buyers else None

        results.append({
            'sku_id': row['sku_id'],
            'product': row['product_name'],
            'expiry': row['expiry_date'].date(),
            'zone': zone,
            'buyer': best_buyer["name"] if best_buyer else "None",
            'channel': best_buyer["channel"] if best_buyer else "None",
            'old_price': f"₹{original_price}",
            'new_price': f"₹{new_price}",
            'stock': row['stock'],
            'status': 'Pending'  # Will be updated after outreach
        })

    return pd.DataFrame(results), total_stock_saved

# ------------------------------
# 🔁 Retry Tracking
# ------------------------------
def update_retry_queue(sku_data):
    retry_queue.append(sku_data)

def get_retry_queue():
    return retry_queue

# ------------------------------
# 🔁 Retry Attempt Logic
# ------------------------------
def rerun_retry_logic():
    results = []
    new_queue = []
    total_stock_saved = 0

    for item in retry_queue:
        original_price = float(item['old_price'].replace("₹", ""))
        # Escalate discount
        discounted_price = round(original_price * 0.5, 2)  # Escalate to flat 50%
        top_buyers = rank_buyers_for_sku(item['zone'])[1:]  # Skip previously tried

        matched_buyer = top_buyers[0] if top_buyers else None
        if matched_buyer:
            item['buyer'] = matched_buyer['name']
            item['channel'] = matched_buyer['channel']
            item['new_price'] = f"₹{discounted_price}"
            item['status'] = '✅ Routed (Retry)'
            total_stock_saved += item['stock']
            results.append(item)
        else:
            item['status'] = '❌ Retry Failed'
            new_queue.append(item)

    retry_queue.clear()
    retry_queue.extend(new_queue)  # Retain unresolved ones

    return pd.DataFrame(results), total_stock_saved

# ------------------------------
# 📜 Legacy Agent Logs (For 🧠 Tab)
# ------------------------------
def run_expiry_agent(inventory_path):
    df = pd.read_csv(inventory_path, parse_dates=['expiry_date'])
    today = pd.to_datetime(datetime.today().date())
    threshold = today + timedelta(days=2)

    near_expiry = df[df['expiry_date'] <= threshold]

    logs = []
    for _, row in near_expiry.iterrows():
        log = f"[{datetime.now().strftime('%H:%M:%S')}] SKU {row['sku_id']} ({row['product_name']}) is expiring on {row['expiry_date'].date()} → Candidate for redistribution from {row['location']}"
        logs.append(log)

    return near_expiry, logs
