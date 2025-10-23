import streamlit as st
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="NSE F&O Dashboard", layout="wide")
st.title("📈 NSE F&O Market Dashboard")

# Headers to mimic browser
headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "text/html",
    "Referer": "https://www.nseindia.com"
}

session = requests.Session()
session.get("https://www.nseindia.com", headers=headers)

# Function to scrape F&O gainers and losers
def fetch_fno_gainers_losers():
    url = "https://www.nseindia.com/live_market/dynaContent/live_watch/stock_watch/mostActiveStock.jsp?flag=F"
    response = session.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find("table", {"id": "dataTable"})
    rows = table.find_all("tr")[1:]  # Skip header

    gainers = []
    losers = []

    for row in rows:
        cols = row.find_all("td")
        symbol = cols[0].text.strip()
        change = float(cols[4].text.strip())
        if change > 0:
            gainers.append((symbol, change))
        elif change < 0:
            losers.append((symbol, change))

    gainers = sorted(gainers, key=lambda x: x[1], reverse=True)[:5]
    losers = sorted(losers, key=lambda x: x[1])[:5]
    return gainers, losers

# Function to fetch option chain data
def fetch_option_chain(symbol="NIFTY"):
    url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
    response = session.get(url, headers=headers)
    return response.json()

# Detect OI spurts
def detect_oi_spurts(data, threshold=30):
    oi_spurts = []
    for record in data['records']['data']:
        for side in ['CE', 'PE']:
            if side in record:
                oi = record[side].get('openInterest', 0)
                prev_oi = record[side].get('previousOpenInterest', 0)
                if prev_oi > 0:
                    change = ((oi - prev_oi) / prev_oi) * 100
                    if change > threshold:
                        oi_spurts.append({
                            'symbol': record[side]['underlying'],
                            'strike': record[side]['strikePrice'],
                            'change': round(change, 2),
                            'side': side
                        })
    return oi_spurts

# Market Breadth (static placeholder)
st.header("Market Breadth")
st.markdown("**Advances:** 2,720 | **Declines:** 902")
st.success("Pre-open sentiment: Positive → Likely Market Opening: Bullish bias")

# F&O Gainers and Losers
st.header("🔥 Top F&O Gainers & 🔻 Losers")
try:
    gainers, losers = fetch_fno_gainers_losers()
    st.subheader("Top Gainers")
    for symbol, change in gainers:
        st.markdown(f"- **{symbol}** – **+{change}%**")
    st.subheader("Top Losers")
    for symbol, change in losers:
        st.markdown(f"- **{symbol}** – **{change}%**")
except Exception as e:
    st.error(f"Failed to fetch F&O gainers/losers: {e}")

# OI Spurt Detection
st.header("📊 Option Chain OI Spurt Detection")
try:
    option_data = fetch_option_chain()
    spurts = detect_oi_spurts(option_data)
    if spurts:
        for spurt in spurts[:10]:
            st.markdown(f"- **{spurt['symbol']}** | Strike: {spurt['strike']} | Side: {spurt['side']} | OI Change: **{spurt['change']}%**")
    else:
        st.info("No significant OI spurts detected above threshold.")
except Exception as e:
    st.error(f"Failed to fetch option chain data: {e}")
