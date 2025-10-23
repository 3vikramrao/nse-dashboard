import streamlit as st
import requests

st.set_page_config(page_title="NSE F&O Dashboard", layout="wide")
st.title("📈 NSE Derivatives (F&O) Dashboard")

# Headers to mimic browser
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Referer": "https://www.nseindia.com"
}

# Function to fetch F&O gainers
def fetch_fno_gainers():
    url = "https://www.nseindia.com/api/live-analysis-variations?index=fno_gainers"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            return response.json().get("data", [])[:5]
    except Exception as e:
        st.error(f"Error fetching F&O gainers: {e}")
    return []

# Function to fetch F&O losers
def fetch_fno_losers():
    url = "https://www.nseindia.com/api/live-analysis-variations?index=fno_losers"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            return response.json().get("data", [])[:5]
    except Exception as e:
        st.error(f"Error fetching F&O losers: {e}")
    return []

# Function to fetch option chain data
def fetch_option_chain(symbol="NIFTY"):
    url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"Error fetching option chain: {e}")
    return {}

# Detect OI spurts
def detect_oi_spurts(data, threshold=30):
    spurts = []
    for record in data.get("records", {}).get("data", []):
        for side in ["CE", "PE"]:
            if side in record:
                oi = record[side].get("openInterest", 0)
                prev_oi = record[side].get("previousOpenInterest", 0)
                if prev_oi > 0:
                    change = ((oi - prev_oi) / prev_oi) * 100
                    if change > threshold:
                        spurts.append({
                            "symbol": record[side].get("underlying", ""),
                            "strike": record[side].get("strikePrice", ""),
                            "side": side,
                            "change": round(change, 2)
                        })
    return spurts

# Display Market Breadth (static placeholder)
st.header("Market Breadth")
st.markdown("**Advances:** 2,720 | **Declines:** 902")
st.success("Pre-open sentiment: Positive → Likely Market Opening: Bullish bias")

# Display Top F&O Gainers
st.header("🔥 Top F&O Gainers")
gainers = fetch_fno_gainers()
if gainers:
    for stock in gainers:
        st.markdown(f"- **{stock['symbol']}** – **{stock['netPrice']}%**")
else:
    st.warning("No F&O gainers data available.")

# Display Top F&O Losers
st.header("🔻 Top F&O Losers")
losers = fetch_fno_losers()
if losers:
    for stock in losers:
        st.markdown(f"- **{stock['symbol']}** – **{stock['netPrice']}%**")
else:
    st.warning("No F&O losers data available.")

# Display OI Spurt Detection
st.header("📊 Option Chain OI Spurt Detection")
option_data = fetch_option_chain()
spurts = detect_oi_spurts(option_data)
if spurts:
    for spurt in spurts[:10]:
        st.markdown(f"- **{spurt['symbol']}** | Strike: {spurt['strike']} | Side: {spurt['side']} | OI Change: **{spurt['change']}%**")
else:
    st.info("No significant OI spurts detected above threshold.")
