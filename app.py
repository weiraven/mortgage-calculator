import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import math

st.set_page_config(page_title="Streamlit - Mortgage Calculator")
st.title("Mortgage Payment Calculator")

st.write("### Input Data")
col1, col2 = st.columns(2)
home_value = col1.number_input("Home Value", min_value=0, value=450000)
downpayment = col1.number_input("Down Payment", min_value=0, value=50000)
interest_rate = col2.number_input("Interest Rate %", min_value=0.0, max_value=100.0, value=6.0)
loan_term = col2.number_input("Loan Term (Years)", min_value=1, value=30)
additional_payment = col1.number_input("Additional Repayment", min_value=0.0, value=0.0, help="Optional supplementary monthly payment")

st.write("### Additional Monthly Costs")
use_breakdown = st.checkbox("Enter cost breakdown", value=True)

if use_breakdown:
    col3, col4 = st.columns(2)
    property_tax = col3.number_input("Property Tax", min_value=0.0, value=300.0)
    home_insurance = col3.number_input("Home Insurance", min_value=0.0, value=150.0)
    pmi = col4.number_input("Private Mortgage Insurance (PMI)", min_value=0.0, value=50.0)
    hoa_fees = col4.number_input("HOA Fees", min_value=0.0, value=100.0)
    total_monthly_costs = property_tax + home_insurance + pmi + hoa_fees
else:
    total_monthly_costs = st.number_input("Total Monthly Costs", min_value=0.0, value=600.0)
    property_tax = home_insurance = pmi = hoa_fees = 0.0

min_down = home_value * 0.03
if downpayment < min_down:
    st.error(f"Down payment must be at least 3% of home value (${min_down:,.2f})")
    st.stop()

# Calculations
loan_amount = home_value - downpayment
monthly_interest_rate = (interest_rate / 100) / 12
number_of_payments = loan_term * 12
monthly_payment = (
    loan_amount * (monthly_interest_rate * (1 + monthly_interest_rate) ** number_of_payments) /
    ((1 + monthly_interest_rate) ** number_of_payments - 1)
)

theoretical_total_interest = (monthly_payment * number_of_payments) - loan_amount

total_monthly_payment = monthly_payment + total_monthly_costs + additional_payment
actual_monthly_payment = monthly_payment + additional_payment

schedule = []
remaining_balance = loan_amount
base_monthly_payment = monthly_payment

for i in range(1, number_of_payments + 1):
    interest_payment = remaining_balance * monthly_interest_rate
    principal_payment = base_monthly_payment - interest_payment

    if additional_payment > 0:
        principal_payment += additional_payment

    if remaining_balance < principal_payment:
        principal_payment = remaining_balance
        interest_payment = remaining_balance * monthly_interest_rate
        monthly_payment = principal_payment + interest_payment
    else:
        monthly_payment = base_monthly_payment + (additional_payment if additional_payment > 0 else 0)
    
    remaining_balance -= principal_payment
    year = math.ceil(i/12)
    schedule.append(
        [
            i,
            monthly_payment,
            principal_payment,
            interest_payment,
            remaining_balance,
            year,
        ]     
    )

    if remaining_balance <= 0:
        break

total_payments = sum(payment[1] for payment in schedule)
total_interest = sum(payment[3] for payment in schedule)
total_cost = total_payments + (total_monthly_costs * len(schedule))

original_term_months = number_of_payments
actual_term_months = len(schedule)
months_saved = original_term_months - actual_term_months
interest_saved = theoretical_total_interest - total_interest

st.write("### Projected Payments")
col1, col2, col3 = st.columns(3)
col1.metric(label="Monthly Principal & Interest", value=f"${actual_monthly_payment:,.2f}")
col2.metric(label="Total Monthly Payment", value=f"${total_monthly_payment:,.2f}")
col3.metric(label="Total Interest", value=f"${total_interest:,.2f}")

if additional_payment > 0:
    st.write(f"### Impact of Additional ${additional_payment:,.2f} per Month")
    col1, col2 = st.columns(2)
    col1.metric(label="Months Saved", value=f"{months_saved:,.0f}")
    col2.metric(label="Interest Saved", value=f"${interest_saved:,.2f}")

st.write("### Monthly Payment Breakdown")
if use_breakdown:
    components = ['Principal & Interest', 'Property Tax', 'Home Insurance', 'PMI', 'HOA Fees']
    amounts = [actual_monthly_payment, property_tax, home_insurance, pmi, hoa_fees]
else:
    components = ['Principal & Interest', 'Other Monthly Costs']
    amounts = [actual_monthly_payment, total_monthly_costs]

payment_breakdown = pd.DataFrame({
    'Component': components, 
    'Amount': amounts
    })
payment_breakdown['Percentage'] = payment_breakdown['Amount'] / total_monthly_payment * 100

st.dataframe(payment_breakdown.style.format({
    'Amount': '${:.2f}',
    'Percentage': '{:.1f}%'
}))

df = pd.DataFrame(
    schedule,
    columns=[
        "Month",
        "Payment",
        "Principal",
        "Interest",
        "Remaining Balance",
        "Year"
    ],
)

st.write("### Loan Balance Over Time")
payments_df = df[["Year", "Remaining Balance"]].groupby("Year").min()
payments_df = payments_df.apply(lambda x: round(x, 2))
st.line_chart(payments_df)

st.markdown(
    """
    💡 Feedback? Contact [weiraven](https://github.com/weiraven)\n
    🚀 Built with [Streamlit](https://streamlit.io) following tutorial by [pixegami](https://www.youtube.com/watch?v=D0D4Pa22iG0)
    """
)