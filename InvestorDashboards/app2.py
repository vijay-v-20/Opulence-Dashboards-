import streamlit as st
import pandas as pd
import plotly.express as px

# Load data
from pathlib import Path
excel_path = Path(__file__).parent / "InvetorDashboard.xlsx"
df = pd.read_excel(excel_path)


df = df.dropna(how='all')  # drop blank rows

st.set_page_config(layout="wide")

# Apply large font and graph style globally
st.markdown("""
<style>
    .stTabs [data-baseweb="tab"] {
        font-size: 20px !important;
        padding: 12px !important;
    }
    .stPlotlyChart, .stAltairChart {
        height: 600px !important;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar filters
st.sidebar.header("🔍 Filter Investors")

# ✅ Improved multi-select filter with Select All checkbox
def dropdown_filter(label, col_data):
    unique_vals = sorted([opt for opt in col_data.unique() if pd.notna(opt)])
    all_selected = st.sidebar.checkbox(f"Select all for {label}", value=True)
    if all_selected:
        return unique_vals
    else:
        choice = st.sidebar.multiselect(label, unique_vals)
        return choice if choice else unique_vals

# Filters
poc_filter = dropdown_filter("Point of Contact", df["Point of Contact"])
designation_filter = dropdown_filter("Designation", df["Designation"])
sector_filter = dropdown_filter("Sector Interest", df["Sector Interest"])
ticket_filter = dropdown_filter("Ticket Size", df["Ticket Size"])
stage_filter = dropdown_filter("Investment Stage", df["Investment Stage"])
source_filter = dropdown_filter("Source of Capital", df["Source of Capital"])
strategy_filter = dropdown_filter("Investment Strategy", df["Investment Strategy"])
geo_filter = dropdown_filter("Geography", df["Geography"])
market_filter = dropdown_filter("Market Type", df["Market Type"])

# Apply filters
df_filtered = df[
    df["Point of Contact"].isin(poc_filter) &
    df["Designation"].isin(designation_filter) &
    df["Sector Interest"].isin(sector_filter) &
    df["Ticket Size"].isin(ticket_filter) &
    df["Investment Stage"].isin(stage_filter) &
    df["Source of Capital"].isin(source_filter) &
    df["Investment Strategy"].isin(strategy_filter) &
    df["Geography"].isin(geo_filter) &
    df["Market Type"].isin(market_filter)
]

# Dashboard Tabs
st.title("💼 Investor Dashboard")
tabs = st.tabs([
    "🏠 Home", "📈 Sector Analysis", "💰 Ticket Size", "📋 Strategy", "👥 Intern Tracker", 
    "🌍 Geography", "📇 Contact Sheet", "📌 Top Investors", "🔗 Strategy Matrix",
    "📊 Sector vs Strategy", "🧭 Stage vs Geography", "💼 Intern vs Investment Stage", "🏢 Designation vs Source of Capital"
])

# Home Tab
with tabs[0]:
    st.subheader("📊 Overview")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Investors", len(df_filtered))
    c2.metric("Unique Sectors", df_filtered['Sector Interest'].nunique())
    c3.metric("Total POCs", df_filtered['Point of Contact'].nunique())
    c4.metric("Top Stage", df_filtered['Investment Stage'].mode()[0] if not df_filtered['Investment Stage'].isna().all() else "N/A")

    st.plotly_chart(px.bar(df_filtered, x='Sector Interest', title='Investor Count by Sector'))
    st.plotly_chart(px.pie(df_filtered, names='Geography', title='Geography Distribution'))
    st.plotly_chart(px.treemap(df_filtered, path=['Investment Strategy', 'Investment Stage'], title='Strategy vs Stage'))

# Sector Analysis
with tabs[1]:
    st.subheader("📈 Sector Analysis")
    st.plotly_chart(px.histogram(df_filtered, x='Sector Interest', color='Investment Stage', barmode='group'))

# Ticket Size
with tabs[2]:
    st.subheader("💰 Ticket Size Analysis")
    st.plotly_chart(px.histogram(df_filtered, x='Ticket Size', title='Ticket Size Distribution'))
    st.plotly_chart(px.histogram(df_filtered, x='Investment Stage', color='Ticket Size', title='Stage vs Ticket Size'))

# Strategy
with tabs[3]:
    st.subheader("📋 Strategy and Source")
    st.plotly_chart(px.bar(df_filtered, x='Investment Strategy', title='Investment Strategy Count'))
    st.plotly_chart(px.sunburst(df_filtered, path=['Source of Capital', 'Investment Strategy'], title='Source vs Strategy'))

# Intern Tracker
with tabs[4]:
    st.subheader("👥 Intern Tracker")
    intern_data = df_filtered['Point of Contact'].value_counts().reset_index()
    intern_data.columns = ['Point of Contact', 'Investor Count']
    st.plotly_chart(px.bar(intern_data, x='Point of Contact', y='Investor Count', title='Investors per Intern'))
    st.dataframe(df_filtered[['Company name', 'Investor Name', 'Point of Contact']])

# Geography
with tabs[5]:
    st.subheader("🌍 Investor Geography")
    st.plotly_chart(px.bar(df_filtered, x='Geography', title='Investors by Geography'))

# Contact Sheet
with tabs[6]:
    st.subheader("📇 Contact Sheet")
    st.dataframe(df_filtered[['Company name', 'Investor Name', 'Designation', 'Linkedin ID', 'Email Id', 'Phone No.']])
    st.download_button("Download CSV", df_filtered.to_csv(index=False), file_name='Filtered_Investors.csv')

# Top Investors
with tabs[7]:
    st.subheader("📌 Top Investors by Ticket Size")
    top_investors = df_filtered[~df_filtered['Ticket Size'].isna()]
    top_investors = top_investors.sort_values(by='Ticket Size', ascending=False)
    st.dataframe(top_investors[['Investor Name', 'Company name', 'Ticket Size', 'Investment Stage', 'Sector Interest']].head(10))

# Strategy Matrix
with tabs[8]:
    st.subheader("🔗 Strategy Matrix: Stage vs Strategy")
    matrix_data = df_filtered.pivot_table(index='Investment Strategy', columns='Investment Stage', aggfunc='size', fill_value=0)
    st.dataframe(matrix_data.style.background_gradient(cmap='Blues'))

# Sector vs Strategy
with tabs[9]:
    st.subheader("📊 Sector vs Investment Strategy")
    sector_strategy = df_filtered.groupby(['Sector Interest', 'Investment Strategy']).size().reset_index(name='Count')
    st.plotly_chart(px.density_heatmap(sector_strategy, x='Sector Interest', y='Investment Strategy', z='Count', color_continuous_scale='Plasma'))

# Stage vs Geography
with tabs[10]:
    st.subheader("🧭 Investment Stage vs Geography")
    stage_geo = df_filtered.groupby(['Investment Stage', 'Geography']).size().reset_index(name='Count')
    st.plotly_chart(px.density_heatmap(stage_geo, x='Investment Stage', y='Geography', z='Count', color_continuous_scale='Cividis'))

# Intern vs Investment Stage
with tabs[11]:
    st.subheader("💼 Intern vs Investment Stage")
    intern_stage = df_filtered.groupby(['Point of Contact', 'Investment Stage']).size().reset_index(name='Count')
    st.plotly_chart(px.bar(intern_stage, x='Point of Contact', y='Count', color='Investment Stage', barmode='stack', title='Investors per Intern by Stage'))

# Designation vs Source of Capital
with tabs[12]:
    st.subheader("🏢 Designation vs Source of Capital")
    designation_source = df_filtered.groupby(['Designation', 'Source of Capital']).size().reset_index(name='Count')
    st.plotly_chart(px.bar(designation_source, x='Designation', y='Count', color='Source of Capital', barmode='group'))