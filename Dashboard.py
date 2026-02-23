import streamlit as st
import pandas as pd
import numpy as np

# ============================================
# CONFIG
# ============================================

st.set_page_config(
    page_title="AWB Weight Reconciliation",
    layout="wide"
)

# Google Sheets CSV (лист "Общая сводная")
GOOGLE_SHEET_CSV = "https://docs.google.com/spreadsheets/d/1FRvs6hAsoH8GyuSruRbGHicZKXUyzI8D8Mko5L2IeQQ/export?format=csv&gid=1284074899"

# Если используешь отдельный sheet для dashboard_data — поменяй ссылку

# ============================================
# LOAD DATA
# ============================================

@st.cache_data(ttl=300)
def load_data():

    try:
        df = pd.read_csv(GOOGLE_SHEET_CSV)

        # ожидаемые колонки после работы agent.py:
        # awb, parcel_net, box_weight, gross_weight, calculated_total, difference

        # если данные из agent.csv — просто читаем
        if "awb" in df.columns:
            return df

        # fallback если читаем raw Google Sheet
        df = df.iloc[:, [2, 6]]
        df.columns = ["awb", "gross_weight"]

        df["awb"] = df["awb"].astype(str)
        df["gross_weight"] = pd.to_numeric(df["gross_weight"], errors="coerce")

        return df

    except Exception as e:

        st.error("Ошибка загрузки данных")
        st.exception(e)

        return pd.DataFrame()

# ============================================
# STATUS CALCULATION
# ============================================

def calculate_status(row):

    if "difference_percent" not in row:
        return "NO DATA"

    x = row["difference_percent"]

    if pd.isna(x):
        return "NO DATA"

    if abs(x) <= 1:
        return "OK"

    elif abs(x) <= 3:
        return "WARNING"

    else:
        return "ERROR"

# ============================================
# MAIN
# ============================================

st.title("📦 AWB Weight Reconciliation Dashboard")

df = load_data()

if df.empty:

    st.warning("Нет данных")

    st.stop()

# Calculate difference_percent if missing
if "difference_percent" not in df.columns and "difference" in df.columns:

    df["difference_percent"] = (
        df["difference"] /
        df["gross_weight"] * 100
    ).round(2)

# Add status
if "status" not in df.columns:

    df["status"] = df.apply(calculate_status, axis=1)

# ============================================
# KPI BLOCK
# ============================================

col1, col2, col3, col4 = st.columns(4)

total_awb = len(df)

errors = len(df[df["status"] == "ERROR"])

warnings = len(df[df["status"] == "WARNING"])

ok = len(df[df["status"] == "OK"])

col1.metric("Total AWB", total_awb)
col2.metric("OK", ok)
col3.metric("Warnings", warnings)
col4.metric("Errors", errors)

# ============================================
# FILTER
# ============================================

st.divider()

col1, col2 = st.columns(2)

awb_filter = col1.text_input("Filter by AWB")

status_filter = col2.selectbox(
    "Filter by Status",
    ["ALL", "OK", "WARNING", "ERROR"]
)

filtered_df = df.copy()

if awb_filter:

    filtered_df = filtered_df[
        filtered_df["awb"].astype(str).str.contains(awb_filter)
    ]

if status_filter != "ALL":

    filtered_df = filtered_df[
        filtered_df["status"] == status_filter
    ]

# ============================================
# FORMAT
# ============================================

display_columns = []

for col in [
    "awb",
    "parcel_net",
    "box_weight",
    "gross_weight",
    "calculated_total",
    "difference",
    "difference_percent",
    "status"
]:
    if col in filtered_df.columns:
        display_columns.append(col)

# ============================================
# TABLE
# ============================================

st.subheader("AWB Summary")

st.dataframe(
    filtered_df[display_columns],
    use_container_width=True,
    height=600
)

# ============================================
# ERROR TABLE
# ============================================

st.subheader("Errors Only")

errors_df = df[df["status"] == "ERROR"]

st.dataframe(
    errors_df,
    use_container_width=True
)

# ============================================
# AUTO REFRESH INFO
# ============================================

st.caption("Auto refresh every 5 minutes")
