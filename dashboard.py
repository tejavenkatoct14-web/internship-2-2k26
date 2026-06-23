import streamlit as st
import pandas as pd
import plotly.express as px
import requests

# Page Configuration
st.set_page_config(page_title="Stock Market Dashboard", layout="wide")
st.title("📈 Real-Time Stock Market Dashboard")

# Sidebar Configuration for User Inputs
st.sidebar.header("Dashboard Controls")
symbol = st.sidebar.text_input("Enter Stock Symbol", value="IBM").upper()
# Alpha Vantage offers a free API key for real-time stock fetching
api_key = st.sidebar.text_input("Alpha Vantage API Key", value="demo", type="password")

def fetch_stock_data(ticker, key):
    """Fetch live stock data using the Requests API."""
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={ticker}&interval=5min&apikey={key}'
    
    try:
        # 1. Requests API Execution
        response = requests.get(url)
        data = response.json()
        
        # Validate response
        if "Time Series (5min)" not in data:
            st.error("API Error: Limit reached or invalid API Key/Symbol.")
            return pd.DataFrame()
            
        time_series = data["Time Series (5min)"]
        
        # 2. Pandas Data Processing
        df = pd.DataFrame.from_dict(time_series, orient='index')
        df.index = pd.to_datetime(df.index)
        df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        df = df.astype(float)
        
        # Sort so newest data is first
        df = df.sort_index(ascending=False)
        return df
        
    except Exception as e:
        st.error(f"Failed to fetch data: {e}")
        return pd.DataFrame()

# Main Dashboard Execution
if st.sidebar.button("Fetch Live Data"):
    with st.spinner(f"Fetching real-time data for {symbol}..."):
        df = fetch_stock_data(symbol, api_key)
        
        if not df.empty:
            st.success("Data fetched successfully!")
            
            # Financial Indicators Calculation
            current_price = df['Close'].iloc[0]
            previous_price = df['Close'].iloc[1]
            price_change = current_price - previous_price
            pct_change = (price_change / previous_price) * 100
            
            # Top Row: KPI Metrics
            col1, col2, col3 = st.columns(3)
            col1.metric("Current Price", f"${current_price:.2f}", f"{pct_change:.2f}%")
            col2.metric("Intraday High", f"${df['High'].max():.2f}")
            col3.metric("Volume (Latest)", f"{int(df['Volume'].iloc[0]):,}")
            
            st.markdown("---")
            
            # 3. Plotly Visualization
            st.subheader(f"Price Trend: {symbol} (5-Min Intervals)")
            fig = px.line(
                df, 
                x=df.index, 
                y='Close', 
                labels={'index': 'Timestamp', 'Close': 'Closing Price (USD)'},
                template="plotly_dark"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Raw Data View
            with st.expander("View Raw Data (Pandas DataFrame)"):
                st.dataframe(df.head(20))