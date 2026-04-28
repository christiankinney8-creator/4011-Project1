import streamlit as st

st.set_page_config(page_title="DCF Valuation Tool", layout="centered")

st.title("📊 Discounted Cash Flow (DCF) Valuation Model")

st.write("Enter assumptions below to estimate intrinsic value per share.")

# Inputs
st.header("Assumptions")

fcf = st.number_input("Current Free Cash Flow ($M)", value=100.0)
growth_rate = st.number_input("Annual FCF Growth Rate (%)", value=5.0) / 100
years = st.slider("Projection Period (Years)", 1, 10, 5)
discount_rate = st.number_input("Discount Rate (WACC %) ", value=10.0) / 100
terminal_growth = st.number_input("Terminal Growth Rate (%)", value=2.0) / 100
shares_outstanding = st.number_input("Shares Outstanding (M)", value=50.0)

# Projection
st.header("Projected Cash Flows")

cash_flows = []
for t in range(1, years + 1):
    fcf_t = fcf * (1 + growth_rate) ** t
    discounted = fcf_t / (1 + discount_rate) ** t
    cash_flows.append(discounted)

pv_fcf = sum(cash_flows)

# Terminal value (Gordon Growth Model)
terminal_fcf = fcf * (1 + growth_rate) ** years * (1 + terminal_growth)
terminal_value = terminal_fcf / (discount_rate - terminal_growth)
pv_terminal = terminal_value / (1 + discount_rate) ** years

enterprise_value = pv_fcf + pv_terminal
equity_value = enterprise_value  # assuming no debt for simplicity
intrinsic_value = (equity_value * 1_000_000) / (shares_outstanding * 1_000_000)

# Output
st.header("📈 Valuation Results")

st.metric("Enterprise Value ($M)", f"{enterprise_value:,.2f}")
st.metric("Intrinsic Value per Share ($)", f"{intrinsic_value:,.2f}")

st.write("---")
st.subheader("Projected Cash Flow Breakdown")

for i, cf in enumerate(cash_flows, 1):
    st.write(f"Year {i}: Present Value of FCF = ${cf:,.2f}M")

st.write(f"Terminal Value (PV): ${pv_terminal:,.2f}M")
