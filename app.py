# Step 1: Streamlit Crypto Dashboard App (Setup)

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import cryptocompare
import numpy as np

st.set_page_config(page_title="Crypto Trend Dashboard", layout="wide")
st.title("📈 Crypto Trend Dashboard with Technical Indicators")

# --- Sidebar Inputs ---
coins = ['BTC', 'ETH', 'BNB', 'SOL']
selected_coin = st.sidebar.selectbox("Select a Coin", coins)
days = st.sidebar.slider("Number of Past Days", min_value=30, max_value=365, value=90)

# --- Fetch Historical Data ---
data = cryptocompare.get_historical_price_day(selected_coin, currency='USD', limit=days)
df = pd.DataFrame(data)
df['time'] = pd.to_datetime(df['time'], unit='s')
df.set_index('time', inplace=True)

# --- Calculate Indicators ---
df['SMA_20'] = df['close'].rolling(window=20).mean()
df['EMA_20'] = df['close'].ewm(span=20, adjust=False).mean()
rolling_std = df['close'].rolling(window=20).std()
df['Upper_Band'] = df['SMA_20'] + (2 * rolling_std)
df['Lower_Band'] = df['SMA_20'] - (2 * rolling_std)

delta = df['close'].diff()
gain = delta.where(delta > 0, 0)
loss = -delta.where(delta < 0, 0)
avg_gain = gain.rolling(window=14).mean()
avg_loss = loss.rolling(window=14).mean()
rs = avg_gain / avg_loss
df['RSI'] = 100 - (100 / (1 + rs))

# --- Plotting ---
st.subheader(f"Price and Indicators for {selected_coin}")

fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 10))

# Plot 1: Price + SMA/EMA + Bollinger Bands
ax1.plot(df['close'], label='Close', color='blue')
ax1.plot(df['SMA_20'], label='SMA 20', color='green')
ax1.plot(df['EMA_20'], label='EMA 20', color='orange')
ax1.fill_between(df.index, df['Lower_Band'], df['Upper_Band'], color='gray', alpha=0.2)
ax1.set_title(f"{selected_coin} Price with SMA, EMA & Bollinger Bands")
ax1.legend()

# Plot 2: RSI
ax2.plot(df['RSI'], label='RSI', color='purple')
ax2.axhline(70, linestyle='--', color='red', label='Overbought')
ax2.axhline(30, linestyle='--', color='green', label='Oversold')
ax2.set_title("RSI Indicator")
ax2.legend()

# Plot 3: Volume
ax3.bar(df.index, df['volumefrom'], color='skyblue')
ax3.set_title("Daily Trading Volume")

plt.tight_layout()
st.pyplot(fig)

st.markdown("---")
st.download_button(
    label="📥 Download Data as CSV",
    data=df.to_csv().encode('utf-8'),
    file_name=f"{selected_coin}_crypto_data.csv",
    mime='text/csv'
)

st.markdown("---")
st.markdown("Built with ❤️ using Python, Streamlit & CryptoCompare API")
