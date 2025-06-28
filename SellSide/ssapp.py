# import streamlit as st
# import pandas as pd
# import plotly.express as px

# # Load data
# df = pd.read_excel("SellSide.xlsx")
# df = df.dropna(how='all')

# st.set_page_config(layout="wide", page_title="Sell Side Dashboard")

# # --- Top Navbar Title Only ---
# st.markdown("""
# <style>
#     .navbar {
#         background-color: #1f77b4;
#         padding: 16px 28px;
#         border-radius: 8px;
#         color: white;
#         font-size: 36px;
#         text-align: center;
#         margin-bottom: 30px;
#     }
#     h1, h2, h3, h4, h5 {
#         font-size: 34px !important;
#     }
#     .block-container {
#         padding-top: 1rem;
#     }
#     label, input, .stSelectbox, .stSlider {
#         font-size: 28px !important;
#     }
# </style>
# <div class="navbar">💼 Sell Side Target Committee Dashboard</div>
# """, unsafe_allow_html=True)

# # --- Sidebar Filters ---
# st.sidebar.header("🔍 Filters")

# def dropdown_filter(label, column):
#     unique_vals = sorted(df[column].dropna().unique())
#     all_selected = st.sidebar.checkbox(f"Select all {label}", value=True, key=label)
#     return unique_vals if all_selected else st.sidebar.multiselect(label, unique_vals, default=unique_vals)

# # Apply Filters
# df = df[df["Sector"].isin(dropdown_filter("Sector", "Sector"))]
# df = df[df["Sub-Sector"].isin(dropdown_filter("Sub-Sector", "Sub-Sector"))]
# df = df[df["Business Model"].isin(dropdown_filter("Business Model", "Business Model"))]
# df = df[df["Location"].isin(dropdown_filter("Location", "Location"))]
# df = df[df["Deal Type"].isin(dropdown_filter("Deal Type", "Deal Type"))]
# df = df[df["Investor Fit"].isin(dropdown_filter("Investor Fit", "Investor Fit"))]
# df = df[df["Status"].isin(dropdown_filter("Status", "Status"))]
# df = df[df["Assigned Analyst"].isin(dropdown_filter("Assigned Analyst", "Assigned Analyst"))]

# min_r, max_r = st.sidebar.slider("Deal Readiness (1 to 5)", 1, 5, (1, 5))
# df = df[df["Deal Readiness"].between(min_r, max_r)]

# # --- Tabs ---
# tabs = st.tabs([
#     "🏠 Overview", "📊 Sector Trends", "💼 Deal Types", "💰 Financials",
#     "👥 Analysts", "📍 Locations", "📇 Contacts", "📌 Top Valuations",
#     "📈 Matrix", "⚖️ Compare"
# ])

# # --- Tab 0: Overview ---
# with tabs[0]:
#     st.subheader("📊 At-a-Glance Metrics")
#     c1, c2, c3, c4 = st.columns(4)
#     c1.metric("Total Targets", len(df))
#     c2.metric("Avg. EBITDA Margin", f"{df['EBITDA Margin'].mean():.2%}")
#     c3.metric("Top Sector", df["Sector"].mode()[0] if not df["Sector"].isna().all() else "N/A")
#     c4.metric("Analyst Count", df["Assigned Analyst"].nunique())

#     st.subheader(" Distribution Overview")
#     pie_cols = ["Sector", "Sub-Sector", "Business Model", "Location", "Deal Type", "Investor Fit", "Status", "Assigned Analyst"]
#     for col in pie_cols:
#         if col in df.columns and not df[col].isna().all():
#             st.plotly_chart(px.pie(df, names=col, title=f"{col} Distribution"), use_container_width=True)

# # --- Tab 1: Sector Trends ---
# with tabs[1]:
#     st.subheader("📊 Sector vs Sub-Sector")
#     trend = df.groupby(["Sector", "Sub-Sector"]).size().reset_index(name="Count")
#     fig = px.bar(trend, x="Sector", y="Count", color="Sub-Sector", barmode="group")
#     st.plotly_chart(fig, use_container_width=True)

# # --- Tab 2: Deal Types ---
# with tabs[2]:
#     st.subheader("💼 Deal Type vs Investor Fit")
#     dt = df.groupby(["Deal Type", "Investor Fit"]).size().reset_index(name="Count")
#     fig = px.bar(dt, x="Deal Type", y="Count", color="Investor Fit", barmode="group")
#     st.plotly_chart(fig, use_container_width=True)

#     st.subheader("📶 Deal Readiness Levels")
#     readiness = df["Deal Readiness"].value_counts().sort_index()
#     st.plotly_chart(px.line(x=readiness.index, y=readiness.values, markers=True), use_container_width=True)

# # --- Tab 3: Financials ---
# with tabs[3]:
#     st.subheader("💰 Revenue vs EBITDA Margin")
#     st.plotly_chart(px.scatter(df, x="Revenue (FY24)", y="EBITDA Margin", color="Sector", hover_name="Target Company Name"), use_container_width=True)

# # --- Tab 4: Analysts ---
# with tabs[4]:
#     st.subheader("👥 Analyst Deal Count")
#     analyst_df = df["Assigned Analyst"].value_counts().reset_index()
#     analyst_df.columns = ["Analyst", "Deals"]
#     st.plotly_chart(px.bar(analyst_df, x="Analyst", y="Deals", text="Deals", color="Deals"), use_container_width=True)

# # --- Tab 5: Locations ---
# with tabs[5]:
#     st.subheader("📍 Deal Locations")
#     loc_df = df["Location"].value_counts().reset_index()
#     loc_df.columns = ["Location", "Count"]
#     st.plotly_chart(px.bar(loc_df, x="Location", y="Count", color="Count", text="Count"), use_container_width=True)

# # --- Tab 6: Contacts ---
# with tabs[6]:
#     st.subheader("📇 Contact List")
#     st.dataframe(df[["Target Company Name", "Promoter Name", "Email ID", "Phone No", "Location"]], use_container_width=True)
#     st.download_button("⬇️ Download Filtered Data", df.to_csv(index=False), file_name="Filtered_SellSide_Targets.csv")

# # --- Tab 7: Top Valuations ---
# with tabs[7]:
#     st.subheader("📌 Top 10 Valuation Expectations")
#     top_val = df[~df["Valuation Expectation"].isna()].sort_values(by="Valuation Expectation", ascending=False).head(10)
#     st.dataframe(top_val[["Target Company Name", "Valuation Expectation", "Revenue (FY24)", "Deal Type", "Investor Fit"]], use_container_width=True)

# # --- Tab 8: Matrix View ---
# with tabs[8]:
#     st.subheader("📈 Deal Type vs Readiness Matrix")
#     matrix = df.pivot_table(index="Deal Type", columns="Deal Readiness", aggfunc="size", fill_value=0)
#     st.dataframe(matrix.style.background_gradient(cmap="Blues"), use_container_width=True)

# # --- Tab 9: Compare Segments ---
# with tabs[9]:
#     st.subheader("⚖️ Compare Segments")
#     col_type = st.selectbox("Select Comparison Field", ["Sector", "Business Model", "Deal Type", "Assigned Analyst"])
#     options = df[col_type].dropna().unique()
#     col1, col2 = st.columns(2)
#     seg1 = col1.selectbox("First Segment", options, key="seg1")
#     seg2 = col2.selectbox("Second Segment", options, index=1 if len(options) > 1 else 0, key="seg2")

#     if seg1 != seg2:
#         comp_df = df[df[col_type].isin([seg1, seg2])]

#         st.subheader("📊 Revenue Comparison")
#         st.plotly_chart(px.box(comp_df, x=col_type, y="Revenue (FY24)", color=col_type, points="all"), use_container_width=True)

#         st.subheader("💡 Avg. EBITDA Comparison")
#         avg_df = comp_df.groupby(col_type)["EBITDA Margin"].mean().reset_index()
#         st.plotly_chart(px.bar(avg_df, x=col_type, y="EBITDA Margin", color=col_type), use_container_width=True)

#         st.subheader("📋 Summary Stats")
#         fields = {
#             "Revenue (FY24)": "mean",
#             "EBITDA Margin": "mean",
#             "Valuation Expectation": "mean",
#             "Target Company Name": "count"
#         }

#         for col in ["Revenue (FY24)", "EBITDA Margin", "Valuation Expectation"]:
#             if col in comp_df.columns:
#                 comp_df[col] = pd.to_numeric(comp_df[col], errors='coerce')

#         valid_fields = {k: v for k, v in fields.items() if k in comp_df.columns and comp_df[k].dtype != 'object'}

#         if valid_fields:
#             summary = comp_df.groupby(col_type).agg(valid_fields).rename(
#                 columns={"Target Company Name": "Target Count"}).reset_index()
#             st.dataframe(summary, use_container_width=True)
#         else:
#             st.warning("⚠️ No valid numeric fields available for comparison summary.")


import streamlit as st
import pandas as pd
import plotly.express as px

# ✅ Page config
st.set_page_config(page_title="Sell Side Committee Dashboard", layout="wide")

# ✅ Load external CSS
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css("style.css")  # Make sure this file is in the same directory

# ✅ Top navbar
st.markdown('<div class="navbar">💼 Sell Side Committee Dashboard</div>', unsafe_allow_html=True)

# ✅ Load data
df = pd.read_excel("SellSide.xlsx")
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