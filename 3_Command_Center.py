import streamlit as st
import yfinance as yf
import json
import os
import pandas as pd

st.set_page_config(page_title="AI Command Center", layout="wide")

def load_data():
    if os.path.exists('portfolio.json'):
        try:
            with open('portfolio.json', 'r') as f: return json.load(f)
        except: return {}
    return {}

def save_data(data):
    with open('portfolio.json', 'w') as f:
        json.dump(data, f, indent=4)

# --- AI BRAIN: UPDATED TO RECOGNIZE 'ADD' ---
def process_decision(user_input):
    portfolio = load_data()
    words = user_input.upper().split()
    ticker = words[-1].strip()
    
    # Recognizes "BUY" or "ADD"
    if any(cmd in words for cmd in ["BUY", "ADD"]):
        try:
            stock = yf.Ticker(ticker)
            live_price = stock.fast_info['last_price']
            cur = "₹" if (".NS" in ticker or ".BO" in ticker) else "$"

            # Value-based logic (e.g., "Add 100 USD")
            if any(x in words for x in ["USD", "INR", "RUPEES"]):
                nums = [float(w) for w in words if w.replace('.','',1).isdigit()]
                amount = nums[0]
                new_shares = amount / live_price
                new_cost = amount
            else:
                # Quantity-based logic (e.g., "Add 5 AAPL")
                nums = [float(w) for w in words if w.replace('.','',1).isdigit()]
                new_shares = nums[0]
                new_cost = new_shares * live_price

            # Position Averaging (No new rows)
            if ticker in portfolio:
                existing = portfolio[ticker]
                total_shares = existing['shares'] + new_shares
                total_cost = existing.get('total_cost', existing['shares'] * existing['buy_price']) + new_cost
                avg_price = total_cost / total_shares
                
                portfolio[ticker] = {
                    "buy_price": avg_price,
                    "shares": total_shares,
                    "total_cost": total_cost,
                    "target_3m": avg_price * 1.02
                }
                msg = f"✅ **Updated:** {ticker} total is now {total_shares:,.2f} shares (Avg: {cur}{avg_price:,.2f})."
            else:
                portfolio[ticker] = {
                    "buy_price": live_price, 
                    "shares": new_shares, 
                    "total_cost": new_cost,
                    "target_3m": live_price * 1.02
                }
                msg = f"✅ **New Position:** Added {new_shares:,.2f} shares of {ticker} at {cur}{live_price:,.2f}."
            
            save_data(portfolio)
            return msg
        except:
            return "❌ Use: 'Add 100 USD of NVDA' or 'Buy 5 NVDA'"

    elif any(cmd in words for cmd in ["REMOVE", "SELL"]):
        # ... (Previous Remove/Sell logic remains the same)
        try:
            if ticker not in portfolio: return f"❓ No {ticker} found."
            nums = [float(w) for w in words if w.replace('.','',1).isdigit()]
            val = nums[0] if nums else 0
            if any(x in words for x in ["USD", "INR", "RUPEES"]):
                shares_to_remove = val / yf.Ticker(ticker).fast_info['last_price']
            else:
                shares_to_remove = val

            if shares_to_remove >= portfolio[ticker]['shares']:
                del portfolio[ticker]
                msg = f"📤 **Closed:** {ticker} removed."
            else:
                portfolio[ticker]['shares'] -= shares_to_remove
                portfolio[ticker]['total_cost'] = portfolio[ticker]['shares'] * portfolio[ticker]['buy_price']
                msg = f"📉 **Reduced:** Removed {shares_to_remove:,.2f} shares of {ticker}."
            save_data(portfolio)
            return msg
        except: return "❌ Use: 'Remove 100 USD of AAPL'"
    
    return "🤖 Commands: 'Add [amt] [ticker]', 'Buy [qty] [ticker]', or 'Sell [ticker]'"

# --- UI LAYOUT ---
st.title("🎮 AI Investment Command Center")
chat_col, table_col = st.columns([1, 2])

with chat_col:
    st.subheader("💬 AI Decision Chat")
    if "messages" not in st.session_state: st.session_state.messages = []
    with st.container(border=True, height=400):
        for msg in st.session_state.messages:
            st.chat_message(msg["role"]).write(msg["content"])

    if prompt := st.chat_input("Ex: Add 100 USD of NVDA"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.messages.append({"role": "assistant", "content": process_decision(prompt)})
        st.rerun()

with table_col:
    st.subheader("📊 Decision Impact & Total Investment")
    portfolio = load_data()
    if not portfolio:
        st.info("No active decisions.")
    else:
        table_list = []
        for ticker, info in portfolio.items():
            live_p = yf.Ticker(ticker).fast_info['last_price']
            cur = "₹" if (".NS" in ticker or ".BO" in ticker) else "$"
            table_list.append({
                "Stock": ticker,
                "Shares": f"{info['shares']:,.2f}",
                "Avg Buy Price": f"{cur}{info['buy_price']:,.2f}",
                "Total Cost": f"{cur}{info['total_cost']:,.2f}",
                "Current Price": f"{cur}{live_p:,.2f}",
                "Status": "🎯 TARGET HIT" if live_p >= info['target_3m'] else "⏳ PENDING"
            })
        st.table(pd.DataFrame(table_list))
