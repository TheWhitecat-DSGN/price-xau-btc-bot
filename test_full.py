import sys
sys.path.insert(0, ".")
from bot import get_gold_price, get_btc_price, analyze_with_gemini, build_price_msg
import os

# Boss's Gemini API key
os.environ["GEMINI_API_KEY"] = "AIzaSyBFwHCU6D3GtS4F9aJ1R17PxDaPmT4lxAk"

print("=== Price ===")
gold = get_gold_price()
btc = get_btc_price()
print("Gold:", gold)
print("BTC:", btc)

print("\n=== Analysis ===")
analysis = analyze_with_gemini(gold, btc, "all")
print(analysis)

print("\n=== Full Message ===")
msg = build_price_msg("all")
print(msg)
