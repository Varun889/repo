import streamlit as st
import pandas as pd
import requests
import time
import random
from bs4 import BeautifulSoup
import plotly.express as px

# Configure
st.set_page_config(layout="wide")
st.title("🚀 NSE Options OI Live Pro")

# User Inputs
symbol = st.selectbox("Select Index", ["NIFTY", "BANKNIFTY"])
expiry = st.selectbox("Expiry", ["Current Week", "Next Week"])

# Smart NSE Scraper (Avoids Blocks)
def get_nse_data():
    url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }
    
    try:
        # Rotate user agents & add delays
        time.sleep(random.uniform(0.5, 1.5))
        
        session = requests.Session()
        session.get("https://www.nseindia.com", headers=headers)  # Get cookies
        data = session.get(url, headers=headers).json()
        
        return data["records"]["data"]
    except Exception as e:
        st.error(f"⚠️ NSE Blocked Request. Retrying... {e}")
        time.sleep(5)
        return get_nse_data()  # Retry

# Process Data
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
    pcr = round(df["PE_OI"].sum() / df["CE_OI"].sum(), 2)
    return df, pcr

# Auto-Refresh UI
refresh_rate = st.slider("Update Speed (ms)", 500, 5000, 1000)
placeholder = st.empty()

while True:
    with placeholder.container():
        raw_data = get_nse_data()
        if raw_data:
            df, pcr = process_data(raw_data)
            
            # Live Metrics
            col1, col2, col3 = st.columns(3)
            col1.metric("📈 Calls OI", f"{df['CE_OI'].sum()/100000:.1f} L")
            col2.metric("📉 Puts OI", f"{df['PE_OI'].sum()/100000:.1f} L")
            col3.metric("🧮 PCR", pcr, delta=f"{pcr-1:.2f}")
            
            # Interactive Chart
            fig = px.bar(
                df, 
                x="Strike", 
                y=["CE_OI", "PE_OI"],
                title=f"{symbol} OI Distribution | PCR: {pcr}"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    time.sleep(refresh_rate/1000)  # Convert ms to seconds
