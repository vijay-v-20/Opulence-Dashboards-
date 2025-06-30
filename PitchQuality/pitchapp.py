# # =======================
# # Professional Pitch Evaluation Dashboard
# # =======================

# import streamlit as st
# import pandas as pd
# import plotly.express as px
# import plotly.graph_objects as go
# from datetime import datetime
# from fpdf import FPDF
# from io import BytesIO
# import base64

# st.set_page_config(page_title="📊 Pitch Evaluation Pro", layout="wide")

# # ===== Theme Settings =====
# MATERIAL_STYLE = {
#     "bg_color": "#F9FAFC",
#     "primary": "#1976D2",
#     "accent": "#FFC107",
#     "text": "#212121",
#     "card_bg": "#FFFFFF",
#     "shadow": "0px 4px 12px rgba(0, 0, 0, 0.1)"
# }

# st.markdown(f"""
#     <style>
#     body {{ background-color: {MATERIAL_STYLE['bg_color']} !important; }}
#     .block-container {{ padding: 2rem 1rem; }}
#     .stSelectbox > div > div {{ background-color: white !important; border-radius: 8px; }}
#     .stMetric-value {{ color: {MATERIAL_STYLE['primary']} }}
#     .stButton > button {{
#         background-color: {MATERIAL_STYLE['primary']};
#         color: white;
#         border-radius: 10px;
#         padding: 10px 16px;
#         border: none;
#     }}
#     </style>
# """, unsafe_allow_html=True)

# # ===== Data Loading =====
# @st.cache_data
# def load_data(uploaded_file):
#     df = pd.read_excel(uploaded_file)
#     df.columns = df.columns.str.strip()  # <-- Clean column names
#     df['Last Updated'] = pd.to_datetime(df['Last Updated'], errors='coerce')
#     df['Reply Rate'] = (df['Total Reply Recived'] / df['Total pitches']) * 100
#     return df

# uploaded_file = st.sidebar.file_uploader("Upload Pitch Evaluation File", type=["xlsx"])

# if uploaded_file:
#     df = load_data(uploaded_file)

#     # ===== Sidebar Filters =====
#     with st.sidebar:
#         st.markdown("## Filters")
#         all_sectors = ["All"] + sorted(df['Industry Sector'].dropna().unique().tolist())
#         all_grades = ["All"] + sorted(df['Grade'].dropna().unique().tolist())

#         sectors = st.multiselect("Industry Sector", all_sectors, default="All")
#         grades = st.multiselect("Grades", all_grades, default="All")

#         eval_status = st.multiselect("Evaluation Status", df['Evaluation Status'].unique())
#         intern_name = st.selectbox("Select Intern", ["All"] + df['Intern Name'].unique().tolist())
#         date_range = st.date_input("Date Range", [df['Last Updated'].min(), df['Last Updated'].max()])

#     filtered_df = df.copy()
#     if "All" not in sectors:
#         filtered_df = filtered_df[filtered_df['Industry Sector'].isin(sectors)]
#     if "All" not in grades:
#         filtered_df = filtered_df[filtered_df['Grade'].isin(grades)]
#     if eval_status:
#         filtered_df = filtered_df[filtered_df['Evaluation Status'].isin(eval_status)]
#     if intern_name != "All":
#         filtered_df = filtered_df[filtered_df['Intern Name'] == intern_name]
#     if date_range:
#         filtered_df = filtered_df[
#             (filtered_df['Last Updated'] >= pd.to_datetime(date_range[0])) &
#             (filtered_df['Last Updated'] <= pd.to_datetime(date_range[1]))
#         ]

#     # ===== Dashboard Layout =====
#     st.title("📊 Pitch Evaluation Dashboard")
#     st.markdown("---")

#     # ===== KPI Cards =====
#     col1, col2, col3, col4 = st.columns(4)
#     col1.metric("Total Interns", len(filtered_df))
#     col2.metric("Avg Score", f"{filtered_df['Total Score'].mean():.2f}")
#     col3.metric("Approval Rate", f"{(filtered_df['Evaluation Status'] == 'Approved').mean() * 100:.1f}%")
#     col4.metric("Avg Reply Rate", f"{filtered_df['Reply Rate'].mean():.1f}%")

#     st.markdown("---")

#     # ===== Charts Section =====
#     tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Performance", "Comparisons", "Intern Cards"])

#     with tab1:
#         st.subheader("Pie Charts & Distributions")
#         pie1, pie2 = st.columns(2)
#         with pie1:
#             st.plotly_chart(px.pie(filtered_df, names='Grade', title='Grade Distribution', hole=0.3))
#         with pie2:
#             st.plotly_chart(px.pie(filtered_df, names='Industry Sector', title='Sectors Covered', hole=0.3))

#     with tab2:
#         st.subheader("Performance Charts")
#         bar = px.bar(
#             filtered_df.groupby('Intern Name')['Total Score'].mean().nlargest(10).reset_index(),
#             x='Intern Name', y='Total Score', title='Top 10 Interns by Score', color='Total Score',
#             color_continuous_scale='Viridis')
#         st.plotly_chart(bar, use_container_width=True)

#         line = px.line(
#             filtered_df.sort_values('Last Updated'),
#             x='Last Updated', y='Total Score', title='Score Trend Over Time',
#             color='Intern Name')
#         st.plotly_chart(line, use_container_width=True)

#         scatter = px.scatter(
#             filtered_df, x='Reply Rate', y='Total Score', color='Grade',
#             size='Total pitches', title='Score vs Reply Rate', hover_name='Intern Name')
#         st.plotly_chart(scatter, use_container_width=True)

#     with tab3:
#         st.subheader("Comparative Analysis")
#         comp = filtered_df.groupby('Industry Sector')[['Total Score', 'Reply Rate']].mean().reset_index()
#         st.plotly_chart(px.bar(comp, x='Industry Sector', y='Total Score', title='Avg Score by Sector', color='Total Score'))
#         st.plotly_chart(px.bar(comp, x='Industry Sector', y='Reply Rate', title='Avg Reply Rate by Sector', color='Reply Rate'))

#     with tab4:
#         st.subheader("Intern Profile Cards")

#         # Ensure proper numeric types with fallback
#         filtered_df['Total pitches'] = pd.to_numeric(filtered_df['Total pitches'], errors='coerce').fillna(0)
#         filtered_df['Total Reply Recived'] = pd.to_numeric(filtered_df['Total Reply Recived'], errors='coerce').fillna(0)

#         for i, row in filtered_df.iterrows():
#             with st.expander(f"{row['Intern Name']} - {row['Pitch Company']}"):
#                 col1, col2 = st.columns([3, 2])
#                 with col1:
#                     st.markdown(f"**University:** {row.get('College/University', 'N/A')}")
#                     st.markdown(f"**Grade:** {row.get('Grade', 'N/A')}")
#                     st.markdown(f"**Score:** {row.get('Total Score', 'N/A')}/10")
#                     st.markdown(f"**Status:** {row.get('Evaluation Status', 'N/A')}")
#                     st.markdown(f"**Comments:** {row.get('Committee Comments', 'No comments')}")
#                 with col2:
#                     total_pitches = int(row["Total pitches"])
#                     replies_received = int(row["Total Reply Recived"])

#                     fig = go.Figure()
#                     fig.add_trace(go.Bar(
#                         x=["Total Pitches", "Replies Received"],
#                         y=[total_pitches, replies_received],
#                         marker_color=[MATERIAL_STYLE['primary'], MATERIAL_STYLE['accent']]
#                     ))
#                     fig.update_layout(
#                         title="Pitches vs Replies",
#                         xaxis_title="Metric",
#                         yaxis_title="Count",
#                         height=300
#                     )
#                     st.plotly_chart(fig, use_container_width=True, key=f"bar_{i}")


# =======================
# Professional Pitch Evaluation Dashboard
# =======================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from fpdf import FPDF
from io import BytesIO
import base64

st.set_page_config(page_title="📊 Pitch Evaluation Pro", layout="wide")

# ===== Theme Settings =====
MATERIAL_STYLE = {
    "bg_color": "#F9FAFC",
    "primary": "#1976D2",
    "accent": "#FFC107",
    "text": "#212121",
    "card_bg": "#FFFFFF",
    "shadow": "0px 4px 12px rgba(0, 0, 0, 0.1)"
}

st.markdown(f"""
    <style>
    body {{ background-color: {MATERIAL_STYLE['bg_color']} !important; }}
    .block-container {{ padding: 2rem 1rem; }}
    .stSelectbox > div > div {{ background-color: white !important; border-radius: 8px; }}
    .stMetric-value {{ color: {MATERIAL_STYLE['primary']} }}
    .stButton > button {{
        background-color: {MATERIAL_STYLE['primary']};
        color: white;
        border-radius: 10px;
        padding: 10px 16px;
        border: none;
    }}
    </style>
""", unsafe_allow_html=True)

# ===== Data Loading =====
@st.cache_data
def load_data():
    # Load data directly from the Excel file path
    df = pd.read_excel("Pitch_Quality_Commitee.xlsx")
    df.columns = df.columns.str.strip()  # Clean column names
    df['Last Updated'] = pd.to_datetime(df['Last Updated'], errors='coerce')
    df['Reply Rate'] = (df['Total Reply Recived'] / df['Total pitches']) * 100
    return df


# Load the data
df = load_data()

@st.cache_data
def load_data():
    try:
        # Debug: Show current directory and files
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        st.write(f"Current directory: {current_dir}")
        st.write(f"Files in directory: {os.listdir(current_dir)}")
        
        # Try multiple possible file paths
        possible_paths = [
            "Pitch_Quality_Commitee.xlsx",  # Same directory
            "./Pitch_Quality_Commitee.xlsx",  # Relative path
            os.path.join(current_dir, "Pitch_Quality_Commitee.xlsx")  # Absolute path
        ]
        
        for path in possible_paths:
            try:
                df = pd.read_excel(path)
                st.success(f"Successfully loaded file from: {path}")
                
                # Data processing
                df.columns = df.columns.str.strip()
                df['Last Updated'] = pd.to_datetime(df['Last Updated'], errors='coerce')
                df['Reply Rate'] = (df['Total Reply Recived'] / df['Total pitches']) * 100
                return df
                
            except Exception as e:
                st.warning(f"Failed to load from {path}: {str(e)}")
                continue
                
        raise FileNotFoundError("Excel file not found in any attempted paths")
        
    except Exception as e:
        st.error(f"Critical error loading data: {str(e)}")
        return pd.DataFrame()  # Return empty dataframe as fallback

# ===== Sidebar Filters =====

with st.sidebar:
    st.markdown("## Filters")
    all_sectors = ["All"] + sorted(df['Industry Sector'].dropna().unique().tolist())
    all_grades = ["All"] + sorted(df['Grade'].dropna().unique().tolist())

    sectors = st.multiselect("Industry Sector", all_sectors, default="All")
    grades = st.multiselect("Grades", all_grades, default="All")

    eval_status = st.multiselect("Evaluation Status", df['Evaluation Status'].unique())
    intern_name = st.selectbox("Select Intern", ["All"] + df['Intern Name'].unique().tolist())
    date_range = st.date_input("Date Range", [df['Last Updated'].min(), df['Last Updated'].max()])

filtered_df = df.copy()
if "All" not in sectors:
    filtered_df = filtered_df[filtered_df['Industry Sector'].isin(sectors)]
if "All" not in grades:
    filtered_df = filtered_df[filtered_df['Grade'].isin(grades)]
if eval_status:
    filtered_df = filtered_df[filtered_df['Evaluation Status'].isin(eval_status)]
if intern_name != "All":
    filtered_df = filtered_df[filtered_df['Intern Name'] == intern_name]
if date_range:
    filtered_df = filtered_df[
        (filtered_df['Last Updated'] >= pd.to_datetime(date_range[0])) &
        (filtered_df['Last Updated'] <= pd.to_datetime(date_range[1]))
    ]

# ===== Dashboard Layout =====
st.title("📊 Pitch Evaluation Dashboard")
st.markdown("---")

# ===== KPI Cards =====
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Interns", len(filtered_df))
col2.metric("Avg Score", f"{filtered_df['Total Score'].mean():.2f}")
col3.metric("Approval Rate", f"{(filtered_df['Evaluation Status'] == 'Approved').mean() * 100:.1f}%")
col4.metric("Avg Reply Rate", f"{filtered_df['Reply Rate'].mean():.1f}%")

st.markdown("---")

# ===== Charts Section =====
tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Performance", "Comparisons", "Intern Cards"])

with tab1:
    st.subheader("Pie Charts & Distributions")
    pie1, pie2 = st.columns(2)
    with pie1:
        st.plotly_chart(px.pie(filtered_df, names='Grade', title='Grade Distribution', hole=0.3))
    with pie2:
        st.plotly_chart(px.pie(filtered_df, names='Industry Sector', title='Sectors Covered', hole=0.3))

with tab2:
    st.subheader("Performance Charts")
    bar = px.bar(
        filtered_df.groupby('Intern Name')['Total Score'].mean().nlargest(10).reset_index(),
        x='Intern Name', y='Total Score', title='Top 10 Interns by Score', color='Total Score',
        color_continuous_scale='Viridis')
    st.plotly_chart(bar, use_container_width=True)

    line = px.line(
        filtered_df.sort_values('Last Updated'),
        x='Last Updated', y='Total Score', title='Score Trend Over Time',
        color='Intern Name')
    st.plotly_chart(line, use_container_width=True)

    scatter = px.scatter(
        filtered_df, x='Reply Rate', y='Total Score', color='Grade',
        size='Total pitches', title='Score vs Reply Rate', hover_name='Intern Name')
    st.plotly_chart(scatter, use_container_width=True)

with tab3:
    st.subheader("Comparative Analysis")
    comp = filtered_df.groupby('Industry Sector')[['Total Score', 'Reply Rate']].mean().reset_index()
    st.plotly_chart(px.bar(comp, x='Industry Sector', y='Total Score', title='Avg Score by Sector', color='Total Score'))
    st.plotly_chart(px.bar(comp, x='Industry Sector', y='Reply Rate', title='Avg Reply Rate by Sector', color='Reply Rate'))

with tab4:
    st.subheader("Intern Profile Cards")

    # Ensure proper numeric types with fallback
    filtered_df['Total pitches'] = pd.to_numeric(filtered_df['Total pitches'], errors='coerce').fillna(0)
    filtered_df['Total Reply Recived'] = pd.to_numeric(filtered_df['Total Reply Recived'], errors='coerce').fillna(0)

    for i, row in filtered_df.iterrows():
        with st.expander(f"{row['Intern Name']} - {row['Pitch Company']}"):
            col1, col2 = st.columns([3, 2])
            with col1:
                st.markdown(f"**University:** {row.get('College/University', 'N/A')}")
                st.markdown(f"**Grade:** {row.get('Grade', 'N/A')}")
                st.markdown(f"**Score:** {row.get('Total Score', 'N/A')}/10")
                st.markdown(f"**Status:** {row.get('Evaluation Status', 'N/A')}")
                st.markdown(f"**Comments:** {row.get('Committee Comments', 'No comments')}")
            with col2:
                total_pitches = int(row["Total pitches"])
                replies_received = int(row["Total Reply Recived"])

                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=["Total Pitches", "Replies Received"],
                    y=[total_pitches, replies_received],
                    marker_color=[MATERIAL_STYLE['primary'], MATERIAL_STYLE['accent']]
                ))
                fig.update_layout(
                    title="Pitches vs Replies",
                    xaxis_title="Metric",
                    yaxis_title="Count",
                    height=300
                )
                st.plotly_chart(fig, use_container_width=True, key=f"bar_{i}")