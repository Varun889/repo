import streamlit as st
import pandas as pd
import requests
import time
import plotly.express as px

# App configuration
st.set_page_config(layout="wide")
st.title("📊 NSE Options OI Live Pro")

# Session state for persistent data
if 'data' not in st.session_state:
    st.session_state.data = None

# Improved data fetcher with proper error handling
def get_nse_data(symbol):
    url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept-Encoding": "gzip, deflate",
        "Accept": "*/*"
    }
    
    try:
        # First get cookies
        session = requests.Session()
        session.get("https://www.nseindia.com", headers=headers, timeout=5)
        
        # Then get data
        response = session.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()["records"]["data"]
    except Exception as e:
        st.warning(f"Data refresh in progress... (Error: {str(e)[:50]})")
        time.sleep(3)
        return None

# Process data with safety checks
def process_data(raw_data):
    if not raw_data:
        return None, None
    
    oi_data = []
    for d in raw_data:
        if isinstance(d, dict) and "CE" in d and "PE" in d:
            oi_data.append({
                "Strike": d["strikePrice"],
                "Calls": d["CE"]["openInterest"],
                "Puts": d["PE"]["openInterest"]
            })
    
    if not oi_data:
        return None, None
        
    df = pd.DataFrame(oi_data)
    pcr = round(df["Puts"].sum() / max(1, df["Calls"].sum()), 2)
    return df, pcr

# UI Elements
symbol = st.selectbox("Select Index", ["NIFTY", "BANKNIFTY"])
refresh_rate = st.slider("Update Speed (seconds)", 1, 10, 3)

# Main app logic
placeholder = st.empty()

while True:
    with placeholder.container():
        # Get fresh data
        raw_data = get_nse_data(symbol)
        df, pcr = process_data(raw_data)
        
        if df is not None:
            # Metrics row
            col1, col2, col3 = st.columns(3)
            col1.metric("📈 Calls OI", f"{df['Calls'].sum()/100000:.1f} L")
            col2.metric("📉 Puts OI", f"{df['Puts'].sum()/100000:.1f} L")
            col3.metric("🧮 Put/Call Ratio", pcr)
            
            # Visual bar chart
            st.subheader("Call vs Put Open Interest")
            fig = px.bar(
                df.melt(id_vars="Strike"), 
                x="Strike", 
                y="value", 
                color="variable",
                barmode="group",
                color_discrete_map={"Calls": "red", "Puts": "green"}
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Waiting for market data...")
    
    time.sleep(refresh_rate)
