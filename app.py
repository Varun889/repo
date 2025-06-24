import streamlit as st
import requests
import time
import json

# Setup - must be first
st.set_page_config(layout="wide")
st.title("🔢 Live NSE Options OI")

# Initialize session state
if 'data' not in st.session_state:
    st.session_state.data = {
        "Calls": 0,
        "Puts": 0,
        "PCR": 0.0
    }

# Silent data fetcher
def get_oi_data(symbol="NIFTY"):
    url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Encoding": "gzip, deflate"
    }
    
    try:
        session = requests.Session()
        session.get("https://www.nseindia.com", headers=headers, timeout=3)
        response = session.get(url, headers=headers, timeout=5)
        data = json.loads(response.text)
        
        calls = sum(item["CE"]["openInterest"] for item in data["records"]["data"] if "CE" in item)
        puts = sum(item["PE"]["openInterest"] for item in data["records"]["data"] if "PE" in item)
        return calls, puts, round(puts/max(1, calls), 2)
    except:
        return None

# UI Controls
col1, col2 = st.columns(2)
with col1:
    symbol = st.selectbox("Select Index", ["NIFTY", "BANKNIFTY"])
with col2:
    refresh_rate = st.select_slider("Refresh (seconds)", options=[1, 2, 3, 5, 10], value=2)

# Create placeholders
call_ph = st.empty()
put_ph = st.empty()
pcr_ph = st.empty()

# Main update loop
while True:
    new_data = get_oi_data(symbol)
    if new_data:
        st.session_state.data["Calls"], st.session_state.data["Puts"], st.session_state.data["PCR"] = new_data
    
    # Update displays silently
    with call_ph:
        st.metric(
            "📈 Calls OI", 
            f"{st.session_state.data['Calls']/100000:.1f} L",
            delta=None,
            label_visibility="visible"
        )
    
    with put_ph:
        st.metric(
            "📉 Puts OI", 
            f"{st.session_state.data['Puts']/100000:.1f} L",
            delta=None,
            label_visibility="visible"
        )
    
    with pcr_ph:
        st.metric(
            "🧮 PCR", 
            st.session_state.data['PCR'],
            delta=None,
            label_visibility="visible"
        )
    
    time.sleep(refresh_rate)
