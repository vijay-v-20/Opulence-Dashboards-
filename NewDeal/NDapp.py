import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# --- Page Setup ---
st.set_page_config(page_title="Deal Flow Dashboard", layout="wide")

# --- Load Custom CSS ---
def load_css(filename):
    css_path = Path(__file__).parent / filename
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css("style.css")

# --- Header ---
st.markdown('<div class="navbar">💼 Deal Flow & Investor Pipeline Dashboard</div>', unsafe_allow_html=True)

# --- Load Excel Data ---
excel_path = Path(__file__).parent / "ND.xlsx"
df = pd.read_excel(excel_path)
df = df.dropna(how="all")

# --- Format Columns ---
df["Contact Date"] = pd.to_datetime(df["Contact Date"], errors="coerce")
df["Deal Size (₹ Cr)"] = pd.to_numeric(df["Deal Size (₹ Cr)"], errors="coerce")

# --- Sidebar Filters ---
st.sidebar.header("🔍 Filters")
filters = ["Intern Name", "Lead Source", "Sector", "Mapping Status", "Meeting Scheduled", "Deal Stage", "Closure Status", "Term Sheet Status"]

for field in filters:
    if field in df.columns:
        unique_vals = sorted(df[field].dropna().unique())
        all_selected = st.sidebar.checkbox(f"Select all {field}", value=True, key=field)
        selected_vals = unique_vals if all_selected else st.sidebar.multiselect(field, unique_vals, default=unique_vals)
        df = df[df[field].isin(selected_vals)]

# ✅ Only ONE tab definition
tabs = st.tabs([
    "📊 Overview",
    "📈 Deal Stage Trends",
    "👤 Intern Analysis",
    "📅 Contact Timeline",
    "💰 Deal Size Analysis",
    "📋 Raw Data",
    "🧮 Deal Stage Comparison",
    "🏆 Top Intern Leaderboard",
    "🔍 Quality Insights",
    "📤 Investor Engagement",
    "📈 Success Correlation"
])

# --- Tab 0: Overview ---
with tabs[0]:
    st.subheader("📊 Overall Summary")
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Leads", df["Lead ID"].nunique())
    c2.metric("Total Interns", df["Intern Name"].nunique())
    c3.metric("Total Deal Value (Cr)", round(df["Deal Size (₹ Cr)"].sum(), 2))

    col1, col2 = st.columns(2)
    col1.plotly_chart(px.pie(df, names="Closure Status", title="Closure Status Distribution", hole=0.4), use_container_width=True)
    col2.plotly_chart(px.pie(df, names="Deal Stage", title="Deal Stage Breakdown"), use_container_width=True)

# --- Tab 1: Deal Stage Trends ---
with tabs[1]:
    st.subheader("📈 Leads Across Deal Stages")
    stage_counts = df["Deal Stage"].value_counts().reset_index()
    stage_counts.columns = ["Deal Stage", "Count"]
    bar = px.bar(stage_counts, x="Deal Stage", y="Count", text="Count", title="Count of Deals per Stage")
    st.plotly_chart(bar, use_container_width=True)

    funnel = px.funnel(df, x="Deal Stage", title="Deal Funnel by Stage")
    st.plotly_chart(funnel, use_container_width=True)

# --- Tab 2: Intern Analysis ---
with tabs[2]:
    st.subheader("👤 Intern Performance")
    intern_summary = df.groupby("Intern Name").agg({
        "Lead ID": "count",
        "Deal Size (₹ Cr)": "sum"
    }).reset_index().rename(columns={"Lead ID": "Lead Count", "Deal Size (₹ Cr)": "Total Deal Size (₹ Cr)"})

    fig = px.bar(intern_summary, x="Intern Name", y="Lead Count", color="Intern Name", title="Leads per Intern")
    st.plotly_chart(fig, use_container_width=True)

    fig2 = px.bar(intern_summary, x="Intern Name", y="Total Deal Size (₹ Cr)", color="Intern Name", title="Total Deal Value per Intern")
    st.plotly_chart(fig2, use_container_width=True)

# --- Tab 3: Contact Timeline ---
with tabs[3]:
    st.subheader("📅 Contacts Over Time")
    timeline = df.groupby("Contact Date").size().reset_index(name="Leads")
    fig = px.line(timeline, x="Contact Date", y="Leads", title="Leads Over Time", markers=True)
    st.plotly_chart(fig, use_container_width=True)

# --- Tab 4: Deal Size Analysis ---
with tabs[4]:
    st.subheader("💰 Deal Size Distribution")
    fig = px.box(df, x="Sector", y="Deal Size (₹ Cr)", points="all", color="Sector", title="Deal Size by Sector")
    st.plotly_chart(fig, use_container_width=True)

    heat_data = df.pivot_table(index="Sector", columns="Deal Stage", values="Deal Size (₹ Cr)", aggfunc="sum", fill_value=0)
    fig2 = px.imshow(heat_data, text_auto=True, title="Heatmap: Deal Size by Sector and Stage", color_continuous_scale="Blues")
    st.plotly_chart(fig2, use_container_width=True)

# --- Tab 5: Raw Data ---
with tabs[5]:
    st.subheader("📋 Full Dataset")
    st.dataframe(df, use_container_width=True)
    st.download_button("⬇️ Download Filtered Data", df.to_csv(index=False), file_name="Filtered_Deals.csv")

# --- Tab 6: Deal Stage Comparison ---
with tabs[6]:
    st.subheader("🧮 Deal Stage by Intern")
    group = df.groupby(["Intern Name", "Deal Stage"]).size().reset_index(name="Count")
    bar = px.bar(group, x="Intern Name", y="Count", color="Deal Stage", barmode="group", title="Deal Stage Distribution per Intern")
    pie = px.pie(df, names="Deal Stage", title="Overall Deal Stage Share", hole=0.4)
    st.plotly_chart(bar, use_container_width=True)
    st.plotly_chart(pie, use_container_width=True)

# --- Tab 7: Top Intern Leaderboard ---
with tabs[7]:
    st.subheader("🏆 Top Performing Interns")
    leaderboard = df.groupby("Intern Name")["Deal Size (₹ Cr)"].sum().reset_index().sort_values(by="Deal Size (₹ Cr)", ascending=False)
    st.dataframe(leaderboard, use_container_width=True)
    fig = px.bar(leaderboard, x="Intern Name", y="Deal Size (₹ Cr)", title="Total Deal Size by Intern", color="Deal Size (₹ Cr)", color_continuous_scale="Agsunset")
    st.plotly_chart(fig, use_container_width=True)
    top_intern = leaderboard.iloc[0]
    st.metric(label="🏅 Top Intern", value=top_intern["Intern Name"], delta=f"₹ {top_intern['Deal Size (₹ Cr)']:.2f} Cr")

# --- Tab 8: Quality Insights ---
with tabs[8]:
    st.subheader("🔍 Quality Rating vs Deal Metrics")
    heat = df.pivot_table(index="Quality Rating", columns="Closure Status", values="Deal Size (₹ Cr)", aggfunc="sum", fill_value=0)
    fig = px.imshow(heat, text_auto=True, title="Heatmap: Deal Size by Quality Rating & Closure Status")
    st.plotly_chart(fig, use_container_width=True)
    scatter = px.scatter(df, x="Quality Rating", y="Deal Size (₹ Cr)", color="Closure Status", size="Deal Size (₹ Cr)", title="Deal Size vs Quality Rating")
    st.plotly_chart(scatter, use_container_width=True)

# --- Tab 9: Investor Engagement ---
with tabs[9]:
    st.subheader("📤 Investor Outreach vs Warm Leads")
    fig = px.scatter(df, x="Investor Outreach Count", y="Warm Investor Leads", color="Intern Name", size="Deal Size (₹ Cr)", title="Investor Engagement Bubble Chart")
    st.plotly_chart(fig, use_container_width=True)

    outreach_time = df.groupby("Contact Date")["Investor Outreach Count"].sum().reset_index()
    fig2 = px.line(outreach_time, x="Contact Date", y="Investor Outreach Count", markers=True, title="Investor Outreach Over Time")
    st.plotly_chart(fig2, use_container_width=True)

# --- Tab 10: Success Correlation ---
with tabs[10]:
    st.subheader("📈 KPI Correlation Heatmap")
    numeric_cols = ["Deal Size (₹ Cr)", "Investor Outreach Count", "Warm Investor Leads", "Quality Rating"]
    corr_df = df[numeric_cols].corr().round(2)
    fig = px.imshow(corr_df, text_auto=True, color_continuous_scale="Viridis", title="Correlation Between Key Metrics")
    st.plotly_chart(fig, use_container_width=True)
