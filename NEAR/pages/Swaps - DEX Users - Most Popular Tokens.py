import streamlit as st
import altair as alt
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from shroomdk import ShroomDK
st.set_page_config(layout="wide")
from PIL import Image
# header = st.container()
dataset= st.container()
# features= st.container() 
modelTraining= st.container()
api='c3f66c29-589c-49cb-b605-b6edceaa6d57'
sdk = ShroomDK(api)
st.markdown("<h1 style='text-align: center; color: White;'> NEAR Traders </h1>", unsafe_allow_html=True)


def add_logo(logo_path, width, height):
    """Read and return a resized logo"""
    logo = Image.open('a.png')
    modified_logo = logo.resize((400, 400))
    return modified_logo

timeframe=st.selectbox(
    "Select the Time Frame",
    ('day','week','month'),
    index=0

)
st.image(add_logo)
 
data1= f"""
 with first_swap as (
  select 
  trader,
  min(block_timestamp::date) as min_date
   
from near.core.ez_dex_swaps
  GROUP BY trader 
 
)
select 
date_trunc({timeframe},min_date) as date,
count(distinct trader) as new_traders,
sum(new_traders) over (order by date) as cumulative_new_traders
from first_swap
GROUP BY date 
ORDER BY date 
"""

data2=f"""
select 
  date_trunc({timeframe},block_timestamp) as date,
  count(distinct tx_hash) as swaps,
  count(distinct trader) as trader,
  sum(swaps) over (order by date) as cumulative_swaps
from near.core.ez_dex_swaps
  GROUP BY date 
  ORDER BY date 
 
"""

data3= f"""
with tokens as (
  select 
  distinct token_in as token
  from near.core.ez_dex_swaps
),
  rowss as (select 
date_trunc('week',block_timestamp) as date,
token,
count(distinct tx_hash) as swaps,
row_number() over (partition by date order by swaps desc) as row_number
from near.core.ez_dex_swaps,tokens where (token_in = token or token_out=token)
GROUP BY token,date
ORDER BY swaps DESC 
 )
select * from rowss where row_number <= 5 
order by date 
"""
data4=f"""
with tokens as (
  select 
  distinct token_in as token
  from near.core.ez_dex_swaps
)
select 
token,
count(distinct tx_hash) as swaps
from near.core.ez_dex_swaps,tokens where (token_in = token or token_out=token)
GROUP BY token
ORDER BY swaps DESC 
LIMIT 10
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
query_result_set3=sdk.query(
    data3,
    ttl_minutes=60,
    cached=True,
    timeout_minutes=20,
    retry_interval_seconds=1 
)
query_result_set4=sdk.query(
    data4,
    ttl_minutes=60,
    cached=True,
    timeout_minutes=20,
    retry_interval_seconds=1 
)

records1=query_result_set1.records
records_data1=pd.DataFrame.from_dict(records1)
records3=query_result_set3.records
records_data3=pd.DataFrame.from_dict(records3)
records2=query_result_set2.records 
records_data2=pd.DataFrame.from_dict(records2) 
single=pd.DataFrame.from_records(records2)
records4=query_result_set4.records 
records_data4=pd.DataFrame.from_dict(records4)

col2, col3 = st.columns(2)
 
# col1.metric("Total NEAR Staked",records_data1['total_near_staked'])
col2.metric("Total Swaps",records_data2['cumulative_swaps'][-1:])
col3.metric("Unique NEAR Traders",records_data1['cumulative_new_traders'][-1:])
 
 


# new1,tx1,tx3=st.columns([1,1,1])
# tx4,tx5=st.columns(2)
new1=st.container()
tx1=st.container()
tx3=st.container()
tx4=st.container()
tx5=st.container()
with new1 :
    st.title('NEAR Traders')
    chart_daily = px.bar(
        records_data1,
        x='date',
        y='new_traders'
    )
    st.plotly_chart(chart_daily,use_container_width=True)


    
with tx1 :
      st.title("Cumulative Swaps NEAR")
      chart_daily = px.area(
            records_data2,
            x='date',
            y='cumulative_swaps'
        )
      st.plotly_chart(chart_daily,use_container_width=True) 

with tx3 :
      st.title("Daily Swaps")
      chart_daily = px.area(
            records_data2,
            x='date',
            y='swaps'
        )
      st.plotly_chart(chart_daily,use_container_width=True) 
with tx4 : 
    st.title("Most Popular Tokens By Swaps") 
    chart_daily = px.area(
            records_data3,
            x='date',
            y='swaps',
            color='token'
        )
    st.plotly_chart(chart_daily,use_container_width=True) 
with tx5 : 
    st.title("Most Popular Tokens By Swaps") 
    chart_daily = px.pie(
            records_data4,
            names='token',
            values='swaps' 
        )
    st.plotly_chart(chart_daily,use_container_width=True) 