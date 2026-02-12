import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

# -----------------------------------
# Page Configuration
# -----------------------------------
st.set_page_config(
    page_title="Shipping Analytics Dashboard",
    layout="wide"
)

st.title("📦 Shipping Performance Analytics Dashboard")

# -----------------------------------
# Load Cleaned Data
# -----------------------------------
df = pd.read_csv('/content/cleaned_data.csv')

# Convert date column (if already datetime this won't harm)
df['Order Date'] = pd.to_datetime(df['Order Date'])

# -----------------------------------
# Sidebar Filters (User Capabilities)
# -----------------------------------
st.sidebar.header("🔎 Filters")

# Date Range Filter
date_range = st.sidebar.date_input(
    "Select Date Range",
    [df['Order Date'].min(), df['Order Date'].max()]
)

# Region Filter
region_filter = st.sidebar.multiselect(
    "Select Region",
    options=df['Region'].unique(),
    default=df['Region'].unique()
)

# Ship Mode Filter
ship_mode_filter = st.sidebar.multiselect(
    "Select Ship Mode",
    options=df['Ship Mode'].unique(),
    default=df['Ship Mode'].unique()
)

# Lead Time Threshold
lead_threshold = st.sidebar.slider(
    "Minimum Lead Time (Days)",
    min_value=int(df['Shipping_lead_time'].min()),
    max_value=int(df['Shipping_lead_time'].max()),
    value=int(df['Shipping_lead_time'].min())
)
# Route Level
route_type = st.sidebar.radio(
 "Select route Level",
   ["Region Route","State Route"]
)
if route_type == "Region Route":
  route_column = "Region_Route"
else:
  route_column = "State_Route"
# -----------------------------------
# Apply Filters
# -----------------------------------
filtered_df = df[
    (df['Order Date'].between(pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1]))) &
    (df['Region'].isin(region_filter)) &
    (df['Ship Mode'].isin(ship_mode_filter)) &
    (df['Shipping_lead_time'] >= lead_threshold)
]

# -----------------------------------
# KPI Section
# -----------------------------------
st.subheader("📊 Key Performance Indicators")

col1, col2, col3 = st.columns(3)

col1.metric("Total Orders", len(filtered_df))
col2.metric("Average Lead Time", round(filtered_df['Shipping_lead_time'].mean(), 2))
col3.metric("Max Lead Time", round(filtered_df['Shipping_lead_time'].max(), 2))

st.markdown("---")

# -----------------------------------
# Route Efficiency Overview
# -----------------------------------
st.header("🚦 Route Efficiency Overview")

scaler = MinMaxScaler()

route_summary = (
    filtered_df
    .groupby(route_column)
    .agg(
        avg_lead_time=('Shipping_lead_time', 'mean')
    )
)

route_summary['efficiency_score'] = 1 - scaler.fit_transform(
    route_summary[['avg_lead_time']]
)

route_summary = route_summary.sort_values(
    by='efficiency_score', ascending=False
)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Average Lead Time by Route")
    st.bar_chart(route_summary['avg_lead_time'])

with col2:
    st.subheader("Route Performance Leaderboard")
    st.dataframe(route_summary)

st.markdown("---")

# -----------------------------------
# Regional Bottleneck Visualization
# -----------------------------------
st.header("🌎 Regional Bottleneck Analysis")

region_perf = (
    filtered_df
    .groupby('Region')['Shipping_lead_time']
    .mean()
    .sort_values(ascending=False)
)

st.bar_chart(region_perf)

st.markdown("---")

# -----------------------------------
# Ship Mode Comparison
# -----------------------------------
st.header("🚚 Ship Mode Comparison")

ship_mode_perf = (
    filtered_df
    .groupby('Ship Mode')['Shipping_lead_time']
    .mean()
    .sort_values(ascending=False)
)

st.bar_chart(ship_mode_perf)

st.markdown("---")

# -----------------------------------
# Route Drill-Down
# -----------------------------------
st.header("🔍 Route Drill-Down Analysis")

selected_route = st.selectbox(
    "Select Route",
    filtered_df[route_column].unique()
)

route_df = filtered_df[filtered_df[route_column] == selected_route]

col1, col2 = st.columns(2)

with col1:
    st.subheader("State-Level Performance")
    state_perf = (
        route_df
        .groupby('State/Province')['Shipping_lead_time']
        .mean()
        .sort_values(ascending=False)
    )
    st.bar_chart(state_perf)

with col2:
    st.subheader("Order-Level Shipment Timeline")
    st.dataframe(
        route_df[['Order ID', 'Order Date', 'Shipping_lead_time']]
    )

st.markdown("---")

st.success("Dashboard Loaded Successfully ✅")
