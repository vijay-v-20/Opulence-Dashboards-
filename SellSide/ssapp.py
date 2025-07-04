import streamlit as st
import pandas as pd
import plotly.express as px

# ✅ Page config
st.set_page_config(page_title="Sell Side Committee Dashboard", layout="wide")

# ✅ Load external CSS
from pathlib import Path

def load_css(filename):
    css_path = Path(__file__).parent / filename
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css("style.css")

# ✅ Top navbar
st.markdown('<div class="navbar">💼 Sell Side Committee Dashboard</div>', unsafe_allow_html=True)

# ✅ Load data
from pathlib import Path
excel_path = Path(__file__).parent / "SellSide.xlsx"
df = pd.read_excel(excel_path)

df = df.dropna(how='all')

# --- Sidebar Filters ---
st.sidebar.header("🔍 Filters")

def dropdown_filter(label, column):
    unique_vals = sorted(df[column].dropna().unique())
    all_selected = st.sidebar.checkbox(f"Select all {label}", value=True, key=label)
    return unique_vals if all_selected else st.sidebar.multiselect(label, unique_vals, default=unique_vals)

filter_fields = [
    "Sector", "Sub-Sector", "Business Model", "Location", "Deal Type",
    "Investor Fit", "Status", "Assigned Analyst"
]

for field in filter_fields:
    if field in df.columns:
        df = df[df[field].isin(dropdown_filter(field, field))]

if "Deal Readiness" in df.columns:
    min_r, max_r = st.sidebar.slider("Deal Readiness (1 to 5)", 1, 5, (1, 5))
    df = df[df["Deal Readiness"].between(min_r, max_r)]

# --- Tabs ---
tabs = st.tabs([
    "🏠 Overview", "📊 Sector Trends", "💼 Deal Types", "💰 Financials",
    "👥 Analysts", "📍 Locations", "📇 Contacts", "📌 Top Valuations",
    "📈 Matrix", "⚖️ Compare Segments"
])

# --- Tab 0: Overview ---
with tabs[0]:
    st.subheader("📊 Summary Metrics")
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Targets", len(df))
    c2.metric("Top Sector", df["Sector"].mode()[0] if not df["Sector"].isna().all() else "N/A")
    c3.metric("Top Location", df["Location"].mode()[0] if not df["Location"].isna().all() else "N/A")

    st.subheader("📌 Distribution Overview")
    pie_cols = ["Sector", "Sub-Sector", "Business Model", "Location", "Deal Type", "Investor Fit", "Status", "Assigned Analyst"]
    for col in pie_cols:
        if col in df.columns and not df[col].isna().all():
            st.plotly_chart(px.pie(df, names=col, title=f"{col} Distribution"), use_container_width=True)

# --- Tab 1: Sector Trends ---
with tabs[1]:
    st.subheader("📊 Sector vs Sub-Sector Trends")
    if "Sector" in df.columns and "Sub-Sector" in df.columns:
        trend_df = df.groupby(["Sector", "Sub-Sector"]).size().reset_index(name="Count")
        st.plotly_chart(px.bar(trend_df, x="Sector", y="Count", color="Sub-Sector", barmode="group"), use_container_width=True)

# --- Tab 2: Deal Types ---
with tabs[2]:
    st.subheader("💼 Deal Type vs Investor Fit")
    if "Deal Type" in df.columns and "Investor Fit" in df.columns:
        deal_df = df.groupby(["Deal Type", "Investor Fit"]).size().reset_index(name="Count")
        st.plotly_chart(px.bar(deal_df, x="Deal Type", y="Count", color="Investor Fit", barmode="group"), use_container_width=True)

# --- Tab 3: Financials ---
with tabs[3]:
    st.subheader("💰 Revenue vs EBITDA Margin")
    if "Revenue (FY24)" in df.columns and "EBITDA Margin" in df.columns:
        st.plotly_chart(px.scatter(df, x="Revenue (FY24)", y="EBITDA Margin", color="Sector", hover_name="Target Company Name"), use_container_width=True)

# --- Tab 4: Analysts ---
with tabs[4]:
    st.subheader("👥 Analyst Deal Count")
    if "Assigned Analyst" in df.columns:
        analyst_df = df["Assigned Analyst"].value_counts().reset_index()
        analyst_df.columns = ["Analyst", "Deals"]
        st.plotly_chart(px.bar(analyst_df, x="Analyst", y="Deals", text="Deals", color="Deals"), use_container_width=True)

# --- Tab 5: Locations ---
with tabs[5]:
    st.subheader("📍 Deal Locations")
    if "Location" in df.columns:
        loc_df = df["Location"].value_counts().reset_index()
        loc_df.columns = ["Location", "Count"]
        st.plotly_chart(px.bar(loc_df, x="Location", y="Count", color="Count", text="Count"), use_container_width=True)

# --- Tab 6: Contacts ---
with tabs[6]:
    st.subheader("📇 Contact List")
    contact_cols = ["Target Company Name", "Promoter Name", "Email ID", "Phone No", "Location"]
    available_cols = [col for col in contact_cols if col in df.columns]
    if available_cols:
        st.dataframe(df[available_cols], use_container_width=True)

# --- Tab 7: Top Valuations ---
with tabs[7]:
    st.subheader("📌 Top 10 Valuation Expectations")
    if "Valuation Expectation" in df.columns:
        top_val = df[~df["Valuation Expectation"].isna()].sort_values(by="Valuation Expectation", ascending=False).head(10)
        st.dataframe(top_val, use_container_width=True)

# --- Tab 8: Matrix ---
with tabs[8]:
    st.subheader("📈 Deal Type vs Readiness Matrix")
    if "Deal Type" in df.columns and "Deal Readiness" in df.columns:
        matrix = df.pivot_table(index="Deal Type", columns="Deal Readiness", aggfunc="size", fill_value=0)
        st.dataframe(matrix.style.background_gradient(cmap="Blues"), use_container_width=True)

# --- Tab 9: Compare Segments ---
with tabs[9]:
    st.subheader("⚖️ Compare Segments")
    if "Sector" in df.columns:
        col_type = st.selectbox("Select Field to Compare", ["Sector", "Business Model", "Deal Type", "Assigned Analyst"])
        options = df[col_type].dropna().unique()
        seg1 = st.selectbox("First Segment", options, key="seg1")
        seg2 = st.selectbox("Second Segment", options, index=1 if len(options) > 1 else 0, key="seg2")

        if seg1 != seg2:
            comp_df = df[df[col_type].isin([seg1, seg2])]

            if "Revenue (FY24)" in comp_df.columns:
                st.plotly_chart(px.box(comp_df, x=col_type, y="Revenue (FY24)", color=col_type), use_container_width=True)
            if "EBITDA Margin" in comp_df.columns:
                avg_df = comp_df.groupby(col_type)["EBITDA Margin"].mean().reset_index()
                st.plotly_chart(px.bar(avg_df, x=col_type, y="EBITDA Margin", color=col_type), use_container_width=True)

            st.dataframe(comp_df[[col_type, "Target Company Name"] + [col for col in comp_df.columns if col not in [col_type, "Target Company Name"]]], use_container_width=True)