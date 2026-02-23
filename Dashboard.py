import streamlit as st
import pandas as pd

# CSV URL Dashboard_Data sheet
DATA_URL = "https://docs.google.com/spreadsheets/d/1FRvs6hAsoH8GyuSruRbGHicZKXUyzI8D8Mko5L2IeQQ/export?format=csv&gid=1284074899"

st.set_page_config(
    page_title="UZUM Weight Dashboard",
    layout="wide"
)

st.title("UZUM Crossborder Weight Reconciliation Dashboard")

# auto refresh cache every 60 seconds
@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv(DATA_URL)
    return df

df = load_data()

# KPI
col1, col2, col3 = st.columns(3)

col1.metric("Total AWB", len(df))

col2.metric(
    "Errors",
    len(df[df["difference_percent"].abs() > 3])
)

col3.metric(
    "Warnings",
    len(df[
        (df["difference_percent"].abs() > 1) &
        (df["difference_percent"].abs() <= 3)
    ])
)

st.divider()

# table
st.dataframe(
    df.sort_values("difference_percent", ascending=False),
    use_container_width=True
)
