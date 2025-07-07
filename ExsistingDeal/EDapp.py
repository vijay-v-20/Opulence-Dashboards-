import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# --- Page Config ---
st.set_page_config(page_title="E-Deal Advanced Dashboard", layout="wide")

# --- Load CSS ---
def load_css(filename):
    css_path = Path(__file__).parent / filename
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css("style.css")

# --- Top Navbar ---
st.markdown('<div class="navbar">💼 E-Deal Advanced Dashboard</div>', unsafe_allow_html=True)

# --- Load Excel Data ---
excel_path = Path(__file__).parent / "EDeal.xlsx"
df = pd.read_excel(excel_path)
df = df.dropna(how="all")

# --- Sidebar Filters (Updated style from FinMod) ---
st.sidebar.header("🔍 Filters")
filters = ["ANALYST", "DEAL_PRIORITY", "STATUS", "COMPANY_SECTOR", "INVESTOR_TYPE", "DUE_DILIGENCE_STATUS", "DEAL_STAGE"]
for field in filters:
    if field in df.columns:
        unique_vals = sorted(df[field].dropna().unique())
        all_selected = st.sidebar.checkbox(f"Select all {field}", value=True, key=field)
        selected_vals = unique_vals if all_selected else st.sidebar.multiselect(field, unique_vals, default=unique_vals)
        df = df[df[field].isin(selected_vals)]

# --- The rest of the dashboard code remains unchanged ---

# Ensure proper formats
if "DATE" in df.columns:
    df["DATE"] = pd.to_datetime(df["DATE"], errors="coerce")
if "Actual Value" in df.columns:
    df["Actual Value"] = pd.to_numeric(df["Actual Value"], errors="coerce")

# (Rest of the tabs and charts continue as they were before)
# Tabs: Overview, Analyst, Sector, Trends, Match Score, Mandate & NDA, Strategic Fit, DD vs Investor, Raw Data

# --- Tabs ---
tabs = st.tabs([
    "📊 Overview", "🧩 Priority Breakdown", "👤 Analyst Performance", "🏢 Sector Analysis",
    "📈 Trends Over Time", "🧠 Match Score Analysis", "📂 Mandate & NDA",
    "🧾 Strategic Fit", "🔍 DD vs Investor", "📋 Full Data"
])

# --- Tab 0: Overview ---
with tabs[0]:
    st.subheader("📊 Deal Summary")
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Deals", len(df))
    c2.metric("Unique Analysts", df["ANALYST"].nunique())
    total_val = df["DEAL_VALUE_ESTIMATE"].sum() if "DEAL_VALUE_ESTIMATE" in df else 0
    c3.metric("Total Deal Value", f"${total_val:,.0f}")

    col1, col2 = st.columns(2)
    if "STATUS" in df.columns:
        col1.plotly_chart(px.pie(df, names="STATUS", title="Status Distribution"), use_container_width=True)
    if "DEAL_STAGE" in df.columns:
        col2.plotly_chart(px.pie(df, names="DEAL_STAGE", title="Deal Stage"), use_container_width=True)

# --- Tab 1: Priority Pie ---
with tabs[1]:
    st.subheader("🧩 Priority-wise Deal Split")
    if "DEAL_PRIORITY" in df.columns:
        fig = px.pie(df, names="DEAL_PRIORITY", title="Deal Distribution by Priority")
        st.plotly_chart(fig, use_container_width=True)

# --- Tab 2: Analyst View ---
with tabs[2]:
    st.subheader("👤 Analyst Activity")
    if {"ANALYST", "STATUS"}.issubset(df.columns):
        count = df.groupby(["ANALYST", "STATUS"]).size().reset_index(name="Deals")
        fig = px.bar(count, x="ANALYST", y="Deals", color="STATUS", barmode="group")
        st.plotly_chart(fig, use_container_width=True)

# --- Tab 3: Sector Analysis ---
with tabs[3]:
    st.subheader("🏢 Sector vs Deal Stage")
    if {"COMPANY_SECTOR", "DEAL_STAGE"}.issubset(df.columns):
        grp = df.groupby(["COMPANY_SECTOR", "DEAL_STAGE"]).size().reset_index(name="Deals")
        fig = px.bar(grp, x="COMPANY_SECTOR", y="Deals", color="DEAL_STAGE", barmode="stack")
        st.plotly_chart(fig, use_container_width=True)

# --- Tab 4: Trends ---
with tabs[4]:
    st.subheader("📈 Deal Progress Over Time")
    if {"DATE", "DEAL_STAGE"}.issubset(df.columns):
        trend = df.groupby(["DATE", "DEAL_STAGE"]).size().reset_index(name="Count")
        fig = px.line(trend, x="DATE", y="Count", color="DEAL_STAGE", markers=True)
        st.plotly_chart(fig, use_container_width=True)

# --- Tab 5: Match Score ---
with tabs[5]:
    st.subheader("🧠 Match Score Distribution")
    if "MATCH_SCORE" in df.columns:
        fig = px.histogram(df, x="MATCH_SCORE", nbins=20, title="Match Score Histogram")
        st.plotly_chart(fig, use_container_width=True)

# --- Tab 6: Mandate & NDA ---
with tabs[6]:
    st.subheader("📂 Mandate Signed vs NDA Status")
    if {"MANDATE_SIGNED", "NDA_SIGNED_STATUS"}.issubset(df.columns):
        grp = df.groupby(["MANDATE_SIGNED", "NDA_SIGNED_STATUS"]).size().reset_index(name="Deals")
        fig = px.sunburst(grp, path=["MANDATE_SIGNED", "NDA_SIGNED_STATUS"], values="Deals")
        st.plotly_chart(fig, use_container_width=True)

# --- Tab 7: Strategic Fit ---
with tabs[7]:
    st.subheader("🧾 Strategic Fit Notes")
    if "STRATEGIC_FIT_NOTES" in df.columns:
        fit = df["STRATEGIC_FIT_NOTES"].value_counts().reset_index()
        fit.columns = ["Fit Note", "Count"]
        fig = px.bar(fit, x="Fit Note", y="Count", text="Count")
        st.plotly_chart(fig, use_container_width=True)

# --- Tab 8: DD vs Investor Type ---
with tabs[8]:
    st.subheader("🔍 Due Diligence by Investor Type")
    if {"DUE_DILIGENCE_STATUS", "INVESTOR_TYPE"}.issubset(df.columns):
        grp = df.groupby(["INVESTOR_TYPE", "DUE_DILIGENCE_STATUS"]).size().reset_index(name="Deals")
        fig = px.bar(grp, x="INVESTOR_TYPE", y="Deals", color="DUE_DILIGENCE_STATUS", barmode="group")
        st.plotly_chart(fig, use_container_width=True)

# --- Tab 9: Raw Data ---
with tabs[9]:
    st.subheader("📋 Complete Filtered Dataset")
    st.dataframe(df, use_container_width=True)
    st.download_button("⬇️ Download Data", df.to_csv(index=False), file_name="Filtered_EDeal_Data.csv")
