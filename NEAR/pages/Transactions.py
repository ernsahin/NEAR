import streamlit as st
import altair as alt
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from shroomdk import ShroomDK
st.set_page_config(layout="wide")
# header = st.container()
dataset= st.container()
# features= st.container()
modelTraining= st.container()
api='53012785-d2f9-49a0-81a9-cdd22bc8a330'
sdk = ShroomDK(api)
st.markdown("<h1 style='text-align: center; color: White;'> Transactions and Fees ON NEAR</h1>", unsafe_allow_html=True)
st.sidebar()


# marketplace= st.checkbox(
#     ['hadeswap','opensea'] 
# )
# st.write(marketplace)

# a=('opensea','hadeswap')
# marketplace= st.multiselect(
#     "Select The Marketplaces You Want To Look",
#     a,
#     default=a
#     ('"hadeswap"','coral cube','opensea'),
#     default=('"hadeswap'",'coral cube','opensea'),
#     key=str 
     

# )
data1= f"""
select 
date_trunc('week',block_timestamp) as date,
avg(transaction_fee/pow(10,24)) as avg_tx_fee,
sum(transaction_fee/pow(10,24)) as tx_fee,
count(distinct tx_signer) as unique_users,
count(*)  as txs,
sum(txs) over (order by date) as cumulative_txs,
sum(tx_fee) over (order by date) as cumulative_tx_fee
from near.core.fact_transactions
GROUP BY date 
ORDER BY date 
 
"""

data2=f"""
with  wallets as (
  select 
  distinct tx_signer as wallet,
   
min(block_timestamp) as first_interaction
  
from near.core.fact_transactions
group by wallet 
 

  )
 select  
date_trunc('week',first_interaction) as date,
count(distinct wallet) as new_users,
sum(new_users) over (order by date) as user_growth
from wallets
GROUP BY DATE 
ORDER BY date 
 
"""

query_result_set1 = sdk.query(
    data1,
    ttl_minutes=60,
    cached=True,
    timeout_minutes=20,
    retry_interval_seconds=1 
)
query_result_set2=sdk.query(
    data2,
    ttl_minutes=60,
    cached=True,
    timeout_minutes=20,
    retry_interval_seconds=1 
)

records1=query_result_set1.records
records_data1=pd.DataFrame.from_dict(records1)
records2=query_result_set2.records 
records_data2=pd.DataFrame.from_dict(records2) 

tx1,tx2=st.columns([1,1])
with tx1 :
    st.title('Daily Transactions')
    chart_daily = px.line(
        records_data1,
        x='date',
        y='txs'
    )
    st.plotly_chart(chart_daily,use_container_width=True)


    
with tx2 :
      st.title("Daily Unique Users")
      chart_daily = px.area(
            records_data1,
            x='date',
            y='unique_users'
        )
      st.plotly_chart(chart_daily,use_container_width=True) 



new1,new2=st.columns([1,1])
with new1 :
    st.title('Average Transaction Fees On NEAR')
    chart_daily = px.line(
        records_data1,
        x='date',
        y='avg_tx_fee'
    )
    st.plotly_chart(chart_daily,use_container_width=True)


    
with new2 :
      st.title("Weekly $NEAR Spent ON Fees")
      chart_daily = px.area(
            records_data1,
            x='date',
            y='tx_fee'
        )
      st.plotly_chart(chart_daily,use_container_width=True) 


# plotly= px.bar(r
#     data_transactions,
#     x='week',
#     y='txs'
# )
 
# st.bar_chart(data=data_transactions,x='week',y='txs',width=0,height=0)
# st.plotly_chart(plotly,theme="streamlit", use_container_width=True)

# daily_txs,fails=st.columns([2,2])
# tps,fees=st.columns([1,1])
# with plotly : 
#     st.title("Plotly Transactions")
#     chart= px.bar(
#         data_transactions,
#         x='week',
#         y='txs'
#     )
# #     st.plotly_chart(chart,theme='streamlit',use_container_width=True)
# daily_txs,fails=st.columns([1,1])

# with fails :
#     st.title('Transactions Succsess  Rate')
#     fail_rate= alt.Chart(data_transactions).mark_area().encode(
#         alt.X('date:T'),
#         alt.Y('volume:Q'),
#         color='marketplace'
#     )
#     st.altair_chart(fail_rate,use_container_width=True)
# with fees :
#     st.title('Weekly Average Fees $LUNA')
#     fee=alt.Chart(data_transactions).mark_line().encode(
#         alt.X('week:T'),
#         alt.Y('avg_fee_luna:Q')
#     )
#     st.altair_chart(fee,use_container_width=True)
# with tps:
#     st.title('Weekly TPS')
#     tps=alt.Chart(data_transactions).mark_line().encode(
#         alt.X('week:T'),
#         alt.Y('avg_tps:Q')
#     )
#     #properties(width=800, height=400)
    
#     st.altair_chart(tps,use_container_width=True)

# with plotly1 :
#     st.title('Daily Transactions')
#     chart_transactions = px.violin(
#         data_transactions,
#         x='week',
#         y='txs'
#     )
#     st.plotly_chart(chart_transactions,use_container_width=True)

# with plotly2 :
#     st.title('Daily Transactions')
#     chart_transactions = px.histogram(
#         data_transactions,
#         x='week',
#         y='avg_fee_luna'
#     )
#     st.plotly_chart(chart_transactions,use_container_width=True)


# Parameters can be passed into SQL statements 
# via native string interpolation
# my_address = "0x...."
# sql = f"""
#      SELECT 
#      block_timestamp::date as date,
#      COUNT(*) as txs
#      FROM   ethereum.core.fact_transactions
#      WHERE date >= '2022-01-01'
#      GROUP BY date 
#      ORDER BY date DESC
     
# """

# Run the query against Flipside's query engine 
# and await the results
# query_result_set = sdk.query(
#     sql,
#     ttl_minutes=60,
#     cached=True,
#     timeout_minutes=20,
#     retry_interval_seconds=1 
# )
# records = query_result_set.records
# eth_txs = f"""
# SELECT 
#      block_timestamp::date as date,
#      COUNT(*) as txs
#      FROM   ethereum.core.fact_transactions
#      WHERE date >= '2021-01-01'
#      GROUP BY date 
#      ORDER BY date DESC
#      LIMIT 30
# """
# eth_records = sdk.query(
#     eth_txs,
#     ttl_minutes=60,
#     cached=True,
#     timeout_minutes=20,
#     retry_interval_seconds=1 
# )
# eth_2=  eth_records.records
# asd,second=st.columns([1,1])

# # Iterate over the results
# with asd : 
#     st.title('Shrooms In API Out')
#     data_shroom=pd.DataFrame.from_dict(records)
#     shro=alt.Chart(data_shroom).mark_bar().encode(   
#         alt.X('date:T'),
#         alt.Y('txs:Q')
#         )
#     st.altair_chart(shro,use_container_width=True)
# with second :
#     st.title('ETH 2021')
#     data=pd.DataFrame.from_dict(eth_2)
#     data2=alt.Chart(data).mark_area().encode(
#         alt.X('date:T'),
#         alt.Y('txs:Q')
#     )
#     st.altair_chart(data2,use_container_width=True)

    
   
    




# with header :
#     st.title('Terra Mega Dashboard')
# df = pd.read_json("https://node-api.flipsidecrypto.com/api/v2/queries/446958b3-a694-4bb5-98a0-41d556a96c5d/data/latest")
# with dataset : 
#       st.header('Transaction Success Status')
#       df=pd.read_json("https://node-api.flipsidecrypto.com/api/v2/queries/423c91f7-141e-4c00-8768-14f610551c4d/data/latest")
#       ye = alt.Chart(df).mark_line().encode(
#       alt.X('DATE_DAY:T',scale=alt.Scale(zero=False)) ,
#       alt.Y('TXS:Q',scale=alt.Scale(zero=False)),
#       alt.StrokeDash('STATUS'),
#       alt.Color('STATUS:N'),
#       alt.OpacityValue(1),
#       tooltip = [
#                alt.Tooltip('DATE_DAY'),
#                alt.Tooltip('TXS'),
#                alt.Tooltip('STATUS')
#               ]
#     )
#       chart= df
#       st.altair_chart(ye,use_container_width=True)
