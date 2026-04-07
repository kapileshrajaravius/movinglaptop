import streamlit as st
import yfinance as yf
import json
import os
import pandas as pd

# --- PAGE CONFIG ---
st.set_page_config(page_title="AI Portfolio Tracker", layout="wide")
st.title("📊 My AI Portfolio Dashboard")

# --- DATA HELPERS ---
def load_data():
    # Looks for the portfolio.json file in your project folder
    if os.path.exists('portfolio.json'):
        try:
            with open('portfolio.json', 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def get_ai_signal(ticker, pl_percent):
    """Smarter AI logic based on personal Profit/Loss and Market Momentum."""
    try:
        # 1. PRIORITY: Personal Wealth Protection
        if pl_percent > 100:
            return "💰 TAKE PROFIT"
        if pl_percent < -30:
            return "⚠️ CUT LOSS"
            
        # 2. SECONDARY: Market Trend (20-day Moving Average)
        stock = yf.Ticker(ticker)
        hist = stock.history(period="30d")
        if hist.empty: 
            return "🟨 HOLD"
        
        current_price = hist['Close'].iloc[-1]
        avg_20 = hist['Close'].mean()
        
        if current_price > avg_20 * 1.05:
            return "🟩 BUY"
        elif current_price < avg_20 * 0.95:
            return "🟥 SELL"
        else:
            return "🟨 HOLD"
    except:
        return "⚠️ ERROR"

# --- MAIN DASHBOARD LOGIC ---
portfolio = load_data()

if not portfolio:
    st.info("Your portfolio is empty. Use the 'Add Stocks' page to add your first stock!")
else:
    table_data = []
    
    with st.spinner('Updating live prices and AI signals...'):
        for ticker, info in portfolio.items():
            try:
                # Fetching live data
                stock = yf.Ticker(ticker)
                price_now = stock.fast_info['last_price']
                
                # Portfolio Values
                buy_price = info.get('buy_price', 0)
                shares = info.get('shares', 0)
                
                # Math
                total_cost = buy_price * shares
                current_value = price_now * shares
                pl_money = current_value - total_cost
                pl_percent = (pl_money / total_cost * 100) if total_cost != 0 else 0
                
                # Get Signal
                ai_verdict = get_ai_signal(ticker, pl_percent)
                
                # Currency formatting based on ticker
                cur = "₹" if (".NS" in ticker or ".BO" in ticker) else "$"
                
                table_data.append({
                    "Stock": ticker,
                    "Shares": shares,
                    "AI RECOMMENDATION": ai_verdict,
                    "Price Bought": f"{cur}{buy_price:,.2f}",
                    "Price Now": f"{cur}{price_now:,.2f}",
                    "Profit/Loss": f"{cur}{pl_money:,.2f}",
                    "P/L (%)": f"{pl_percent:,.2f}%"
                })
            except:
                continue

    # Display the Table
    if table_data:
        df = pd.DataFrame(table_data)
        st.table(df)
    else:
        st.error("Failed to load market data. Check your internet connection.")

st.divider()
st.caption("🚀 AI Rule: Suggests 'Take Profit' at +100% and 'Cut Loss' at -30%.")
