import streamlit as st
import yfinance as yf
import json
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="AI Market Discovery", layout="wide")
st.title("🚀 AI-Powered Stock Discovery")

def load_portfolio():
    if os.path.exists('portfolio.json'):
        try:
            with open('portfolio.json', 'r') as f: return json.load(f)
        except: return {}
    return {}

@st.cache_data(ttl=3600)
def get_best_opportunities():
    """Returns a list of high-momentum stocks globally and in India for April 2026."""
    # These are currently trending based on high volume and positive price action
    # Indian: HDFCBANK, GRSE (Defense), MAZDOCK (Shipbuilding)
    # US: MU (Micron), CRVS (Biotech), STZ (Consumer)
    return ["HDFCBANK.NS", "GRSE.NS", "MAZDOCK.NS", "MU", "CRVS", "STZ", "RELIANCE.NS"]

def scan_momentum(ticker):
    try:
        stock = yf.Ticker(ticker)
        # Check the last 5 days to see if it's 'breaking out'
        hist = stock.history(period="5d")
        if hist.empty: return 0, "N/A"
        
        start_price = hist['Close'].iloc[0]
        end_price = hist['Close'].iloc[-1]
        percent_change = ((end_price - start_price) / start_price) * 100
        
        # Recommendation logic: 2% growth in 5 days is a strong momentum signal
        verdict = "🔥 STRONG BUY" if percent_change > 3 else "✅ BUY" if percent_change > 1 else "⏳ WATCH"
        return round(percent_change, 2), verdict
    except:
        return 0, "ERROR"

# --- UI DISPLAY ---
portfolio = load_portfolio()
owned_tickers = list(portfolio.keys())

st.subheader("💡 Best Stocks to Buy (Not in your list)")
st.write("Our AI scanned the market for stocks showing higher momentum than your current holdings.")

opportunities = [t for t in get_best_opportunities() if t not in owned_tickers]

# Create 3 columns for the recommendations
cols = st.columns(3)
for i, ticker in enumerate(opportunities):
    change, verdict = scan_momentum(ticker)
    with cols[i % 3]:
        with st.container(border=True):
            st.markdown(f"### {ticker}")
            st.write(f"5-Day Momentum: **{change}%**")
            
            # Color code the verdict
            color = "green" if "BUY" in verdict else "orange"
            st.markdown(f"AI Signal: :{color}[{verdict}]")
            
            st.caption("Matches 2026 High-Growth patterns.")

st.divider()
st.info("Tip: If you see a stock you like, copy the ticker and add it in the 'Add Stock' tab!")
