import streamlit as st
import requests

# Set page config
st.set_page_config(page_title="NSE F&O Dashboard", layout="wide")
st.title("📈 NSE F&O Market Dashboard")

# NSE headers to avoid 403 errors
headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Referer": "https://www.nseindia.com"
}

# Function to fetch F&O gainers
def get_fno_gainers():
    url = "https://www.nseindia.com/api/live-analysis-variations?index=fno_gainers"
    session = requests.Session()
    session.get("https://www.nseindia.com", headers=headers)
    response = session.get(url, headers=headers)
    return response.json()['data'][:5]

# Function to fetch F&O losers
def get_fno_losers():
    url = "https://www.nseindia.com/api/live-analysis-variations?index=fno_losers"
    session = requests.Session()
    session.get("https://www.nseindia.com", headers=headers)
    response = session.get(url, headers=headers)
    return response.json()['data'][:5]

# Function to fetch option chain data
def fetch_option_chain(symbol="NIFTY"):
    url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
    session = requests.Session()
    session.get("https://www.nseindia.com", headers=headers)
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

# Top F&O Gainers
st.header("🔥 Top F&O Gainers")
try:
    gainers = get_fno_gainers()
    for stock in gainers:
        st.markdown(f"- **{stock['symbol']}** – **{stock['netPrice']}%**")
except Exception as e:
    st.error(f"Failed to fetch F&O gainers: {e}")

# Top F&O Losers
st.header("🔻 Top F&O Losers")
try:
    losers = get_fno_losers()
    for stock in losers:
        st.markdown(f"- **{stock['symbol']}** – **{stock['netPrice']}%**")
except Exception as e:
    st.error(f"Failed to fetch F&O losers: {e}")

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
