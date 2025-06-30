import streamlit as st
import pandas as pd
import plotly.express as px

# Page config
st.set_page_config(page_title="Buy Side Committee Dashboard", layout="wide")


# Load external CSS
from pathlib import Path

def load_css(filename):
    css_path = Path(__file__).parent / filename
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css("style.css")

# Top navbar
st.markdown('<div class="navbar">📊 Strategic Buy Side Committee Dashboard</div>', unsafe_allow_html=True)

# Load data
from pathlib import Path
excel_path = Path(__file__).parent / "vs.xlsx"
df = pd.read_excel(excel_path)

df = df.dropna(how='all')

# --- Sidebar Filters ---
st.sidebar.header("🔍 Filters")

def dropdown_filter(label, column):
    unique_vals = sorted(df[column].dropna().unique())
    all_selected = st.sidebar.checkbox(f"Select all {label}", value=True, key=label)
    return unique_vals if all_selected else st.sidebar.multiselect(label, unique_vals, default=unique_vals)

filter_fields = [
    "Sector of Interest", "Geography Preference", "Investment Type",
    "Deal Structure Preference", "Client Type", "Investment Horizon",
    "ESG Mandate", "Board Representation Required", "Risk Appetite",
    "Decision Making Speed"
]

for field in filter_fields:
    if field in df.columns:
        df = df[df[field].isin(dropdown_filter(field, field))]

if "Engagement Level (1 to 5)" in df.columns:
    min_eng, max_eng = st.sidebar.slider("Engagement Level (1 to 5)", 1, 5, (1, 5))
    df = df[df["Engagement Level (1 to 5)"].between(min_eng, max_eng)]

# --- Tabs ---
tabs = st.tabs([
    "📊 Overview", "📈 Sector Trends", "💼 Investment Types", "📍 Geography",
    "💰 Financial Preferences", "📇 Contacts", "⚖️ Compare Segments"
])

# --- Tab 0: Overview ---
with tabs[0]:
    st.subheader("📊 Summary Metrics")
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Clients", len(df))
    c2.metric("Top Sector", df["Sector of Interest"].mode()[0] if not df["Sector of Interest"].isna().all() else "N/A")
    c3.metric("Top Geography", df["Geography Preference"].mode()[0] if not df["Geography Preference"].isna().all() else "N/A")

    st.subheader("📌 Distribution Overview")
    pie_cols = ["Sector of Interest", "Geography Preference", "Investment Type", "Deal Structure Preference",
                "Client Type", "ESG Mandate", "Board Representation Required", "Risk Appetite"]
    for col in pie_cols:
        if col in df.columns and not df[col].isna().all():
            st.plotly_chart(px.pie(df, names=col, title=f"{col} Distribution"), use_container_width=True)

# --- Tab 1: Sector Trends ---
with tabs[1]:
    st.subheader("📈 Sector vs Deal Structure")
    chart = df.groupby(["Sector of Interest", "Deal Structure Preference"]).size().reset_index(name="Count")
    fig = px.bar(chart, x="Sector of Interest", y="Count", color="Deal Structure Preference", barmode="group")
    st.plotly_chart(fig, use_container_width=True)

# --- Tab 2: Investment Types ---
with tabs[2]:
    st.subheader("💼 Investment Type vs Horizon")
    chart = df.groupby(["Investment Type", "Investment Horizon"]).size().reset_index(name="Count")
    fig = px.bar(chart, x="Investment Type", y="Count", color="Investment Horizon", barmode="stack")
    st.plotly_chart(fig, use_container_width=True)

# --- Tab 3: Geography ---
with tabs[3]:
    st.subheader("📍 Geography Preference")
    chart = df["Geography Preference"].value_counts().reset_index()
    chart.columns = ["Geography", "Count"]
    fig = px.bar(chart, x="Geography", y="Count", text="Count", color="Count")
    st.plotly_chart(fig, use_container_width=True)

# --- Tab 4: Financial Preferences ---
with tabs[4]:
    st.subheader("💰 Fund Size vs Deal Size")
    df_numeric = df.copy()
    df_numeric["Fund Size (INR Cr)"] = pd.to_numeric(df_numeric["Fund Size (INR Cr)"], errors='coerce')
    df_numeric["Deal Size Range (INR Cr)"] = pd.to_numeric(df_numeric["Deal Size Range (INR Cr)"], errors='coerce')
    fig = px.scatter(df_numeric, x="Fund Size (INR Cr)", y="Deal Size Range (INR Cr)", color="Sector of Interest")
    st.plotly_chart(fig, use_container_width=True)

# --- Tab 5: Contacts ---
with tabs[5]:
    st.subheader("📇 Contact List")
    contact_cols = ["Client Name", "Contact Person Name", "Designation", "Email ID", "Phone No"]
    st.dataframe(df[[col for col in contact_cols if col in df.columns]], use_container_width=True)
    st.download_button("⬇️ Download Filtered Data", df.to_csv(index=False), file_name="Filtered_BuySide_Clients.csv")

# --- Tab 6: Compare Segments ---
with tabs[6]:
    st.subheader("⚖️ Compare Segments")
    comp_field = st.selectbox("Select Comparison Field", ["Sector of Interest", "Investment Type", "Client Type"])
    unique_vals = df[comp_field].dropna().unique()
    col1, col2 = st.columns(2)
    seg1 = col1.selectbox("Segment A", unique_vals, key="seg1")
    seg2 = col2.selectbox("Segment B", unique_vals, index=1 if len(unique_vals) > 1 else 0, key="seg2")

    if seg1 != seg2:
        comp_df = df[df[comp_field].isin([seg1, seg2])]
        comp_df["Fund Size (INR Cr)"] = pd.to_numeric(comp_df["Fund Size (INR Cr)"], errors='coerce')

        st.subheader("📊 Fund Size Comparison")
        st.plotly_chart(px.box(comp_df, x=comp_field, y="Fund Size (INR Cr)", color=comp_field), use_container_width=True)

        st.subheader("📋 Summary Stats")
        summary = comp_df.groupby(comp_field).agg({
            "Fund Size (INR Cr)": "mean",
            "Client Name": "count"
        }).rename(columns={"Client Name": "Client Count"}).reset_index()
        st.dataframe(summary, use_container_width=True)
