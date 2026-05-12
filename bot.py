import os
import logging
import requests
from datetime import datetime, timezone, timedelta
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
CHAT_ID = os.environ.get("CHAT_ID", "1027083696")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
TZ = timezone(timedelta(hours=7))

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
logger = logging.getLogger(__name__)

def get_gold_price():
    try:
        r = requests.get(
            "https://query1.finance.yahoo.com/v8/finance/chart/GC=F?range=1d&interval=1m",
            timeout=10, headers={"User-Agent": "Mozilla/5.0"}
        )
        if r.status_code == 200:
            data = r.json()
            result = data["chart"]["result"][0]
            price = result["meta"]["regularMarketPrice"]
            prev = result["meta"]["chartPreviousClose"]
            change = price - prev
            change_pct = (change / prev) * 100
            return {"price": round(price, 2), "change": round(change, 2), "change_pct": round(change_pct, 2)}
    except Exception as e:
        logger.error(f"Gold price error: {e}")
    return None

def get_btc_price():
    try:
        r = requests.get(
            "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_24hr_change=true",
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            btc = data["bitcoin"]
            return {"price": btc["usd"], "change_24h": round(btc.get("usd_24h_change", 0), 2)}
    except Exception as e:
        logger.error(f"BTC price error: {e}")
    return None

def get_analysis(gold_data, btc_data, analysis_type="all"):
    if not GEMINI_API_KEY:
        return None
    try:
        if analysis_type == "gold":
            prompt = f"วิเคราะห์ราคาทองคำ XAUUSD ตอนนี้ ${gold_data['price']:,.2f} ({gold_data['change_pct']:+.2f}%) ให้สั้นๆ ภาษาไทย: สรุปตลาด, จุดสำคัญ, support/resistance, แนวโน้ม ไม่เกิน 300 ตัวอักษร ใช้ emoji"
        elif analysis_type == "btc":
            prompt = f"วิเคราะห์ราคา Bitcoin ตอนนี้ ${btc_data['price']:,.2f} ({btc_data['change_24h']:+.2f}%) ให้สั้นๆ ภาษาไทย: สรุปตลาด, ปัจจัยสำคัญ, support/resistance, แนวโน้ม ไม่เกิน 300 ตัวอักษร ใช้ emoji"
        else:
            prompt = f"วิเคราะห์ตลาดให้สั้นๆ ภาษาไทย: ทอง ${gold_data['price']:,.2f} ({gold_data['change_pct']:+.2f}%), BTC ${btc_data['price']:,.2f} ({btc_data['change_24h']:+.2f}%). สรุปตลาด, จุดสำคัญ, แนวโน้ม ไม่เกิน 300 ตัวอักษร ใช้ emoji"

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"maxOutputTokens": 400}
        }
        r = requests.post(url, json=payload, timeout=30)
        if r.status_code == 200:
            return r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        else:
            logger.error(f"Gemini error: {r.status_code}")
    except Exception as e:
        logger.error(f"Analysis error: {e}")
    return None

def build_msg(analysis_type="all"):
    now = datetime.now(TZ).strftime("%d/%m/%Y %H:%M")
    gold = get_gold_price()
    btc = get_btc_price()

    msg = f"📊 ราคาตลาดวันนี้\n📅 {now} น.\n"
    msg += "━━━━━━━━━━━━━━━━━━\n\n"

    if gold and analysis_type in ("gold", "all"):
        e = "🟢" if gold["change"] >= 0 else "🔴"
        msg += f"🥇 ทองคำ (XAUUSD)\n   ${gold['price']:,.2f} / oz\n   {e} {gold['change']:+,.2f} ({gold['change_pct']:+,.2f}%)\n\n"

    if btc and analysis_type in ("btc", "all"):
        e = "🟢" if btc["change_24h"] >= 0 else "🔴"
        msg += f"🟠 Bitcoin (BTCUSD)\n   ${btc['price']:,.2f}\n   {e} {btc['change_24h']:+.2f}% (24h)\n\n"

    msg += "━━━━━━━━━━━━━━━━━━\n"

    analysis = get_analysis(gold, btc, analysis_type)
    if analysis:
        msg += f"\n🔬 วิเคราะห์\n{analysis}\n\n"

    msg += "💡 /gold /btc /all"
    return msg

async def send_scheduled(bot):
    try:
        msg = build_msg("all")
        await bot.send_message(chat_id=CHAT_ID, text=msg)
    except Exception as e:
        logger.error(f"Schedule error: {e}")

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 สวัสดี! Bot ราคาทองคำ + BTC\n\n"
        "📌 /all /gold /btc\n"
        "⏰ ส่งอัตโนมัติ 09:00 + 19:00"
    )

async def cmd_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(build_msg("all"))

async def cmd_gold(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(build_msg("gold"))

async def cmd_btc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(build_msg("btc"))

async def post_init(application):
    scheduler = AsyncIOScheduler(timezone="Asia/Bangkok")
    scheduler.add_job(send_scheduled, "cron", hour=9, minute=0, args=[application.bot])
    scheduler.add_job(send_scheduled, "cron", hour=19, minute=0, args=[application.bot])
    scheduler.start()
    logger.info("Bot ready! Schedule: 09:00 + 19:00 Bangkok")

def main():
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN not set!")
        return
    logger.info("Starting bot...")
    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("all", cmd_all))
    app.add_handler(CommandHandler("gold", cmd_gold))
    app.add_handler(CommandHandler("btc", cmd_btc))
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
