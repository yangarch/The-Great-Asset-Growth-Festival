import streamlit as st
import pandas as pd
import requests
import os
from dotenv import load_dotenv
import plotly.express as px
import yfinance as yf

load_dotenv()

st.set_page_config(page_title="NONE DASHBOARD", page_icon="📈")

# Configuration
API_URL = os.getenv("API_URL", "http://backend:8001/api/assets")
START_AMOUNTS = {
    "KS": float(os.getenv("START_AMOUNT_KS", 2000000)),
    "DH": float(os.getenv("START_AMOUNT_DH", 10000000)),
    "BH": float(os.getenv("START_AMOUNT_BH", 2000000)),
    "YJ": float(os.getenv("START_AMOUNT_YJ", 5000000)),
}

st.title("🎢 None Festival")
st.subheader("Leaderboard: Who is the Growth King? :)")

# Fetch Data
try:
    try:
        response = requests.get(API_URL, timeout=3)
    except Exception:
        # Fallback to localhost if 'backend' is not resolvable (e.g., running locally)
        if "backend" in API_URL:
             st.warning("⚠️ Could not connect to internal 'backend'. trying 'localhost'...")
             API_URL = API_URL.replace("backend", "localhost")
             response = requests.get(API_URL, timeout=3)
        else:
            raise



    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)
    else:
        st.error(f"Failed to fetch data: {response.status_code}")
        df = pd.DataFrame()
except Exception as e:
    st.error(f"❌ Connection Error: {e}")
    st.warning("""
    **Could not connect to the Backend API.**
    
    1. Ensure the backend container is running:
       `docker compose ps`
    2. If running locally, check if uvicorn is active on port 8000.
    
    Refresh this page after checking.
    """)
    df = pd.DataFrame()

if not df.empty:
    # Process Data
    df['date'] = pd.to_datetime(df['date'])
    
    # Keep only the latest entry per user per day
    if 'id' in df.columns:
        df = df.sort_values('id').drop_duplicates(subset=['name', 'date'], keep='last')
    else:
        df = df.drop_duplicates(subset=['name', 'date'], keep='last')
    
    # Calculate Growth Rate
    def calculate_growth(row):
        start = START_AMOUNTS.get(row['name'], 1)
        return row['amount'] / start

    df['growth_rate'] = df.apply(calculate_growth, axis=1)

    # 1. Leaderboard (Latest Data)
    latest_df = df.sort_values(by='date').groupby('name').tail(1)
    latest_df = latest_df.sort_values(by='growth_rate', ascending=False)
    
    # Display Metrics
    cols = st.columns(len(latest_df))
    for i, (index, row) in enumerate(latest_df.iterrows()):
        with cols[i]:
            start_amount = START_AMOUNTS.get(row['name'], 1)
            net_profit = row['amount'] - start_amount
            st.metric(
                label=f"{i+1}위 {row['name']}",
                value=f"{(row['growth_rate']-1)*100:.1f}%",
                delta=f"{net_profit:,.0f} KRW"
            )

    st.divider()

    # 2. Growth Chart (Line Chart starting at 1.0)
    # Add initial point (Day 0) for cleaner graph? 
    # Or just plot current data normalized.
    
    st.subheader("Growth Race 🏎️")
    
    # Sort for graph
    df_sorted = df.sort_values(by='date')
    
    # 2. Add "Start" point (1.0) for better visualization
    # We create a synthetic data point at "Earliest Date - 1 Day" with 1.0 growth
    start_date = df_sorted['date'].min() - pd.Timedelta(days=1)
    start_points = []
    
    for name in df['name'].unique():
        start_points.append({
            'name': name,
            'date': start_date,
            'amount': START_AMOUNTS.get(name, 0),
            'growth_rate': 1.0
        })
    
    df_start = pd.DataFrame(start_points)
    df_chart = pd.concat([df_start, df_sorted], ignore_index=True).sort_values(by='date')
    
    df_chart = df_chart.copy()
    df_chart['growth_rate'] = (df_chart['growth_rate'] - 1) * 100

    # 가장 최근 날짜 기준 growth_rate 순위 (KOSPI 200 제외)
    non_kospi_latest = df_chart[df_chart['name'] != 'KOSPI 200'].sort_values('date').groupby('name').tail(1)
    crown_name = non_kospi_latest.sort_values('growth_rate', ascending=False).iloc[0]['name']
    turtle_name = non_kospi_latest.sort_values('growth_rate', ascending=True).iloc[0]['name']
    df_chart['name'] = df_chart['name'].apply(
        lambda n: f"👑 {n}" if n == crown_name else (f"🐢 {n}" if n == turtle_name else n)
    )

    fig = px.line(
        df_chart,
        x='date',
        y='growth_rate',
        color='name',
        markers=True,
        title="Asset Growth Rate Over Time",
        labels={'growth_rate': 'Growth (%)'}
    )
    fig.update_layout(yaxis_ticksuffix="%")

    # KOSPI 200 (KODEX 069500.KS) 비교선 추가
    KOSPI_START_DATE = "2026-02-01"
    try:
        kospi_raw = yf.download("069500.KS", start=KOSPI_START_DATE, progress=False, auto_adjust=True)
        if not kospi_raw.empty:
            kospi = kospi_raw[["Close"]].copy()
            kospi.index = pd.to_datetime(kospi.index)
            kospi.index = kospi.index.tz_localize(None)
            kospi.columns = ["close"]
            kospi = kospi.sort_index()

            # 시작일 기준 정규화
            start_price = kospi.iloc[0]["close"]
            kospi["growth_rate"] = (kospi["close"] / start_price - 1) * 100

            # 시작점(0.0) 추가
            start_row = pd.DataFrame([{
                "growth_rate": 0.0
            }], index=[pd.Timestamp(KOSPI_START_DATE) - pd.Timedelta(days=1)])
            kospi = pd.concat([start_row, kospi[["growth_rate"]]]).sort_index()

            fig.add_scatter(
                x=kospi.index,
                y=kospi["growth_rate"],
                mode="lines",
                name="KOSPI 200",
                line=dict(color="gray", dash="dot", width=2),
            )
    except Exception as e:
        st.warning(f"⚠️ KOSPI 200 데이터를 불러오지 못했습니다: {e}")

    # Add horizontal line at 1.0
    fig.add_hline(y=0.0, line_dash="dash", line_color="lightgray", annotation_text="Start")

    st.plotly_chart(fig, use_container_width=True)

#     # 3. Data Entry Form (Optional Helper)
#     with st.expander("📝 Add New Data"):
#         with st.form("add_data"):
#             name = st.selectbox("Name", ["KS", "DH", "BH", "YJ"])
#             date = st.date_input("Date")
#             amount = st.number_input("Current Amount (KRW)", min_value=0)
#             submitted = st.form_submit_button("Submit")
            
#             if submitted:
#                 payload = {
#                     "name": name,
#                     "date": str(date),
#                     "amount": amount
#                 }
#                 res = requests.post(API_URL, json=payload)
#                 if res.status_code == 200:
#                     st.success("Data Added! Refresh page.")
#                 else:
#                     st.error(f"Error: {res.text}")
# else:
#     st.info("No data available yet. Use the API or form to add data.")
    
#     with st.expander("📝 Add First Data Entry", expanded=True):
#         with st.form("add_first_data"):
#             name = st.selectbox("Name", ["KS", "DH", "BH", "YJ"])
#             date = st.date_input("Date")
#             amount = st.number_input("Current Amount (KRW)", min_value=0)
#             submitted = st.form_submit_button("Submit")
            
#             if submitted:
#                 payload = {
#                     "name": name,
#                     "date": str(date),
#                     "amount": amount
#                 }
#                 try:
#                     res = requests.post(API_URL, json=payload)
#                     if res.status_code == 200:
#                         st.success("Data Added! Refresh page.")
#                     else:
#                         st.error(f"Error: {res.text}")
#                 except Exception as e:
#                      st.error(f"Failed to connect: {e}")

    # 4. Admin / Reset
    # with st.expander("⚠️ Admin Zone (Reset Data)"):
    #     st.warning("This will delete ALL data.")
    #     if st.button("🔴 Reset All Data"):
    #         try:
    #             res = requests.delete(API_URL)
    #             if res.status_code == 200:
    #                 st.success("All data deleted. Refreshing...")
    #                 st.rerun()
    #             else:
    #                 st.error(f"Failed to reset: {res.text}")
    #         except Exception as e:
    #             st.error(f"Error: {e}")
