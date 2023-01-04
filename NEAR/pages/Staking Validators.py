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
api='c3f66c29-589c-49cb-b605-b6edceaa6d57'
sdk = ShroomDK(api)
st.markdown("<h1 style='text-align: center; color: White;'> NEAR STAKING </h1>", unsafe_allow_html=True)

timeframe=st.selectbox(
    "Select the Time Frame",
    ('day','week','month'),
    index=0

)

 
data1= f"""
 with  events as ( 
  select 
  txs.tx_hash,
  txs.tx_signer,
  deposit/pow(10,24) as near,
  tx_receiver
from near.core.fact_actions_events_function_call calll full outer join near.core.fact_transactions txs on txs.tx_hash=calll.tx_hash
WHERE method_name = 'deposit_and_stake'  
)
 

select 
  sum(near) as total_near_staked, 
  count(distinct(tx_receiver)) as total_validators,
  avg(near) as average_near_staked,
  count(distinct(tx_signer)) as total_unique_staker
from events  
"""

data2=f"""
 with  events as ( 
  select 
  date_trunc({timeframe},txs.block_timestamp::date) as date,
  txs.tx_hash,
  txs.tx_signer,
  deposit/pow(10,24) as near,
  tx_receiver
from near.core.fact_actions_events_function_call calll full outer join near.core.fact_transactions txs on txs.tx_hash=calll.tx_hash
WHERE method_name = 'deposit_and_stake'
)
 

select 
   date_trunc({timeframe},date) as date ,
  sum(near) as near_staked, 
  count(distinct(tx_receiver)) as validators,
  avg(near) as avg_staked,
  count(distinct(tx_signer)) as weekly_stakers
from events  where date >= '2022-01-01'
GROUP BY date 
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
single=pd.DataFrame.from_records(records2)

col2, col3,col4 = st.columns(3)
 
# col1.metric("Total NEAR Staked",records_data1['total_near_staked'])
col2.metric("Total Validators",records_data1['total_validators'])
col3.metric("Average NEAR Staked",records_data1['average_near_staked'])
col4.metric("Total Unique Stakers:star2:",records_data1['total_unique_staker'])
 


new1,tx1,tx3=st.columns([1,1,1])
with new1 :
    st.title('NEAR Staked')
    chart_daily = px.bar(
        records_data2,
        x='date',
        y='near_staked'
    )
    st.plotly_chart(chart_daily,use_container_width=True)


    
with tx1 :
      st.title("Validators")
      chart_daily = px.area(
            records_data2,
            x='date',
            y='validators'
        )
      st.plotly_chart(chart_daily,use_container_width=True) 

with tx3 :
      st.title("Average $NEAR Staked")
      chart_daily = px.area(
            records_data2,
            x='date',
            y='avg_staked'
        )
      st.plotly_chart(chart_daily,use_container_width=True) 