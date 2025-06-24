import streamlit as st
import pandas as pd
import requests
import time
import random

# Configure app
st.set_page_config(layout="wide")
st.title("🚀 NSE Options OI Live Pro")

# User inputs
symbol = st.selectbox("Select Index", ["NIFTY", "BANKNIFTY"])
refresh_rate = st.slider("Update Speed (ms)", 1000, 5000, 2000)

# Simplified data fetcher (no BeautifulSoup needed)
def get_nse_data():
    url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept-Language": "en-US,en;q=0.9",
    }
    
    try:
        session = requests.Session()
        session.get("https://www.nseindia.com", headers=headers, timeout=5)
        response = session.get(url, headers=headers, timeout=5)
        return response.json()["records"]["data"]
    except Exception as e:
        st.warning(f"Fetching fresh data... (Retry in 5s) | Error: {str(e)[:50]}")
        time.sleep(5)
        return get_nse_data()

# Process data
def process_data(raw_data):
    oi_data = []
    for d in raw_data:
        if d.get("CE") and d.get("PE"):
            oi_data.append({
                "Strike": d["strikePrice"],
                "CE_OI": d["CE"]["openInterest"],
                "PE_OI": d["PE"]["openInterest"]
            })
    df = pd.DataFrame(oi_data)
    pcr = round(df["PE_OI"].sum() / max(1, df["CE_OI"].sum()), 2)
    return df, pcr

# Main app
placeholder = st.empty()

while True:
    with placeholder.container():
        try:
            raw_data = get_nse_data()
            if raw_data:
                df, pcr = process_data(raw_data)
                
                # Display metrics
                col1, col2, col3 = st.columns(3)
                col1.metric("📈 Calls OI", f"{df['CE_OI'].sum()/100000:.1f} L")
                col2.metric("📉 Puts OI", f"{df['PE_OI'].sum()/100000:.1f} L")
                col3.metric("🧮 PCR", pcr)
                
                # Display chart
                st.bar_chart(df.set_index("Strike")[["CE_OI", "PE_OI"]])
                
        except Exception as e:
            st.error(f"Temporary error: {str(e)[:100]}")
    
    time.sleep(refresh_rate/1000)
