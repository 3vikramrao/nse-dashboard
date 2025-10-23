import streamlit as st
import requests

# Headers to avoid 403 errors
headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Referer": "https://www.nseindia.com"
}

# Function to fetch option chain data
def fetch_option_chain(symbol="NIFTY"):
    url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
    session = requests.Session()
    session.get("https://www.nseindia.com", headers=headers)  # Get cookies
    response = session.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Detect OI spurts
def detect_oi_spurts(data, threshold=30):
    oi_spurts = []
    for record in data['records']['data']:
        if 'CE' in record and 'PE' in record:
            ce = record['CE']
            pe = record['PE']
            if 'openInterest' in ce and 'previousOpenInterest' in ce:
                ce_change = ((ce['openInterest'] - ce['previousOpenInterest']) / ce['previousOpenInterest']) * 100
                if ce_change > threshold:
                    oi_spurts.append((ce['underlying'], ce['strikePrice'], round(ce_change, 2), 'CE'))
            if 'openInterest' in pe and 'previousOpenInterest' in pe:
                pe_change = ((pe['openInterest'] - pe['previousOpenInterest']) / pe['previousOpenInterest']) * 100
                if pe_change > threshold:
                    oi_spurts.append((pe['underlying'], pe['strikePrice'], round(pe_change, 2), 'PE'))
    return oi_spurts
# Streamlit UI
st.header("🔍 Option Chain OI Spurt Detection")
data = fetch_option_chain()
if data:
    spurts = detect_oi_spurts(data)
    if spurts:
        for scrip, strike, change, side in spurts[:10]:
            st.markdown(f"- **{scrip}** | Strike: {strike} | Side: {side} | OI Change: **{change}%**")
    else:
        st.info("No significant OI spurts detected above threshold.")
else:
    st.error("Failed to fetch option chain data.")
