

import streamlit as st
import pandas as pd
import plotly.express as px

# --- Page Config ---
st.set_page_config(page_title="Vendor Dashboard", layout="wide")

from pathlib import Path

def load_css(filename):
    css_path = Path(__file__).parent / filename
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css("style.css")


st.markdown('<div class="navbar">📦 Vendor Management Dashboard</div>', unsafe_allow_html=True)

# --- Load and Clean Data ---
from pathlib import Path
excel_path = Path(__file__).parent / "vs.xlsx"
df = pd.read_excel(excel_path)

df = df.dropna(how='all')

# Clean numeric columns
numeric_cols = [
    "Total PO Value (₹)", "Avg Rating (1–5)", "On-Time Delivery (%)",
    "Defect Rate (%)", "Pending Payments (₹)", "SLA Breaches", "Complaints Count"
]
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# --- Sidebar Filters ---
st.sidebar.header("🔍 Filter Vendors")

# ✅ Master Toggle
select_all = st.sidebar.checkbox("✅ Select All Filters", value=True)

# Individual filters, obey master toggle
categories = st.sidebar.multiselect(
    "Category", sorted(df["Category"].dropna().unique()),
    default=sorted(df["Category"].dropna().unique()) if select_all else []
)

locations = st.sidebar.multiselect(
    "Location", sorted(df["Location"].dropna().unique()),
    default=sorted(df["Location"].dropna().unique()) if select_all else []
)

iso_certified = st.sidebar.multiselect(
    "ISO Certified", sorted(df["ISO Certified"].dropna().unique()),
    default=sorted(df["ISO Certified"].dropna().unique()) if select_all else []
)

status_filter = st.sidebar.multiselect(
    "Status", sorted(df["Status"].dropna().unique()),
    default=sorted(df["Status"].dropna().unique()) if select_all else []
)

# ✅ Apply Filters
df = df[
    df["Category"].isin(categories) &
    df["Location"].isin(locations) &
    df["ISO Certified"].isin(iso_certified) &
    df["Status"].isin(status_filter)
]

# Apply filters
df = df[
    df["Category"].isin(categories) &
    df["Location"].isin(locations) &
    df["ISO Certified"].isin(iso_certified) &
    df["Status"].isin(status_filter)
]

# --- Layout Tabs ---
tabs = st.tabs([
    "📊 Overview", "📈 Visual Insights", "📋 Vendor Table",
    "🧾 Payment Overview", "⚙️ Performance Metrics", "🗂 Category Drilldown"
])

# --- Tab 0: Overview ---
with tabs[0]:
    st.markdown("## 📊 Key Performance Indicators")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### 🧾 Total Vendors")
        st.markdown(f"<h2 style='color:#0072C6'>{len(df)}</h2>", unsafe_allow_html=True)
    with col2:
        st.markdown("### ⭐ Average Rating")
        st.markdown(f"<h2 style='color:#0072C6'>{df['Avg Rating (1–5)'].mean():.2f}</h2>", unsafe_allow_html=True)
    with col3:
        st.markdown("### 💰 Total PO Value (₹)")
        st.markdown(f"<h2 style='color:#0072C6'>{df['Total PO Value (₹)'].sum():,.0f}</h2>", unsafe_allow_html=True)

    col4, col5 = st.columns(2)
    with col4:
        st.markdown("### ⏱️ Avg On-Time Delivery (%)")
        st.markdown(f"<h2 style='color:#0072C6'>{df['On-Time Delivery (%)'].mean():.2f}</h2>", unsafe_allow_html=True)
    with col5:
        st.markdown("### ⚠️ Avg Defect Rate (%)")
        st.markdown(f"<h2 style='color:#0072C6'>{df['Defect Rate (%)'].mean():.2f}</h2>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📍 Vendor Distribution by Location")
    loc_df = df["Location"].value_counts().reset_index()
    loc_df.columns = ["Location", "Count"]
    fig_loc = px.bar(loc_df, x="Location", y="Count", color="Location", title="Vendors by Location")
    st.plotly_chart(fig_loc, use_container_width=True)

    st.markdown("### 🔄 Status Distribution")
    fig_status = px.pie(df, names="Status", hole=0.5, title="Vendor Status Distribution")
    st.plotly_chart(fig_status, use_container_width=True)

# --- Tab 1: Visual Insights ---
with tabs[1]:
    st.subheader("📈 Visual Insights")
    c1, c2 = st.columns(2)

    with c1:
        cat_df = df["Category"].value_counts().reset_index()
        cat_df.columns = ["Category", "Count"]
        fig1 = px.bar(cat_df, x="Category", y="Count", title="Vendors by Category")
        st.plotly_chart(fig1, use_container_width=True)

    with c2:
        fig2 = px.pie(df, names="ISO Certified", title="ISO Certification Distribution")
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("🎯 Ratings by Category")
    fig3 = px.box(df, x="Category", y="Avg Rating (1–5)", color="Category", title="Ratings Distribution by Category")
    st.plotly_chart(fig3, use_container_width=True)

# --- Tab 2: Vendor Table ---
with tabs[2]:
    st.subheader("📋 Vendor Table")
    st.dataframe(df, use_container_width=True)
    st.download_button("⬇️ Download Filtered Data", df.to_csv(index=False), "Filtered_Vendors.csv")

# --- Tab 3: Payment Overview ---
with tabs[3]:
    st.subheader("🧾 Payment Overview")

    df["Pending Payments (₹)"] = pd.to_numeric(df["Pending Payments (₹)"], errors="coerce")
    df["Total PO Value (₹)"] = pd.to_numeric(df["Total PO Value (₹)"], errors="coerce")

    st.metric("💸 Total Pending Payments (₹)", f"{df['Pending Payments (₹)'].sum():,.0f}")

    st.markdown("### 📊 Pending Payments vs PO Value (Top 10 Vendors)")
    pay_df = df[["Vendor Name", "Pending Payments (₹)", "Total PO Value (₹)"]].dropna()
    top10 = pay_df.sort_values("Pending Payments (₹)", ascending=False).head(10)

    fig_combo = px.bar(top10, x="Vendor Name", y="Pending Payments (₹)",
                       labels={"Pending Payments (₹)": "Pending Amount"},
                       color_discrete_sequence=["#0072C6"])

    fig_combo.add_scatter(x=top10["Vendor Name"], y=top10["Total PO Value (₹)"],
                          mode="lines+markers", name="Total PO Value",
                          line=dict(color="orange", width=3))
    fig_combo.update_layout(title="Top 10 Vendors: Pending Payments vs PO Value")
    st.plotly_chart(fig_combo, use_container_width=True)

    st.markdown("### 📂 Avg Pending Payment by Category")
    cat_df = df[["Category", "Pending Payments (₹)"]].dropna()
    cat_avg = cat_df.groupby("Category", as_index=False)["Pending Payments (₹)"].mean()
    cat_avg = cat_avg[cat_avg["Pending Payments (₹)"] > 0]

    fig_avg = px.bar(cat_avg, x="Category", y="Pending Payments (₹)",
                     title="Average Pending by Category",
                     color="Category", color_discrete_sequence=px.colors.qualitative.Set2)
    st.plotly_chart(fig_avg, use_container_width=True)

# --- Tab 4: Performance Metrics ---
with tabs[4]:
    st.subheader("⚙️ Performance Metrics")

    fig_sla = px.scatter(df, x="SLA Breaches", y="Avg Rating (1–5)", size="Complaints Count",
                         color="Category", title="SLA Breaches vs Rating")
    st.plotly_chart(fig_sla, use_container_width=True)

    fig_defect = px.bar(df.groupby("Category")["Defect Rate (%)"].mean().reset_index(),
                        x="Category", y="Defect Rate (%)", title="Average Defect Rate by Category")
    st.plotly_chart(fig_defect, use_container_width=True)

    fig_ontime = px.box(df, x="Category", y="On-Time Delivery (%)", title="On-Time Delivery by Category")
    st.plotly_chart(fig_ontime, use_container_width=True)

# --- Tab 5: Category Drilldown ---
with tabs[5]:
    st.subheader("🗂 Category Drilldown")
    selected_cat = st.selectbox("Choose a Category", sorted(df["Category"].dropna().unique()))

    cat_df = df[df["Category"] == selected_cat]
    st.markdown(f"### Showing {len(cat_df)} vendors in **{selected_cat}** category")

    st.dataframe(cat_df, use_container_width=True)
    st.download_button("⬇️ Download Category Data", cat_df.to_csv(index=False), f"{selected_cat}_vendors.csv")
