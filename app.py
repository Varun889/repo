import streamlit as st
import requests
import time
import pandas as pd

# Setup - must be first
st.set_page_config(layout="wide")
st.title("🔢 Live NSE Options OI Numbers")

# Session state to persist data
if 'oi_data' not in st.session_state:
    st.session_state.oi_data = {"Calls": 0, "Puts": 0, "PCR": 0}

# Improved NSE data fetcher
def fetch_live_data(symbol="NIFTY"):
    url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "en-US,en;q=0.9"
    }
    
    try:
        session = requests.Session()
        session.get("https://www.nseindia.com", headers=headers, timeout=5)
        data = session.get(url, headers=headers, timeout=10).json()
        
        calls = sum(item["CE"]["openInterest"] for item in data["records"]["data"] if "CE" in item)
        puts = sum(item["PE"]["openInterest"] for item in data["records"]["data"] if "PE" in item)
        return calls, puts, round(puts/max(1, calls), 2)
    except:
        return None

# UI Controls
col1, col2 = st.columns(2)
with col1:
    symbol = st.selectbox("Index", ["NIFTY", "BANKNIFTY"])
with col2:
    refresh_time = st.selectbox("Refresh (seconds)", [1, 2, 5], index=1)

# Display containers
call_placeholder = st.empty()
put_placeholder = st.empty()
pcr_placeholder = st.empty()

# Main update loop
while True:
    data = fetch_live_data(symbol)
    if data:
        calls, puts, pcr = data
        st.session_state.oi_data = {
            "Calls": calls,
            "Puts": puts,
            "PCR": pcr
        }
    
    # Update displays without redrawing everything
    with call_placeholder.container():
        st.metric(
            label="📈 Calls OI", 
            value=f"{st.session_state.oi_data['Calls']/100000:.1f} L", 
            delta_color="off"
        )
    
    with put_placeholder.container():
        st.metric(
            label="📉 Puts OI", 
            value=f"{st.session_state.oi_data['Puts']/100000:.1f} L", 
            delta_color="off"
        )
    
    with pcr_placeholder.container():
        st.metric(
            label="🧮 Put/Call Ratio", 
            value=st.session_state.oi_data['PCR'], 
            delta_color="off"
        )
    
    time.sleep(refresh_time)
