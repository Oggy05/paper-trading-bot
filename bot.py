import yfinance as yf
from datetime import datetime, time as dtime
import pytz
import os
import sys

# =====================
# CONFIG
# =====================
SYMBOL = "AAPL"          # US stock (AAPL, MSFT, NVDA)
TARGET_PCT = 0.0075      # 0.75%
STOP_PCT = 0.005         # 0.5%
LOG_FILE = "trade_log.txt"
STATE_FILE = "state.txt"

et = pytz.timezone("US/Eastern")

# =====================
# MARKET HOURS (US)
# =====================
def market_is_open():
    now = datetime.now(et).time()
    return dtime(9, 30) <= now <= dtime(16, 0)

def log(msg):
    with open(LOG_FILE, "a") as f:
        f.write(msg + "\n")

def save_entry(price):
    with open(STATE_FILE, "w") as f:
        f.write(str(price))

def load_entry():
    if not os.path.exists(STATE_FILE):
        return None
    with open(STATE_FILE, "r") as f:
        return float(f.read())

# =====================
# SKIP IF MARKET CLOSED
# =====================
if not market_is_open():
    sys.exit()

# =====================
# FETCH PRICE
# =====================
data = yf.Ticker(SYMBOL).history(period="1d", interval="1m")
if data.empty:
    sys.exit()

price = float(data["Close"].iloc[-1])
now = datetime.now(et).strftime("%Y-%m-%d %H:%M:%S ET")

entry = load_entry()

# =====================
# ENTRY
# =====================
if entry is None:
    save_entry(price)
    log(f"[{now}] BUY @ {price:.2f}")
    sys.exit()

# =====================
# MONITOR
# =====================
target = entry * (1 + TARGET_PCT)
stop = entry * (1 - STOP_PCT)
pnl = (price - entry) / entry * 100

log(f"[{now}] Price: {price:.2f} | P&L: {pnl:.2f}%")

# =====================
# EXIT
# =====================
if price >= target:
    log(f"[{now}] TARGET HIT @ {price:.2f}")
    os.remove(STATE_FILE)
    sys.exit()

if price <= stop:
    log(f"[{now}] STOP LOSS HIT @ {price:.2f}")
    os.remove(STATE_FILE)
    sys.exit()
