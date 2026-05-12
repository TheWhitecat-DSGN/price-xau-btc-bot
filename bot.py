import os
import logging
import requests
import json
from datetime import datetime, timezone, timedelta
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8511076929:AAFMJUMc1m4O2xylOa1H6RJeGkvt8M-x6s8")
CHAT_ID = os.environ.get("CHAT_ID", "1027083696")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyADKqHQirxtbdWZthPf_utgI1oX-oIDkwA")
TZ = timezone(timedelta(hours=7))

logging.basicConfig(level=logging.INFO)
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
    except:
        pass
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
    except:
        pass
    return None

def get_silver_price():
    try:
        r = requests.get(
            "https://query1.finance.yahoo.com/v8/finance/chart/SI=F?range=1d&interval=1m",
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
    except:
        pass
    return None

def analyze_with_gemini(gold_data, btc_data, analysis_type="gold"):
    if not GEMINI_API_KEY:
        return None
    
    if analysis_type == "gold":
        prompt = f"""You are a professional gold market analyst. Write a short analysis in Thai language.
Current XAUUSD price: ${gold_data['price']} ({gold_data['change']:+.2f}, {gold_data['change_pct']:+.2f}%)
Provide:
1. สรุปสภาพตลาดทองวันนี้ (1-2 ประโยค)
2. จุดสำคัญที่ต้องจับตา (Fed, USD, Geopolitics)
3. Support/Resistance สำคัญ
4. แนวโน้มระยะสั้น (ขึ้น/ลง/ไซด์เวย์)

Keep it under 300 chars. Use emoji. No markdown headers."""
    elif analysis_type == "btc":
        prompt = f"""You are a professional crypto analyst. Write a short analysis in Thai language.
Current BTC price: ${btc_data['price']:,.2f} ({btc_data['change_24h']:+.2f}%)
Provide:
1. สรุปสภาพตลาด BTC วันนี้ (1-2 ประโยค)
2. ปัจจัยสำคัญ (ETF flows, whale, regulation)
3. Support/Resistance สำคัญ
4. แนวโน้มระยะสั้น

Keep it under 300 chars. Use emoji. No markdown headers."""
    else:
        prompt = f"""You are a market analyst. Write a short combined analysis in Thai language.
Gold (XAUUSD): ${gold_data['price']} ({gold_data['change_pct']:+.2f}%)
Bitcoin: ${btc_data['price']:,.2f} ({btc_data['change_24h']:+.2f}%)
Provide:
1. สรุปตลาดวันนี้ (ทอง + BTC)
2. ปัจจัยสำคัญที่ต้องจับตา
3. ความเสี่ยงที่ต้องระวัง

Keep it under 400 chars. Use emoji. No markdown headers."""

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.7, "maxOutputTokens": 500}
        }
        r = requests.post(url, json=payload, timeout=30)
        if r.status_code == 200:
            text = r.json()["candidates"][0]["content"]["parts"][0]["text"]
            return text.strip()
    except Exception as e:
        logger.error(f"Gemini error: {e}")
    return None

def build_price_msg(analysis_type="all"):
    now = datetime.now(TZ)
    time_str = now.strftime("%d/%m/%Y %H:%M")

    gold = get_gold_price()
    btc = get_btc_price()

    msg = f"📊 ราคาตลาดวันนี้\n📅 {time_str} น.\n"
    msg += "━━━━━━━━━━━━━━━━━━\n\n"

    if gold and analysis_type in ("gold", "all"):
        emoji_g = "🟢" if gold["change"] >= 0 else "🔴"
        msg += f"🥇 ทองคำ (XAUUSD)\n"
        msg += f"   ${gold['price']:,.2f} / oz\n"
        msg += f"   {emoji_g} {gold['change']:+,.2f} ({gold['change_pct']:+,.2f}%)\n\n"

    if btc and analysis_type in ("btc", "all"):
        emoji_b = "🟢" if btc["change_24h"] >= 0 else "🔴"
        msg += f"🟠 Bitcoin (BTCUSD)\n"
        msg += f"   ${btc['price']:,.2f}\n"
        msg += f"   {emoji_b} {btc['change_24h']:+,.2f}% (24h)\n\n"

    msg += "━━━━━━━━━━━━━━━━━━\n"

    # Add Gemini analysis
    analysis = analyze_with_gemini(gold, btc, analysis_type)
    if analysis:
        msg += f"\n🔬 วิเคราะห์\n{analysis}\n\n"

    msg += "💡 /gold /btc /all /analyze"
    return msg

async def send_scheduled(context: ContextTypes.DEFAULT_TYPE):
    msg = build_price_msg("all")
    await context.bot.send_message(chat_id=CHAT_ID, text=msg)

async def cmd_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(build_price_msg("all"))

async def cmd_gold(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = build_price_msg("gold")
    await update.message.reply_text(msg)

async def cmd_btc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = build_price_msg("btc")
    await update.message.reply_text(msg)

async def cmd_analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Deep analysis with Gemini"""
    gold = get_gold_price()
    btc = get_btc_price()
    
    now = datetime.now(TZ).strftime("%d/%m/%Y %H:%M")
    msg = f"🔬 วิเคราะห์ละเอียด\n📅 {now} น.\n\n"
    
    analysis = analyze_with_gemini(gold, btc, "all")
    if analysis:
        msg += analysis
    else:
        msg += "❌ วิเคราะห์ไม่สำเร็จ (อาจไม่ได้ตั้ง GEMINI_API_KEY)"
    
    await update.message.reply_text(msg)

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 สวัสดี! Bot ราคาทองคำ + BTC\n\n"
        "📌 คำสั่ง:\n"
        "/all — ราคาทั้งหมด + วิเคราะห์\n"
        "/gold — ราคาทองคำ + วิเคราะห์\n"
        "/btc — ราคา BTC + วิเคราะห์\n"
        "/analyze — วิเคราะห์ละเอียด\n\n"
        "⏰ ส่งอัตโนมัติ 09:00 + 19:00 ทุกวัน"
    )

async def post_init(application):
    scheduler = AsyncIOScheduler(timezone="Asia/Bangkok")
    # Use bot object directly for scheduled messages
    async def scheduled_job():
        msg = build_price_msg("all")
        await application.bot.send_message(chat_id=CHAT_ID, text=msg)
    
    scheduler.add_job(scheduled_job, "cron", hour=9, minute=0)
    scheduler.add_job(scheduled_job, "cron", hour=19, minute=0)
    scheduler.start()
    logger.info("Scheduler: 09:00 + 19:00 Bangkok time")

def main():
    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("all", cmd_all))
    app.add_handler(CommandHandler("gold", cmd_gold))
    app.add_handler(CommandHandler("cmd_btc", cmd_btc))
    app.add_handler(CommandHandler("btc", cmd_btc))
    app.add_handler(CommandHandler("analyze", cmd_analyze))

    logger.info("Bot starting...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
