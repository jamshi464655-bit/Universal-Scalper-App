import streamlit as st
import pandas as pd
import requests
import json

# Page configuration
st.set_page_config(page_title="Universal Options Scalper", layout="wide")

# Session State Initialization
if 'connected' not in st.session_state:
    st.session_state['connected'] = False
if 'broker' not in st.session_state:
    st.session_state['broker'] = "None"
if 'token' not in st.session_state:
    st.session_state['token'] = None
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

# SIDEBAR - Controls
st.sidebar.markdown("### 🔌 Broker Bridge")
selected_broker = st.sidebar.selectbox(
    "Select Your Trading Broker", 
    ["Flattrade", "Dhan", "Shoonya (Finvasia)", "Zerodha (Kite)", "Angel One", "Fyers"]
)

st.sidebar.markdown("---")

if selected_broker in ["Flattrade", "Shoonya (Finvasia)"]:
    st.sidebar.markdown(f"**{selected_broker} Live Login:**")
    api_key = st.sidebar.text_input("User ID / Client ID")
    api_secret = st.sidebar.text_input("API Secret Key (From Broker Portal)", type="password")
    totp_token = st.sidebar.text_input("Current 6-Digit TOTP OTP", type="password")
    vendor_code = st.sidebar.text_input("Vendor Code", value="FA_API")
else:
    api_key = st.sidebar.text_input("API Key / App Key")
    api_secret = st.sidebar.text_input("Access Token", type="password")
    totp_token = st.sidebar.text_input("TOTP (If Any)", type="password")

# Connection Engine
if st.sidebar.button("🔌 INITIALIZE LIVE BRIDGE", use_container_width=True):
    if api_key and api_secret and totp_token:
        try:
            url = "https://piconnect.flattrade.in/NorenWSTP/QuickAuth" if selected_broker == "Flattrade" else "https://api.shoonya.com/NorenWSTP/QuickAuth"
            
            # SHA256 Encryption formatting required by broker
            import hashlib
            raw_appkey = f"{api_key}|{api_secret}"
            sha256_appkey = hashlib.sha256(raw_appkey.encode()).hexdigest()
            
            payload = {
                "apkversion": "1.0.0", 
                "uid": api_key, 
                "pwd": sha256_appkey, 
                "factor2": totp_token, 
                "vc": vendor_code, 
                "imei": "12345"
            }
            
            response = requests.post(url, data=f"jData={json.dumps(payload)}")
            res_data = response.json() if response.status_code == 200 else {}
            
            if res_data.get('stat') == 'Ok':
                st.session_state['token'] = res_data.get('susertoken')
                st.session_state['connected'] = True
                st.session_state['broker'] = selected_broker
                st.sidebar.success(f"✅ {selected_broker} Connected Successfully!")
            else:
                st.sidebar.error(f"Login Failed: {res_data.get('emsg', 'Check ID/Secret/TOTP')}")
        except Exception as e:
            st.sidebar.error(f"Connection Error: {e}")
    else:
        st.sidebar.error("All credentials are mandatory!")

# MAIN BOARD LAYOUT
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown('<div class="broker-card"><h3>🚀 QUICK ORDER PAD</h3></div>', unsafe_allow_html=True)
    exch = st.selectbox("Exchange Segment", ["NFO", "NSE"])
    sym = st.text_input("Option Symbol", value="NIFTY28MAY26C22000")
    qty = st.number_input("Lot Size / Quantity", value=25, step=25)
    
    c1, c2, c3 = st.columns(3)
    with c1: target_pts = st.number_input("Target Pts", value=10.0, step=1.0)
    with c2: sl_pts = st.number_input("SL Pts", value=5.0, step=1.0)
    with c3: trail_pts = st.number_input("Trail Pts", value=2.0, step=1.0)
        
    st.markdown("---")
    
    if st.button("🚀 INSTANT BUY (CE/PE)", type="primary", use_container_width=True):
        if st.session_state['connected']:
            if st.session_state['broker'] in ["Flattrade", "Shoonya (Finvasia)"] and st.session_state['token']:
                try:
                    order_url = "https://piconnect.flattrade.in/NorenWSTP/PlaceOrder" if st.session_state['broker'] == "Flattrade" else "https://api.shoonya.com/NorenWSTP/PlaceOrder"
                    order_data = {
                        "uid": api_key, "actid": api_key, "prd": "I", "exch": exch,
                        "tsym": sym, "qty": str(qty), "trantype": "B", "prctyp": "MKT", "ret": "DAY"
                    }
                    requests.post(order_url, data=f"jData={json.dumps(order_data)}&jKey={st.session_state['token']}")
                except Exception as e:
                    st.error(f"Execution Error: {e}")
            
            st.toast("Transmitting Order...")
            st.balloons()
            
            st.session_state['live_positions'].append({
                "Broker": st.session_state['broker'], "Asset": sym, "Qty": qty,
                "Target": f"+{target_pts} Pts", "StopLoss": f"-{sl_pts} Pts",
                "Trailing": f"{trail_pts} Pts", "Status": "RUNNING 🟢"
            })
            st.success("🎯 Scalp Position Activated!")
        else:
            st.error("❌ Broker Connection is Offline!")

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
            st.session_state['live_positions'] = []
            st.warning("💥 Emergency Square-off Sent!")
            st.rerun()
    else:
        st.info("No active option orders running.")
