from stock_utility_handler import StockAPI, StockAnalyzer
from ai_insights_handler import AIInsights
from config import ALPHVANTAGE_API_KEY, GEMINI_API_KEY
import pandas as pd

import streamlit as st

if 'page' not in st.session_state:
    st.session_state.page = "page1"  
    st.session_state.ticker = "GOOG"  
    st.session_state.image_path = ""
    st.session_state.ai_insights = ""
    st.session_state.internal_results_available = False
    st.session_state.indices_results_available = False


def get_stock_symbols():
    companies = pd.read_csv('companies.csv')
    return companies

companies = get_stock_symbols()

def format_stock_option(option_symbol):
    # Find the corresponding name for the given symbol
    stock_name = companies[companies.ticker == option_symbol].company_name.iloc[0]
    return f"{option_symbol} - {stock_name}"

def page1():
    st.title('Stock AI Agent')


    st.session_state.ticker = st.selectbox("Enter Stock Ticker Symbol", companies.ticker, index=None, format_func=format_stock_option, key="ticker_input") #Use key, corrected index.

    if st.button('Submit'):
        st.session_state.page = "page2"  # Go to the next page
        st.session_state.internal_results_available = False
        st.rerun() 

    st.markdown("---")


    if not st.session_state.indices_results_available: 
        indices = ["VOO", "QQQ"] # POC only. Alphavantage does not provide data on stock indices anymore. Will have to obtain this data elsewhere. 
        for stock in indices: 
            image_path=f"images/{stock}.png"   
            st.session_state.image_path=image_path
                
            stock_api_obj = StockAPI(ALPHVANTAGE_API_KEY)
    
            market_data=stock_api_obj.get_stock_info(stock) 
    
            stock_analyzer_obj=StockAnalyzer()
    
            df=stock_analyzer_obj.json_to_dataframe(market_data,stock) 
    
            stock_analyzer_obj.plot_index_data(df,stock,image_path) 

        st.session_state.indices_results_available = True

    if  st.session_state.indices_results_available:
        st.subheader("Stock Indexes")
        col1, col2 = st.columns(2)
        with col1:
            st.image(f"images/{indices[0]}.png", caption=f"S&P 500 Chart", width='stretch')  
        with col2:
            st.image(f"images/{indices[1]}.png", caption=f"Nasdaq-100 Chart", width='stretch')  
        
    
    st.sidebar.header("About")
    st.sidebar.write("This is a stock analysis platform for the NYSE and NASDAQ. For a given stock, Stock AI Agent will provide analysis of the last 100 days of price trends, volume traded, and moving averages. Given this context, you will be provided insights about the stock and potential to purchase, hold, or sell.")
    st.sidebar.write("This is for educational and informational purposes only - stock decisions should not be made with the information provided.")                     

def page2():


    st.title(f"Analysis for {st.session_state.ticker}")  # Use stored inputs 
    
    stock=st.session_state.ticker
    # market=st.session_state.market
    if not st.session_state.internal_results_available:
        with st.spinner('Analyzing the last 100 days of price trends, volume traded, and moving averages, and gathering insights on potential to purchase, hold, or sell...'):
            image_path=f"images/{stock}.png"   
            st.session_state.image_path=image_path
            
            stock_api_obj = StockAPI(ALPHVANTAGE_API_KEY)

            market_data=stock_api_obj.get_stock_info(stock) 

            stock_analyzer_obj=StockAnalyzer()

            df=stock_analyzer_obj.json_to_dataframe(market_data,stock) 

            stock_analyzer_obj.plot_stock_data(df,stock,image_path) 

            ai_insights_obj=AIInsights(GEMINI_API_KEY)

            response=ai_insights_obj.get_ai_insights(image_path,stock)   

            candidates = response.candidates  
            for candidate in candidates:
                text_parts = candidate.content.parts
                for part in text_parts:
                    print(part.text)
                    st.session_state.ai_insights += part.text   
            st.session_state.internal_results_available = True
        
    if  st.session_state.internal_results_available:
        st.subheader("Chart Analysis")
        st.image(st.session_state.image_path, caption=f"{st.session_state.ticker} Chart", width='stretch')  # Example image

        st.subheader("Analysis Results")
        st.write(st.session_state.ai_insights)
        
        if st.button("Back"): #Back button
            st.session_state.page = "page1"
            st.session_state.internal_results_available = False
            st.session_state.ai_insights = ""
            st.rerun()


if st.session_state.page == "page1":
    page1()
elif st.session_state.page == "page2":
    page2()
