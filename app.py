import streamlit as st
import requests
import time
import json
from datetime import datetime

# Setup
st.set_page_config(layout="wide")
st.title("📊 Live NSE Options OI")

# Initialize session state
if 'oi_data' not in st.session_state:
    st.session_state.oi_data = {
        "Calls": 0,
        "Puts": 0,
        "PCR": 0.0,
        "last_update": datetime.now().strftime("%H:%M:%S")
    }

# Silent data fetcher with better error handling
def fetch_oi_data(symbol="NIFTY"):
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
    refresh_rate = st.select_slider("Refresh (seconds)", options=[1, 2, 3, 5], value=2)

# Create containers for each metric
call_container = st.container()
put_container = st.container()
pcr_container = st.container()
update_container = st.container()

# Custom CSS for color bars
st.markdown("""
<style>
    .call-bar {
        background-color: #4CAF50;
        height: 20px;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    .put-bar {
        background-color: #F44336;
        height: 20px;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    .highlight {
        border: 2px solid #FFD700;
        padding: 5px;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Main app logic
while True:
    new_data = fetch_oi_data(symbol)
    if new_data:
        st.session_state.oi_data = {
            "Calls": new_data[0],
            "Puts": new_data[1],
            "PCR": new_data[2],
            "last_update": datetime.now().strftime("%H:%M:%S")
        }
    
    # Determine which OI is higher
    higher_oi = "Calls" if st.session_state.oi_data["Calls"] > st.session_state.oi_data["Puts"] else "Puts"
    
    # Update call display
    with call_container:
        col1, col2 = st.columns([1, 4])
        with col1:
            st.markdown("📈 **Calls OI**")
            st.markdown(f"`{st.session_state.oi_data['Calls']/100000:.1f} L`")
        with col2:
            bar_width = min(100, st.session_state.oi_data["Calls"]/max(1, st.session_state.oi_data["Puts"])*50)
            st.markdown(f'<div class="call-bar" style="width: {bar_width}%"></div>', unsafe_allow_html=True)
            if higher_oi == "Calls":
                st.markdown('<div class="highlight">Higher OI</div>', unsafe_allow_html=True)
    
    # Update put display
    with put_container:
        col1, col2 = st.columns([1, 4])
        with col1:
            st.markdown("📉 **Puts OI**")
            st.markdown(f"`{st.session_state.oi_data['Puts']/100000:.1f} L`")
        with col2:
            bar_width = min(100, st.session_state.oi_data["Puts"]/max(1, st.session_state.oi_data["Calls"])*50)
            st.markdown(f'<div class="put-bar" style="width: {bar_width}%"></div>', unsafe_allow_html=True)
            if higher_oi == "Puts":
                st.markdown('<div class="highlight">Higher OI</div>', unsafe_allow_html=True)
    
    # Update PCR
    with pcr_container:
        st.metric("🧮 Put/Call Ratio", st.session_state.oi_data["PCR"])
    
    # Show last update time
    with update_container:
        st.caption(f"Last update: {st.session_state.oi_data['last_update']} | Auto-refreshing every {refresh_rate} seconds")
    
    time.sleep(refresh_rate)
