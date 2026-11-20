import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Nassau Candy Sales Dashboard", page_icon="🍬", layout="wide")
st.title("🍬 Nassau Candy Distributor – Sales Analytics Dashboard")
st.caption("Sales performance, profitability, and shipping-date data-quality review.")

uploaded = st.file_uploader("Upload Nassau Candy Distributor CSV", type=["csv"])
if uploaded is None:
    st.info("Upload your Nassau Candy CSV file to view the dashboard.")
    st.stop()

df = pd.read_csv(uploaded)
df.columns = df.columns.str.strip()
required = ["Sales", "Gross Profit", "Order ID", "Customer ID", "Product Name", "Division", "Region", "Ship Mode", "Order Date", "Ship Date"]
missing = [c for c in required if c not in df.columns]
if missing:
    st.error("Missing required columns: " + ", ".join(missing))
    st.write("Available columns:", list(df.columns))
    st.stop()

for c in ["Sales", "Gross Profit"]:
    df[c] = pd.to_numeric(df[c], errors="coerce")
df["Order Date Parsed"] = pd.to_datetime(df["Order Date"].astype(str).str.strip(), format="%d-%m-%Y", errors="coerce")
df["Ship Date Parsed"] = pd.to_datetime(df["Ship Date"].astype(str).str.strip(), format="%d-%m-%Y", errors="coerce")
df["Shipping Duration (Days)"] = (df["Ship Date Parsed"] - df["Order Date Parsed"]).dt.days

st.sidebar.header("Filters")
regions = sorted(df["Region"].dropna().astype(str).unique())
divisions = sorted(df["Division"].dropna().astype(str).unique())
modes = sorted(df["Ship Mode"].dropna().astype(str).unique())
rsel = st.sidebar.multiselect("Region", regions, default=regions)
dsel = st.sidebar.multiselect("Division", divisions, default=divisions)
msel = st.sidebar.multiselect("Ship Mode", modes, default=modes)
d = df[df["Region"].astype(str).isin(rsel) & df["Division"].astype(str).isin(dsel) & df["Ship Mode"].astype(str).isin(msel)].copy()

sales = d["Sales"].sum()
profit = d["Gross Profit"].sum()
margin = profit/sales*100 if sales else np.nan
k1,k2,k3,k4,k5 = st.columns(5)
k1.metric("Total Sales", f"{sales:,.2f}")
k2.metric("Gross Profit", f"{profit:,.2f}")
k3.metric("Profit Margin", f"{margin:.2f}%" if pd.notna(margin) else "N/A")
k4.metric("Orders", f"{d['Order ID'].nunique():,}")
k5.metric("Customers", f"{d['Customer ID'].nunique():,}")

t1,t2,t3,t4,t5 = st.tabs(["Sales","Profitability","Products & Customers","Shipping Data Quality","Data Preview"])
with t1:
    st.subheader("Sales by Division")
    vals=d.groupby("Division")["Sales"].sum().sort_values(ascending=False)
    fig,ax=plt.subplots(figsize=(8,4)); sns.barplot(x=vals.index,y=vals.values,ax=ax); ax.set_ylabel("Sales"); st.pyplot(fig); plt.close(fig)
    st.subheader("Sales by Region")
    vals=d.groupby("Region")["Sales"].sum().sort_values(ascending=False)
    fig,ax=plt.subplots(figsize=(8,4)); sns.barplot(x=vals.index,y=vals.values,ax=ax); ax.set_ylabel("Sales"); st.pyplot(fig); plt.close(fig)
    valid=d.dropna(subset=["Order Date Parsed"])
    if not valid.empty:
        vals=valid.groupby(valid["Order Date Parsed"].dt.to_period("M"))["Sales"].sum()
        vals.index=vals.index.astype(str)
        st.subheader("Monthly Sales Trend")
        fig,ax=plt.subplots(figsize=(11,4)); ax.plot(vals.index,vals.values,marker="o"); ax.tick_params(axis="x",rotation=45); ax.grid(True); fig.tight_layout(); st.pyplot(fig); plt.close(fig)
with t2:
    for title, grouping in [("Gross Profit by Region","Region"),("Gross Profit by Division","Division")]:
        st.subheader(title); vals=d.groupby(grouping)["Gross Profit"].sum().sort_values(ascending=False)
        fig,ax=plt.subplots(figsize=(8,4)); sns.barplot(x=vals.index,y=vals.values,ax=ax); ax.set_ylabel("Gross Profit"); st.pyplot(fig); plt.close(fig)
    valid=d.dropna(subset=["Order Date Parsed"])
    if not valid.empty:
        vals=valid.groupby(valid["Order Date Parsed"].dt.to_period("M"))["Gross Profit"].sum(); vals.index=vals.index.astype(str)
        st.subheader("Monthly Gross Profit Trend")
        fig,ax=plt.subplots(figsize=(11,4)); ax.plot(vals.index,vals.values,marker="o"); ax.tick_params(axis="x",rotation=45); ax.grid(True); fig.tight_layout(); st.pyplot(fig); plt.close(fig)
with t3:
    st.subheader("Top 10 Products by Sales")
    vals=d.groupby("Product Name")["Sales"].sum().sort_values(ascending=False).head(10)
    fig,ax=plt.subplots(figsize=(9,5)); sns.barplot(x=vals.values,y=vals.index,ax=ax); st.pyplot(fig); plt.close(fig)
    st.dataframe(vals.rename("Sales").reset_index(),use_container_width=True)
    st.subheader("Top 10 Customers by Sales")
    vals=d.groupby("Customer ID")["Sales"].sum().sort_values(ascending=False).head(10)
    st.dataframe(vals.rename("Sales").reset_index(),use_container_width=True)
with t4:
    st.warning("Data-quality investigation only. Do not interpret calculated durations as actual delivery performance until source dates are validated.")
    duration=d["Shipping Duration (Days)"]
    st.write("Invalid order dates:",int(d["Order Date Parsed"].isna().sum()))
    st.write("Invalid ship dates:",int(d["Ship Date Parsed"].isna().sum()))
    st.write("Negative durations:",int((duration<0).sum()))
    st.write("Zero durations:",int((duration==0).sum()))
    st.write("Durations > 90 days:",int((duration>90).sum()))
    st.subheader("Duration summary (days)")
    st.dataframe(duration.describe().to_frame().T)
    if duration.notna().any():
        fig,ax=plt.subplots(figsize=(9,4)); sns.histplot(duration.dropna(),bins=30,ax=ax); ax.set_xlabel("Shipping duration (days)"); st.pyplot(fig); plt.close(fig)
    st.caption("Validate raw source dates before making logistics recommendations.")
with t5:
    st.write(f"Filtered records: {len(d):,}")
    st.dataframe(d.head(100),use_container_width=True)
    st.download_button("Download filtered CSV",d.to_csv(index=False).encode("utf-8"),"nassau_candy_filtered.csv","text/csv")
st.caption("Portfolio project by Sanskar Kasar | Python • Pandas • NumPy • Matplotlib • Seaborn • Streamlit")
