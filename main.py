import requests
import time
import schedule
import pandas as pd
from telegram import Bot
import os
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
from datetime import datetime

bot = Bot(token=TELEGRAM_TOKEN)

def get_filtered_pump_candidates(threshold_percent=5):
    url = 'https://api.coingecko.com/api/v3/coins/markets'
    params = {
        'vs_currency': 'usd',
        'order': 'market_cap_desc',
        'per_page': 250,
        'page': 1,
        'price_change_percentage': '1h'
    }

    try:
        response = requests.get(url, params=params)
        coins = response.json()
    except Exception as e:
        print(f"❌ خطا در دریافت داده‌ها: {e}")
        return []

    strong_pumps = []
    for coin in coins:
        change = coin.get('price_change_percentage_1h_in_currency', 0)
        volume = coin.get('total_volume', 0)
        market_cap = coin.get('market_cap', 0)

        if change and change >= threshold_percent:
            if volume > 50_000_000 and market_cap > 10_000_000:
                volume_ratio = volume / market_cap
                if volume_ratio >= 0.5:
                    strong_pumps.append({
                        'name': coin['name'],
                        'symbol': coin['symbol'],
                        'change': change,
                        'price': coin['current_price'],
                        'volume': volume,
                        'market_cap': market_cap,
                        'volume_ratio': volume_ratio
                    })

    strong_pumps.sort(key=lambda x: x['change'], reverse=True)
    return strong_pumps[:3]

def save_to_csv(data):
    df = pd.DataFrame(data)
    df['timestamp'] = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    df.to_csv('pump_log.csv', mode='a', index=False, header=not pd.io.common.file_exists('pump_log.csv'))

def check_and_notify():
    print("📊 بررسی پامپ‌های دقیق‌تر...")
    candidates = get_filtered_pump_candidates()

    if candidates:
        for coin in candidates:
            msg = (
                f"🚀 *پامپ قدرتمند شناسایی شد!*\n"
                f"💰 {coin['name']} ({coin['symbol'].upper()})\n"
                f"📈 رشد ۱ ساعته: *{coin['change']:.2f}%*\n"
                f"💵 قیمت فعلی: ${coin['price']}\n"
                f"📊 حجم معاملات: ${coin['volume']:,}\n"
                f"🏦 مارکت کپ: ${coin['market_cap']:,}\n"
                f"📌 نسبت حجم به مارکت‌کپ: {coin['volume_ratio']:.2f}"
            )
            print(msg)
            bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode='Markdown')

        save_to_csv(candidates)
    else:
        print("⏳ پامپ قدرتمندی پیدا نشد.")

schedule.every(5).minutes.do(check_and_notify)

if __name__ == "__main__":
    print("📡 سیستم پیشرفته پایش پامپ فعال شد...")
    check_and_notify()
    while True:
        schedule.run_pending()
        time.sleep(1)
