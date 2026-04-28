import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="DCF Valuation Model", layout="wide")

# -------------------------
# Helper Functions
# -------------------------

def project_fcf(fcf, growth, years):
    return [fcf * (1 + growth) ** t for t in range(1, years + 1)]

def discount(cash_flows, discount_rate):
    return [cf / (1 + discount_rate) ** i for i, cf in enumerate(cash_flows, start=1)]

def terminal_value(last_fcf, growth, terminal_growth, discount_rate):
    if discount_rate <= terminal_growth:
        return None
    return (last_fcf * (1 + growth) * (1 + terminal_growth)) / (discount_rate - terminal_growth)

# -------------------------
# UI Inputs
# -------------------------

st.title("📊 Discounted Cash Flow (DCF) Valuation Model")

st.sidebar.header("Assumptions")

fcf = st.sidebar.number_input("Current Free Cash Flow ($M)", value=100.0)
growth = st.sidebar.number_input("FCF Growth Rate (%)", value=5.0) / 100
years = st.sidebar.slider("Projection Period (Years)", 1, 10, 5)
wacc = st.sidebar.number_input("Discount Rate / WACC (%)", value=10.0) / 100
terminal_growth = st.sidebar.number_input("Terminal Growth Rate (%)", value=2.0) / 100
shares = st.sidebar.number_input("Shares Outstanding (M)", value=50.0)

st.sidebar.markdown("---")
st.sidebar.caption("Tip: Keep terminal growth < WACC for realism.")

# -------------------------
# Validation
# -------------------------

if wacc <= terminal_growth:
    st.error("WACC must be greater than terminal growth rate.")
    st.stop()

# -------------------------
# Core Calculations
# -------------------------

fcf_proj = project_fcf(fcf, growth, years)
pv_fcf = discount(fcf_proj, wacc)

last_fcf = fcf_proj[-1]
tv = terminal_value(fcf, growth, terminal_growth, wacc)
pv_tv = tv / (1 + wacc) ** years

enterprise_value = sum(pv_fcf) + pv_tv
equity_value = enterprise_value  # simplified (no net debt input)
price_per_share = (equity_value * 1e6) / (shares * 1e6)

# -------------------------
# Output Section
# -------------------------

col1, col2, col3 = st.columns(3)

col1.metric("Enterprise Value ($M)", f"{enterprise_value:,.2f}")
col2.metric("Terminal Value PV ($M)", f"{pv_tv:,.2f}")
col3.metric("Intrinsic Value / Share ($)", f"{price_per_share:,.2f}")

# -------------------------
# Cash Flow Table
# -------------------------

st.subheader("📄 Cash Flow Projection")

df = pd.DataFrame({
    "Year": list(range(1, years + 1)),
    "FCF ($M)": fcf_proj,
    "PV of FCF ($M)": pv_fcf
})

st.dataframe(df, use_container_width=True)

# -------------------------
# Visualization
# -------------------------

fig = go.Figure()

fig.add_trace(go.Bar(
    x=df["Year"],
    y=df["FCF ($M)"],
    name="FCF Projection"
))

fig.add_trace(go.Scatter(
    x=df["Year"],
    y=df["PV of FCF ($M)"],
    mode="lines+markers",
    name="Present Value"
))

fig.update_layout(
    title="Projected vs Discounted Cash Flows",
    xaxis_title="Year",
    yaxis_title="($M)"
)

st.plotly_chart(fig, use_container_width=True)

# -------------------------
# Sensitivity Table
# -------------------------

st.subheader("📊 Sensitivity Analysis (Value per Share)")

wacc_range = np.arange(wacc - 0.02, wacc + 0.025, 0.01)
growth_range = np.arange(growth - 0.02, growth + 0.025, 0.01)

sensitivity = pd.DataFrame(index=[f"{g:.1%}" for g in growth_range],
                           columns=[f"{w:.1%}" for w in wacc_range])

for g in growth_range:
    for w in wacc_range:
        if w <= terminal_growth:
            sensitivity.loc[f"{g:.1%}", f"{w:.1%}"] = np.nan
        else:
            proj = project_fcf(fcf, g, years)
            pv = discount(proj, w)
            tv = terminal_value(fcf, g, terminal_growth, w)
            if tv:
                ev = sum(pv) + tv / (1 + w) ** years
                sensitivity.loc[f"{g:.1%}", f"{w:.1%}"] = round((ev * 1e6) / (shares * 1e6), 2)

st.dataframe(sensitivity, use_container_width=True)

# -------------------------
# Footer Insight
# -------------------------

st.markdown("---")
st.caption("DCF Model: Simplified equity valuation assuming no net debt adjustments.")
