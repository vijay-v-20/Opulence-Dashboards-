import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# --- Page Config ---
st.set_page_config(page_title="Financial Modeling Dashboard", layout="wide")

# --- Load CSS ---
def load_css(filename):
    css_path = Path(__file__).parent / filename
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css("style.css")

# --- Top Navbar ---
st.markdown('<div class="navbar">📊 Financial Modeling & KPI Dashboard</div>', unsafe_allow_html=True)

# --- Load Excel Data ---
excel_path = Path(__file__).parent / "FinM.xlsx"
df = pd.read_excel(excel_path, sheet_name="Sheet1")
df = df.dropna(how="all")

# --- Sidebar Filters ---
st.sidebar.header("🔍 Filters")

filters = ["KRA", "Analyst", "Activity Name", "Frequency", "Status"]
for field in filters:
    if field in df.columns:
        unique_vals = sorted(df[field].dropna().unique())
        all_selected = st.sidebar.checkbox(f"Select all {field}", value=True, key=field)
        selected_vals = unique_vals if all_selected else st.sidebar.multiselect(field, unique_vals, default=unique_vals)
        df = df[df[field].isin(selected_vals)]

# Ensure proper formats
df["Period"] = pd.to_datetime(df["Period"], errors="coerce")
df["Actual Value"] = pd.to_numeric(df["Actual Value"], errors="coerce")

# --- Tabs ---
tabs = st.tabs([
    "📊 Overview", "📌 KRA Explorer", "👤 Analyst Dashboard", "🧮 KPI Metrics",
    "📅 Frequency View", "⚖️ Compare Dimensions", "🧾 Model Types Summary",
    "🎯 Target Analysis", "📂 Metrics Breakdown", "🔍 Status Heatmap",
    "📁 Documentation Activity", "🏆 Analyst Leaderboard", "📈 KRA Leaderboard",
    "🔄 KPI Comparison", "📋 Raw Data"
])

# --- Tab 0: Overview ---
with tabs[0]:
    st.subheader("📊 Summary Metrics")
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Records", len(df))
    c2.metric("Unique Activities", df["Activity Name"].nunique())
    c3.metric("Total Analysts", df["Analyst"].nunique())

    st.subheader("📌 KPI Distributions")
    col1, col2 = st.columns(2)
    col1.plotly_chart(px.pie(df, names="KRA", title="KRA Distribution"), use_container_width=True)
    col2.plotly_chart(px.pie(df, names="Status", title="KPI Status Breakdown"), use_container_width=True)

# --- Tab 1: KRA Explorer ---
with tabs[1]:
    st.subheader("📌 Activities per KRA")
    chart = df.groupby(["KRA", "Status"]).size().reset_index(name="Count")
    fig = px.bar(chart, x="KRA", y="Count", color="Status", barmode="stack")
    st.plotly_chart(fig, use_container_width=True)

# --- Tab 2: Analyst Dashboard ---
    
with tabs[2]:
    st.subheader("👤 Analyst Performance")
    chart = df.groupby(["Analyst", "Status"]).size().reset_index(name="Count")
    bar_fig = px.bar(chart, x="Analyst", y="Count", color="Status", barmode="group")
    line_fig = px.line(chart, x="Analyst", y="Count", color="Status", markers=True)
    st.plotly_chart(bar_fig, use_container_width=True, key="analyst_bar")
    st.plotly_chart(line_fig, use_container_width=True, key="analyst_line")


# --- Tab 3: KPI Metrics (Enhanced Visuals) ---
with tabs[3]:
    st.subheader("🧮 KPI Trends and Activity Breakdown")
    df_grouped = df.groupby(["Period", "KRA"]).agg({"Actual Value": "mean"}).reset_index()

    bar_fig = go.Figure()
    for kra in df_grouped["KRA"].unique():
        temp_df = df_grouped[df_grouped["KRA"] == kra]
        bar_fig.add_trace(go.Bar(x=temp_df["Period"], y=temp_df["Actual Value"], name=f"{kra} (Bar)"))
        bar_fig.add_trace(go.Scatter(x=temp_df["Period"], y=temp_df["Actual Value"], mode='lines+markers', name=f"{kra} (Line)"))

    bar_fig.update_layout(title="KRA-wise KPI Performance Over Time", barmode='group')
    st.plotly_chart(bar_fig, use_container_width=True)

# --- Tab 4: Frequency View ---
with tabs[4]:
    st.subheader("📅 Frequency Distribution")
    freq = df["Frequency"].value_counts().reset_index()
    freq.columns = ["Frequency", "Count"]
    fig = px.bar(freq, x="Frequency", y="Count", text="Count")
    st.plotly_chart(fig, use_container_width=True)

# --- Tab 5: Compare Dimensions ---
with tabs[5]:
    st.subheader("⚖️ Compare KPI Performance")
    dimension = st.selectbox("Select Dimension to Compare", ["KRA", "Analyst", "Frequency"])
    comp = df.groupby([dimension, "Status"]).size().reset_index(name="Count")
    fig = px.bar(comp, x=dimension, y="Count", color="Status", barmode="group")
    st.plotly_chart(fig, use_container_width=True)

# --- Tab 6: Model Types Summary ---
with tabs[6]:
    st.subheader("🧾 KPIs by Model Type")
    chart = df["Model Type"].value_counts().reset_index()
    chart.columns = ["Model Type", "Count"]
    fig = px.bar(chart, x="Model Type", y="Count", text="Count")
    st.plotly_chart(fig, use_container_width=True)

# --- Tab 7: Target Analysis ---
with tabs[7]:
    st.subheader("🎯 Target Value Distribution")
    st.plotly_chart(px.box(df, x="Status", y="Actual Value", color="Status"), use_container_width=True)

# --- Tab 8: Metrics Breakdown ---
with tabs[8]:
    st.subheader("📂 Metrics Used Across KPIs")
    chart = df["Metrics"].value_counts().reset_index()
    chart.columns = ["Metric", "Count"]
    fig = px.bar(chart, x="Metric", y="Count", text="Count")
    st.plotly_chart(fig, use_container_width=True)

# --- Tab 9: Status Heatmap (Updated) ---
with tabs[9]:
    st.subheader("🔍 Status Heatmap by KRA")
    heat_data = df.groupby(["KRA", "Status"]).size().unstack().fillna(0)
    fig = px.imshow(heat_data, text_auto=True, color_continuous_scale='Blues')
    st.plotly_chart(fig, use_container_width=True)

# --- Tab 10: Documentation Activity (Updated) ---
with tabs[10]:
    st.subheader("📁 Documentation KPIs")
    doc_df = df[df["Frequency"].str.contains("deck|deal|model", case=False, na=False)]
    doc_chart = doc_df["Model Type"].value_counts().reset_index()
    doc_chart.columns = ["Document Type", "Count"]
    fig = px.bar(doc_chart, x="Document Type", y="Count", text="Count")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(doc_df, use_container_width=True)

# --- Tab 11: Analyst Leaderboard ---
with tabs[11]:
    st.subheader("🏆 Analyst Leaderboard")
    board = df.groupby("Analyst").agg({"Activity Name": "count"}).reset_index()
    board.columns = ["Analyst", "Total KPIs"]
    st.dataframe(board.sort_values("Total KPIs", ascending=False), use_container_width=True)

# --- Tab 12: KRA Leaderboard ---
with tabs[12]:
    st.subheader("📈 KRA Success Leaderboard")
    success = df[df["Status"].isin(["Met", "Exceeded"])]
    score = success.groupby("KRA").size() / df.groupby("KRA").size() * 100
    score = score.reset_index(name="% Success")
    st.dataframe(score.sort_values("% Success", ascending=False), use_container_width=True)

# --- Tab 13: KPI Comparison ---
with tabs[13]:
    st.subheader("🔄 Compare Two Analysts")
    options = df["Analyst"].dropna().unique()
    col1, col2 = st.columns(2)
    a1 = col1.selectbox("Select Analyst A", options)
    a2 = col2.selectbox("Select Analyst B", options, index=1 if len(options) > 1 else 0)
    subset = df[df["Analyst"].isin([a1, a2])]
    fig = px.bar(subset, x="Activity Name", y="Actual Value", color="Analyst", barmode="group")
    st.plotly_chart(fig, use_container_width=True)

# --- Tab 14: Raw Data ---
with tabs[14]:
    st.subheader("📋 Complete Dataset")
    st.dataframe(df, use_container_width=True)
    st.download_button("⬇️ Download Filtered Data", df.to_csv(index=False), file_name="Filtered_KPIs.csv")
