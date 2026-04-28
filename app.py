import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="DCF Valuation Model", layout="wide")

# -----------------------
# Functions
# -----------------------

def project_fcf(fcf, growth, years):
    return [fcf * (1 + growth) ** t for t in range(1, years + 1)]

def discount(cash_flows, wacc):
    return [cf / (1 + wacc) ** (i + 1) for i, cf in enumerate(cash_flows)]

def terminal_value(last_fcf, growth, terminal_growth, wacc):
    if wacc <= terminal_growth:
        return None
    return (last_fcf * (1 + growth) * (1 + terminal_growth)) / (wacc - terminal_growth)

# -----------------------
# UI
# -----------------------

st.title("📊 DCF Valuation Model")

st.sidebar.header("Assumptions")

fcf = st.sidebar.number_input("Current Free Cash Flow ($M)", value=100.0)
growth = st.sidebar.number_input("FCF Growth Rate (%)", value=5.0) / 100
years = st.sidebar.slider("Projection Period", 1, 10, 5)
wacc = st.sidebar.number_input("Discount Rate (WACC %)", value=10.0) / 100
terminal_growth = st.sidebar.number_input("Terminal Growth Rate (%)", value=2.0) / 100
shares = st.sidebar.number_input("Shares Outstanding (M)", value=50.0)

# Safety check
if wacc <= terminal_growth:
    st.error("WACC must be greater than terminal growth rate.")
    st.stop()

# -----------------------
# Model
# -----------------------

fcf_proj = project_fcf(fcf, growth, years)
pv_fcf = discount(fcf_proj, wacc)

tv = terminal_value(fcf_proj[-1], growth, terminal_growth, wacc)
pv_tv = tv / (1 + wacc) ** years

enterprise_value = sum(pv_fcf) + pv_tv
price_per_share = enterprise_value / shares

# -----------------------
# Output
# -----------------------

col1, col2, col3 = st.columns(3)

col1.metric("Enterprise Value ($M)", f"{enterprise_value:,.2f}")
col2.metric("Terminal Value PV ($M)", f"{pv_tv:,.2f}")
col3.metric("Intrinsic Value / Share ($)", f"{price_per_share:,.2f}")

# -----------------------
# Table
# -----------------------

df = pd.DataFrame({
    "Year": range(1, years + 1),
    "FCF ($M)": fcf_proj,
    "PV FCF ($M)": pv_fcf
})

st.subheader("Cash Flow Projection")
st.dataframe(df, use_container_width=True)

# -----------------------
# Chart
# -----------------------

fig = go.Figure()

fig.add_trace(go.Bar(
    x=df["Year"],
    y=df["FCF ($M)"],
    name="FCF"
))

fig.add_trace(go.Scatter(
    x=df["Year"],
    y=df["PV FCF ($M)"],
    mode="lines+markers",
    name="PV of FCF"
))

fig.update_layout(
    title="FCF vs Discounted FCF",
    xaxis_title="Year",
    yaxis_title="$M"
)

st.plotly_chart(fig, use_container_width=True)
