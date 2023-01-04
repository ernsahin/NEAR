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
st.markdown("<h1 style='text-align: center; color: White;'> Contracts Of NEAR </h1>", unsafe_allow_html=True)
date=''
date=st.slider(
        "How Many Days You Want For Your Data",
        min_value=0,
        value=360
        ) 


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
data = f"""
with contracts as (
  select
  distinct tx_receiver  as contract,
  min(events.block_timestamp) as date_contract_deployed
  
  from near.core.fact_actions_events events LEFT JOIN near.core.fact_transactions txs on txs.tx_hash = events.tx_hash  WHERE action_name='DeployContract' 
  GROUP BY 1 
)
select 
date_trunc('day',date_contract_deployed) as date ,
count(distinct contract) as contracts_deployed_daily,
avg(contracts_deployed_daily) over (order by date) as avg_contracts,
sum(contracts_deployed_daily) over (order by date) as contracts_deployed_cumulative
from contracts where date >= current_date - interval '{date} days'
GROUP BY date
ORDER BY date


"""
query2=f"""
with blocks as (
  select block_timestamp,
block_id,
tx_count,
lag(block_timestamp, 1)  over (order by block_timestamp) as lag1,
datediff(second, lag1, block_timestamp) as time_dif
from near.core.fact_blocks
)
SELECT 
  date_trunc('week',block_timestamp) as date,
  avg(time_dif) as avg_time_blocks, 
  max(time_dif) as max_time_blocks, 
  min(time_dif) as min_time_blocks,
  avg(tx_count) as avg_tx_per_block,
  max(tx_count) as max_tx_per_block,
  min(tx_count) as min_tx_per_block
FROM blocks where block_timestamp >= current_date - interval '{date} days'
GROUP BY date 
ORDER BY date 
"""
query3= f"""
with top_5 as (select  
date_trunc('month',block_timestamp) as date,
tx_receiver as protocol,
count(*) as txs,
row_number() over (partition by date order by (txs) desc ) as row_number
  
from near.core.fact_transactions

GROUP BY date,protocol 

ORDER BY date asc,row_number )
select 
*
from top_5 where row_number <= 5 AND protocol not in ('c9bde26f54187d2dba81987363842de6a42cc874cb160a4ac19d551d03e569da','	
2260fac5e5542a773aa44fbcfedf7c193bc2c599.factory.bridge.near')
ORDER By date asc , txs DESC 
"""
top10= f"""
with contracts as (
  select
  distinct tx_receiver  as contract,
  min(events.block_timestamp) as date_contract_deployed
  
  from near.core.fact_actions_events events LEFT JOIN near.core.fact_transactions txs on txs.tx_hash = events.tx_hash 
  WHERE action_name='DeployContract'  
  GROUP BY 1 
)
select 
contract,
count(*) as use_of_contracts
from contracts left join near.core.fact_transactions txs on txs.tx_receiver=contract
GROUP BY contract
ORDER BY use_of_contracts DESC
LIMIT 10
"""
near2= f"""
with  wallets as (
  select 
distinct tx_signer as wallet,
tx_hash as first_event,
min(block_timestamp) as first_interaction
  
from near.core.fact_transactions
group by wallet,first_event
having first_interaction >=  CURRENT_DATE - interval '3 month'

  ),
  txss as (select  
date_trunc('day',block_timestamp) as date,
tx_receiver as protocol,
count(*) as txs,
row_number() over (partition by date order by (txs) desc ) as row_number
  
from near.core.fact_transactions,wallets 
where date >= current_date - interval '3 months'  and first_event=tx_hash
GROUP BY date,protocol 

ORDER BY date asc,row_number ),
  cumulative as (
  select 
  date_trunc('day',first_interaction) as datee,
  count(distinct wallet) as wallet_cumulative,
  sum(wallet_cumulative) over (order by datee) as new_users_onbarding
  from wallets
  GROUP BY datee
  )
  
select 
date,
protocol,
txs,
row_number,
new_users_onbarding
from txss left join cumulative on datee=date where row_number <= 10  and date >= current_date - interval '{date} days'
order by date, txs DESC
"""
month= sdk.query(
    query3,
    cached=True,
    timeout_minutes=20,
    retry_interval_seconds=1 
)
tops = sdk.query(
    top10,
    ttl_minutes=60,
    cached=True,
    timeout_minutes=20,
    retry_interval_seconds=1 
)
daily_query=sdk.query(
  query2,
  ttl_minutes=60,
  cached=True,
  timeout_minutes=20,
  retry_interval_seconds=1 
)
near2=sdk.query(
  near2,
  ttl_minutes=60,
  cached=True,
  timeout_minutes=20,
  retry_interval_seconds=1 
)
near2_records=near2.records 
near2_data=pd.DataFrame.from_dict(near2_records)
data5=month.records 
monthly_data=pd.DataFrame.from_dict(data5)
daily=daily_query.records 
data_daily= pd.DataFrame.from_dict(daily)
transactions_query=sdk.query(
    data,
    ttl_minutes=60,
    cached=True,
    timeout_minutes=20,
    retry_interval_seconds=1 
)   
data3=tops.records 
data_contracts=pd.DataFrame.from_dict(data3)
txs=  transactions_query.records
data_transactions=pd.DataFrame.from_dict(txs)
data2 =pd.DataFrame.from_dict(txs)
 
# n= data2.pop(-1)
# st.write(n)
# st.write(data2['sales'][ -1: ])
 

col1,col3, col2 = st.columns([2,1,2])
col1.metric(":star2: Total Contracts Deployed At NEAR :star2:",data2['contracts_deployed_cumulative'][-1:])
col2.metric(":star2: Daily Average Of Contracts Deployed :star2:",data2['avg_contracts'][-1:])

 

blocks,blocks2=st.columns(2)
with blocks :
    st.title('Contracts Deployed Daily')
    chart_daily = px.bar(
        data_transactions,
        x='date',
        y='contracts_deployed_daily'
    )
    st.plotly_chart(chart_daily,use_container_width=True)

with blocks2 : 
      st.title("Contracts Deployed Cumulative")
      chart_daily = px.area(
            data_transactions,
            x='date',
            y='contracts_deployed_cumulative'
        )
      st.plotly_chart(chart_daily,use_container_width=True)
tx1,tx2 = st.columns(2)     
with tx1 :
      st.title("Most Popular Contracts Of NEAR Monthly")
      chart_daily = px.bar(
            monthly_data,
            x='date',
            y='txs',
            color='protocol'
        )
      st.plotly_chart(chart_daily,use_container_width=True) 

with tx2 :
      st.title("Top 10 Most Popular Contract OF NEAR")
      chart_daily = px.bar(
            data_contracts,
            x='contract',
            y='use_of_contracts',
            color='contract'
        )
      st.plotly_chart(chart_daily,use_container_width=True) 
contracts1,contracts2 = st.columns(2)
with contracts1 :
      st.title("Most Popular First Interaction Contracts Of New Users")
      chart_daily = px.bar(
            near2_data,
            x='date',
            y='txs',
            color='protocol'
        )
      st.plotly_chart(chart_daily,use_container_width=True) 

with contracts2 :
      st.title("Most Popular First Interaction Contracts Of New Users ( By TXs )")
      chart_daily = px.pie(
            near2_data,
            title="First Interaction Contracts Of Users",
            
            names='protocol',
            values='txs' )
            
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
