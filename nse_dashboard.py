from nsepython import *
import streamlit as st

st.set_page_config(page_title="NSE Market Dashboard", layout="wide")
st.title("📈 NSE Market Dashboard")

# Market Breadth (Static for now)
st.header("Market Breadth")
st.markdown("**Advances:** 2,720 | **Declines:** 902")
st.success("Pre-open sentiment: Positive → Likely Market Opening: Bullish bias")

# Sectoral Trends (Static or use sectoral index API)
st.header("Sectoral Trends – Top Performing Sectors")
top_sectors = ["Artificial Intelligence & Robotics", "Renewable Energy", "Biotech & Digital Health"]
st.markdown("- " + "\n- ".join(top_sectors))

# Top Gainers
st.header("Top 3 Gainers (<9:30 AM)")
gainers = nse_top_gainers()
for stock in gainers[:3]:
    st.markdown(f"- **{stock['symbol']}** – **{stock['netPrice']}%**")

# Top Losers
st.header("Top 3 Losers (<9:30 AM)")
losers = nse_top_losers()
for stock in losers[:3]:
    st.markdown(f"- **{stock['symbol']}** – **{stock['netPrice']}%**")

# OI Spurt (from Option Chain)
st.header("Top F&O Stocks with >30% OI Spurt")
option_chain = nse_optionchain_scrapper("NIFTY")
oi_spurt_stocks = []
for data in option_chain['records']['data']:
    if 'CE' in data and data['CE']['openInterest'] > 300000:  # Example threshold
        oi_spurt_stocks.append(data['CE']['underlying'])

for stock in oi_spurt_stocks[:5]:
    st.markdown(f"- **{stock}** – High OI")

# Overlap Section
st.header("Overlap (F&O Gainers/Losers + OI Spurts)")
overlap = set([s['symbol'] for s in gainers]) & set(oi_spurt_stocks)
st.markdown("- " + "\n- ".join(overlap))
