import streamlit as st
import requests

# NSE headers to avoid 403 errors
headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Referer": "https://www.nseindia.com"
}

# Function to fetch top gainers
def get_top_gainers():
    url = "https://www.nseindia.com/api/live-analysis-variations?index=gainers"
    response = requests.get(url, headers=headers)
    data = response.json()
    return data['data'][:3]

# Function to fetch top losers
def get_top_losers():
    url = "https://www.nseindia.com/api/live-analysis-variations?index=losers"
    response = requests.get(url, headers=headers)
    data = response.json()
    return data['data'][:3]

# Streamlit UI
st.set_page_config(page_title="NSE Market Dashboard", layout="wide")
st.title("📈 NSE Market Dashboard")

st.header("Top 3 Gainers (<9:30 AM)")
try:
    gainers = get_top_gainers()
    for stock in gainers:
        st.markdown(f"- **{stock['symbol']}** – **{stock['netPrice']}%**")
except Exception as e:
    st.error(f"Failed to fetch gainers: {e}")

st.header("Top 3 Losers (<9:30 AM)")
try:
    losers = get_top_losers()
    for stock in losers:
        st.markdown(f"- **{stock['symbol']}** – **{stock['netPrice']}%**")
except Exception as e:
    st.error(f"Failed to fetch losers: {e}")
