import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

# --- PAGE CONFIG ---
st.set_page_config(page_title="Jaffle Shop Dashboard", layout="wide")
st.title("Jaffle Shop Sales Dashboard - 2019")


# --- LOAD DATABASE VARIABLES ---
try:
    DB_USER = st.secrets.get("DB_USER")
    DB_PASSWORD = st.secrets.get("DB_PASS")
    DB_HOST = st.secrets.get("DB_HOST")
    DB_PORT = st.secrets.get("DB_PORT", "5432")
    DB_NAME = st.secrets.get("DB_NAME")
except st.errors.StreamlitSecretNotFoundError:
    # fallback to .env if no secrets.toml exists
    load_dotenv()
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME")

# --- DATABASE CONNECTION ---
engine = create_engine(
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
    connect_args={"sslmode": "require"}
)

# --- LOAD DATA ---
monthly_df = pd.read_sql("SELECT * FROM analytics.analytics_monthly_metrics", engine)
product_df = pd.read_sql("SELECT * FROM analytics.analytics_product_metrics", engine)

# --- STORE FILTER IN SIDEBAR ---
with st.sidebar:
    store_options = ["All"] + sorted(product_df["store_name"].unique().tolist())
    selected_stores = st.selectbox("🏬 Select store", store_options)

if selected_stores != "All":
    monthly_df = monthly_df[monthly_df["store_name"] == selected_stores]
    product_df = product_df[product_df["store_name"] == selected_stores]

# --- KPIs ---
total_revenue = monthly_df["revenue"].sum()
total_orders = monthly_df["number_of_orders"].sum()

col1, col2 = st.columns(2)
col1.metric("💰 Total Revenue", f"${total_revenue:,.2f}")
col2.metric("🙋‍♂️ Total Orders", f"{total_orders:,}")

# --- PRODUCT TABLE ---
st.subheader("Product Performance")
product_table = product_df[["product_name", "product_type", "number_sold", "product_revenue"]].copy()

if selected_stores == "All":
    product_table = product_table.groupby(
        ["product_name", "product_type"], as_index=False
    ).agg(
        number_sold=("number_sold", "sum"),
        product_revenue=("product_revenue", "sum")
    )

# Rename column names in product_table
product_table = product_table.rename(columns={
    "product_name": "Product Name",
    "product_type": "Product Type",
    "number_sold": "Units Sold",
    "product_revenue": "Revenue $"
})

st.dataframe(
    product_table.sort_values("Units Sold", ascending=False).reset_index(drop=True),
    use_container_width=False,
    width=800,
    hide_index=True
)

# --- MONTHLY CHARTS ---
monthly_df["year_month"] = pd.to_datetime(monthly_df["year_month"], format="%Y-%m")
monthly_plot_df = monthly_df.copy()

if selected_stores == "All":
    monthly_plot_df = monthly_plot_df.groupby("year_month", as_index=False).agg(
        revenue=("revenue", "sum"),
        number_of_orders=("number_of_orders", "sum")
    )

monthly_plot_df = monthly_plot_df.sort_values("year_month")

# Revenue chart
fig_revenue = px.line(
    monthly_plot_df,
    x="year_month",
    y="revenue",
    title="Revenue by Month",
    markers=True
)
fig_revenue.update_traces(marker=dict(size=10, color='green'), line=dict(color='green'))
fig_revenue.update_traces(mode="lines+markers+text", text=[f"${v:,.0f}" for v in monthly_plot_df["revenue"]], textposition="top center")
fig_revenue.update_layout(xaxis_title="Month", yaxis_title="Revenue ($)", yaxis=dict(rangemode="tozero"), title_font=dict(size=26),)
st.plotly_chart(fig_revenue, use_container_width=True)

# Orders chart
fig_orders = px.line(
    monthly_plot_df,
    x="year_month",
    y="number_of_orders",
    title="Orders by Month",
    markers=True
)
fig_orders.update_traces(marker=dict(size=10, color='orange'), line=dict(color='orange'))
fig_orders.update_traces(mode="lines+markers+text", text=[f"{v:,}" for v in monthly_plot_df["number_of_orders"]], textposition="top center")
fig_orders.update_layout(xaxis_title="Month", yaxis_title="Number of Orders", yaxis=dict(rangemode="tozero"), title_font=dict(size=26),)
st.plotly_chart(fig_orders, use_container_width=True)
