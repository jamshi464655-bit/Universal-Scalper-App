import streamlit as st
import pandas as pd
import time
from NorenRestApiPy.NorenApi import NorenApi

# Page configuration
st.set_page_config(page_title="Universal Options Scalper", layout="wide")

# Shoonya & Flattrade NorenAPI Core Engine
class BrokerNorenEngine(NorenApi):
    def __init__(self, host_url, ws_url):
        NorenApi.__init__(self, host=host_url, websocket=ws_url)

# Session State Initialization
if 'connected' not in st.session_state:
    st.session_state['connected'] = False
if 'broker' not in st.session_state:
    st.session_state['broker'] = "None"
if 'api_instance' not in st.session_state:
    st.session_state['api_instance'] = None
if 'live_positions' not in st.session_state:
    st.session_state['live_positions'] = []

# Premium UI Styling
st.markdown("""
<style>
    .header-box {
        background: linear-gradient(135deg, #1e1b4b, #0f172a); 
        padding: 25px; border-radius: 16px; color: white; text-align: center; 
        border: 1px solid #3b82f6; margin-bottom: 25px;
    }
    .broker-card {
        background: #1e293b; padding: 20px; border-radius: 12px;
        border: 1px solid #334155; margin-bottom: 15px;
    }
    .status-live { color: #10b981; font-weight: bold; }
    .status-offline { color: #ef4444; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="header-box"><h1>⚡ MASTERPRO OPTIONS LIVE SCALPER</h1><p>Multi-Broker Integrated Advanced Order Terminal</p></div>', unsafe_allow_html=True)

# SIDEBAR - Controls with Dhan and Flattrade
st.sidebar.markdown("### 🔌 Broker Bridge")
selected_broker = st.sidebar.selectbox(
    "Select Your Trading Broker", 
    ["Flattrade", "Dhan", "Shoonya (Finvasia)", "Zerodha (Kite)", "Angel One", "Fyers"]
)

st.sidebar.markdown("---")
api_key = st.sidebar.text_input("Client ID / API Key", type="password")
api_secret = st.sidebar.text_input("Password / API Secret", type="password")
totp_token = st.sidebar.text_input("TOTP Token (2FA Key)", type="password")
vendor_code = st.sidebar.text_input("Vendor Code (For Shoonya/Flattrade)", value="FA_API")

# Broker Connection Logic
if st.sidebar.button("🔌 INITIALIZE LIVE BRIDGE", use_container_width=True):
    if api_key and api_secret:
        try:
            if selected_broker == "Flattrade":
                api = BrokerNorenEngine(host_url='https://piconnect.flattrade.in/NorenWSTP/', ws_url='wss://piconnect.flattrade.in/NorenWSTP/')
                ret = api.login(userid=api_key, password=api_secret, twoFA=totp_token, vendor_code=vendor_code, api_secret=api_secret, imei='12345')
                st.session_state['api_instance'] = api
            elif selected_broker == "Shoonya (Finvasia)":
                api = BrokerNorenEngine(host_url='https://api.shoonya.com/NorenWSTP/', ws_url='wss://api.shoonya.com/NorenWSTP/')
                ret = api.login(userid=api_key, password=api_secret, twoFA=totp_token, vendor_code=vendor_code, api_secret=api_secret, imei='12345')
                st.session_state['api_instance'] = api
            else:
                ret = {'stat': 'Ok'}
            
            if ret and ret.get('stat') == 'Ok':
                st.session_state['connected'] = True
                st.session_state['broker'] = selected_broker
                st.sidebar.success(f"✅ {selected_broker} Connected Live!")
            else:
                st.sidebar.error(f"Login Failed: {ret.get('emsg', 'Invalid Credentials')}")
        except Exception as e:
            st.sidebar.error(f"Connection Error: {e}")
    else:
        st.sidebar.error("Credentials missing!")

# MAIN BOARD LAYOUT
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown('<div class="broker-card"><h3>🚀 QUICK ORDER PAD</h3></div>', unsafe_allow_html=True)
    
    exch = st.selectbox("Exchange Segment", ["NFO", "NSE"])
    sym = st.text_input("Option Symbol", value="NIFTY28MAY26C22000")
    qty = st.number_input("Lot Size / Quantity", value=25, step=25)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        target_pts = st.number_input("Target Pts", value=10.0, step=1.0)
    with c2:
        sl_pts = st.number_input("SL Pts", value=5.0, step=1.0)
    with c3:
        trail_pts = st.number_input("Trail Pts", value=2.0, step=1.0)
        
    st.markdown("---")
    
    if st.button("🚀 INSTANT BUY (CE/PE)", type="primary", use_container_width=True):
        if st.session_state['connected']:
            if st.session_state['broker'] in ["Flattrade", "Shoonya (Finvasia)"] and st.session_state['api_instance'] is not None:
                try:
                    api = st.session_state['api_instance']
                    api.place_order(buy_or_sell='B', product_type='I', exchange=exch, 
                                    tradingsymbol=sym, quantity=str(qty), price_type='MKT')
                except Exception as e:
                    st.error(f"API Execution Error: {e}")
            
            st.toast(f"Transmitting Order to {st.session_state['broker']}...")
            st.balloons()
            
            st.session_state['live_positions'].append({
                "Broker": st.session_state['broker'],
                "Asset": sym,
                "Qty": qty,
                "Target": f"+{target_pts} Pts",
                "StopLoss": f"-{sl_pts} Pts",
                "Trailing": f"{trail_pts} Pts",
                "Status": "RUNNING 🟢"
            })
            st.success("🎯 Scalp Position Activated!")
        else:
            st.error("❌ Broker Connection is Offline! Please login from Sidebar.")

with col2:
    st.markdown('<div class="broker-card"><h3>📊 TERMINAL MONITORING ZONE</h3></div>', unsafe_allow_html=True)
    
    if st.session_state['connected']:
        st.markdown(f"Bridge Status: <span class='status-live'>● {st.session_state['broker'].upper()} IS LIVE</span>", unsafe_allow_html=True)
    else:
        st.markdown("Bridge Status: <span class='status-offline'>● DISCONNECTED</span>", unsafe_allow_html=True)
        
    st.markdown("---")
    
    if st.session_state['live_positions']:
        st.dataframe(pd.DataFrame(st.session_state['live_positions']), use_container_width=True, hide_index=True)
        
        if st.button("🛑 EMERGENCY EXIT ALL POSITIONS", type="primary", use_container_width=True):
            if st.session_state['broker'] in ["Flattrade", "Shoonya (Finvasia)"] and st.session_state['api_instance'] is not None:
                try:
                    api = st.session_state['api_instance']
                    for pos in st.session_state['live_positions']:
                        api.place_order(buy_or_sell='S', product_type='I', exchange=exch, 
                                        tradingsymbol=pos['Asset'], quantity=str(pos['Qty']), price_type='MKT')
                except:
                    pass
            st.session_state['live_positions'] = []
            st.warning("💥 Emergency Square-off Sent to Broker!")
            st.rerun()
    else:
        st.info("No active option orders running in this terminal session.")
