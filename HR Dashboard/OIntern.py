import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Interns Dashboard", layout="wide")


# Load the cleaned data (simulate loading for deployed app)
@st.cache_data
def load_data():
    df = pd.read_excel("OEmployees.xlsx", sheet_name='Sheet2', skiprows=2)
    df.columns = [
        "Index", "Sno", "Student Name", "Collage Name", "Phone No.", "Email ID",
        "Specialisation", "WHO/WFH", "Days Worked", "Allocated Sector",
        "New Deals Assigned", "Existing Deals Worked", "Priority of Deal",
        "Attendance Days", "Absences", "Performance Score",
        "Stakeholder Feedback", "Intern Remarks", "Number"
    ]
    df = df.drop(columns=["Index", "Number"])
    df = df.dropna(subset=["Student Name"])
    df["Days Worked"] = pd.to_numeric(df["Days Worked"], errors='coerce')
    df["Attendance Days"] = pd.to_numeric(df["Attendance Days"], errors='coerce')
    df["Absences"] = pd.to_numeric(df["Absences"], errors='coerce')
    df["Performance Score"] = pd.to_numeric(df["Performance Score"], errors='coerce')
    return df

df = load_data()

st.title("📊 Interns Performance Dashboard")

# Filters


with st.sidebar:
    st.header("🔍 Filters")
    specialisation = st.multiselect("Select Specialisation", df["Specialisation"].unique())
    work_mode = st.multiselect("Select Work Mode", df["WHO/WFH"].unique())
    sector = st.multiselect("Select Sector", df["Allocated Sector"].unique())

filtered_df = df.copy()
if specialisation:
    filtered_df = filtered_df[filtered_df["Specialisation"].isin(specialisation)]
if work_mode:
    filtered_df = filtered_df[filtered_df["WHO/WFH"].isin(work_mode)]
if sector:
    filtered_df = filtered_df[filtered_df["Allocated Sector"].isin(sector)]

# KPI Section
# ===== ADD THIS SECTION RIGHT AFTER THE KPI METRICS (around line 50) =====

st.divider()

# NEW SECTION: INDIVIDUAL INTERN DETAILS
st.subheader("👤 Individual Intern Performance Explorer")

# Create two columns for better layout
col1, col2 = st.columns([1, 3])

with col1:
    # Enhanced intern selector with search
    selected_intern = st.selectbox(
        "Select Intern:",
        df["Student Name"].unique(),
        index=0,
        key="intern_selector"
    )
    
    # Quick stats card
    intern_data = df[df["Student Name"] == selected_intern].iloc[0]
    st.markdown(f"""
    **📌 Quick Stats:**
    - **Specialization:** {intern_data['Specialisation']}
    - **Work Mode:** {intern_data['WHO/WFH']}
    - **Sector:** {intern_data['Allocated Sector']}
    - **Deals:** {intern_data['New Deals Assigned']} new, {intern_data['Existing Deals Worked']} existing
    - **Priority:** {intern_data['Priority of Deal']}
    """)

with col2:
    # Performance metrics visualization
    fig_ind, ax_ind = plt.subplots(figsize=(10, 4))
    metrics = ["Performance Score", "Days Worked", "Attendance Days"]
    values = [intern_data[m] for m in metrics]
    ax_ind.barh(metrics, values, color=['#4CAF50', '#2196F3', '#FFC107'])
    ax_ind.set_title(f"{selected_intern}'s Key Metrics")
    ax_ind.set_xlim(0, max(values)*1.2)
    for i, v in enumerate(values):
        ax_ind.text(v + 1, i, str(v), color='black', va='center')
    st.pyplot(fig_ind)

# Detailed feedback section
st.markdown("""
**📝 Feedback & Remarks:**
""")
feedback_col1, feedback_col2 = st.columns(2)
with feedback_col1:
    st.markdown(f"**Stakeholder Feedback:**  \n{intern_data['Stakeholder Feedback']}")
with feedback_col2:
    st.markdown(f"**Intern Remarks:**  \n{intern_data['Intern Remarks']}")

# Comparative performance chart
st.subheader("📊 Performance Comparison")
compare_col1, compare_col2, compare_col3 = st.columns(3)
with compare_col1:
    compare_mode = st.radio(
        "Compare with:",
        ["Specialization Peers", "Sector Peers", "All Interns"],
        horizontal=True
    )

# Prepare comparison data
if compare_mode == "Specialization Peers":
    compare_df = df[df["Specialisation"] == intern_data["Specialisation"]]
elif compare_mode == "Sector Peers":
    compare_df = df[df["Allocated Sector"] == intern_data["Allocated Sector"]]
else:
    compare_df = df

fig_compare, ax_compare = plt.subplots(figsize=(10, 5))
sns.boxplot(data=compare_df, y="Performance Score", ax=ax_compare, color="lightblue")
ax_compare.scatter(0, intern_data["Performance Score"], color='red', s=100, label="Selected Intern")
ax_compare.set_title(f"Performance Comparison ({compare_mode})")
ax_compare.legend()
ax_compare.set_xticklabels([])
st.pyplot(fig_compare)

st.divider()
# ===== END OF NEW SECTION =====

st.markdown("### 📌 Key Performance Indicators")
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("👩‍🎓 Total Interns", len(filtered_df))
kpi2.metric("📈 Avg Performance Score", round(filtered_df["Performance Score"].mean(), 2))
kpi3.metric("📅 Avg Days Worked", round(filtered_df["Days Worked"].mean(), 2))
kpi4.metric("🚫 Avg Absences", round(filtered_df["Absences"].mean(), 2))

st.divider()

# Charts
st.subheader("📍 Work Mode Distribution")
fig1, ax1 = plt.subplots()
filtered_df["WHO/WFH"].value_counts().plot.pie(autopct='%1.1f%%', startangle=90, ax=ax1)
ax1.set_ylabel('')
ax1.set_title("WHO vs WFH Distribution")
st.pyplot(fig1)

st.subheader("📊 Deals Assigned vs. Worked")
fig2, ax2 = plt.subplots(figsize=(10, 6))
x = range(len(filtered_df))
ax2.bar(x, filtered_df["New Deals Assigned"], width=0.4, label='New Deals')
ax2.bar([i + 0.4 for i in x], filtered_df["Existing Deals Worked"], width=0.4, label='Existing Deals')
ax2.set_xticks([i + 0.2 for i in x])
ax2.set_xticklabels(filtered_df["Student Name"], rotation=45, ha='right')
ax2.set_title("Deals Overview")
ax2.legend()
st.pyplot(fig2)

st.subheader("📈 Performance Score Distribution")
fig3, ax3 = plt.subplots()
sns.histplot(filtered_df["Performance Score"], bins=10, kde=True, ax=ax3)
ax3.set_title("Performance Score Histogram")
st.pyplot(fig3)

st.subheader("📌 Stakeholder Feedback Count")
fig4, ax4 = plt.subplots()
filtered_df["Stakeholder Feedback"].value_counts().plot(kind='bar', ax=ax4)
ax4.set_title("Feedback Overview")
ax4.set_ylabel("Count")
ax4.set_xlabel("Feedback")
st.pyplot(fig4)

st.subheader("🏆 Top 5 Interns by Performance")
top_performers = filtered_df.sort_values(by="Performance Score", ascending=False).head(5)
st.dataframe(top_performers[["Student Name", "Specialisation", "Performance Score", "Stakeholder Feedback"]],
             use_container_width=True)

st.divider()
st.markdown("✅ *All data is dynamically filterable from the sidebar. Please apply filters to dive deep into specific groups of interns.*")


st.subheader("📌 Correlation Heatmap Between Numeric Metrics")
numeric_cols = ["Days Worked", "Attendance Days", "Absences", "Performance Score"]
corr = filtered_df[numeric_cols].corr()
fig5, ax5 = plt.subplots(figsize=(8, 6))
sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f", ax=ax5)
ax5.set_title("Correlation Heatmap")
st.pyplot(fig5)

st.subheader("📋 Deal Priority Distribution")
fig6, ax6 = plt.subplots()
filtered_df["Priority of Deal"].value_counts().plot(kind='bar', color='skyblue', ax=ax6)
ax6.set_title("Deal Priority Count")
ax6.set_ylabel("Count")
ax6.set_xlabel("Priority Level")
st.pyplot(fig6)

st.subheader("🎓 Specialisation vs Performance (Box Plot)")
fig7, ax7 = plt.subplots(figsize=(10, 6))
sns.boxplot(data=filtered_df, x="Specialisation", y="Performance Score", ax=ax7)
ax7.set_title("Performance by Specialisation")
ax7.set_xticklabels(ax7.get_xticklabels(), rotation=30)
st.pyplot(fig7)

st.subheader("🏢 Sector-wise Average Performance")
sector_perf = filtered_df.groupby("Allocated Sector")["Performance Score"].mean().sort_values()
fig8, ax8 = plt.subplots()
sector_perf.plot(kind='barh', color='mediumseagreen', ax=ax8)
ax8.set_title("Avg. Performance Score by Sector")
ax8.set_xlabel("Avg Performance Score")
st.pyplot(fig8)

# SECTION A: SMART SEGMENTATION & INSIGHTS

st.subheader("🧠 Performance Segmentation")
def segment(score):
    if score >= 8:
        return "High"
    elif score >= 5:
        return "Medium"
    else:
        return "Low"

filtered_df["Performance Segment"] = filtered_df["Performance Score"].apply(segment)
segment_count = filtered_df["Performance Segment"].value_counts()
fig9, ax9 = plt.subplots()
segment_count.plot(kind='bar', color=["green", "orange", "red"], ax=ax9)
ax9.set_title("Interns by Performance Segment")
st.pyplot(fig9)

st.subheader("📉 Absences vs Performance")
fig10, ax10 = plt.subplots()
sns.scatterplot(data=filtered_df, x="Absences", y="Performance Score", hue="Performance Segment", palette="Set2", ax=ax10)
ax10.set_title("Impact of Absences on Performance")
st.pyplot(fig10)

st.subheader("🏡 WFH vs WHO Comparison")
fig11, axs = plt.subplots(1, 3, figsize=(15, 5))

sns.boxplot(data=filtered_df, x="WHO/WFH", y="Performance Score", ax=axs[0])
axs[0].set_title("Performance by Work Mode")

sns.boxplot(data=filtered_df, x="WHO/WFH", y="Attendance Days", ax=axs[1])
axs[1].set_title("Attendance by Work Mode")

sns.boxplot(data=filtered_df, x="WHO/WFH", y="New Deals Assigned", ax=axs[2])
axs[2].set_title("New Deals by Work Mode")

plt.tight_layout()
st.pyplot(fig11)

# SECTION B: ANALYTICAL HIGHLIGHTS

st.subheader("🔍 Outliers in Performance")
avg_score = filtered_df["Performance Score"].mean()
std_dev = filtered_df["Performance Score"].std()

outliers_df = filtered_df[(filtered_df["Performance Score"] > avg_score + std_dev) |
                          (filtered_df["Performance Score"] < avg_score - std_dev)]

st.write(f"Interns significantly deviating from average score (mean = {round(avg_score,2)}):")
st.dataframe(outliers_df[["Student Name", "Performance Score", "Specialisation", "Absences"]], use_container_width=True)

st.subheader("📈 Interns Consistency Score")

filtered_df["Consistency Score"] = (
    (filtered_df["Days Worked"] - filtered_df["Absences"]) / filtered_df["Days Worked"]
).round(2)

fig12, ax12 = plt.subplots()
sns.histplot(filtered_df["Consistency Score"], bins=10, kde=True, color='purple', ax=ax12)
ax12.set_title("Interns' Consistency Score Distribution")
st.pyplot(fig12)

# Optional: WordCloud (if textual data is strong enough)
from wordcloud import WordCloud

st.subheader("💬 Word Cloud: Stakeholder Feedback")
feedback_text = ' '.join(filtered_df["Stakeholder Feedback"].dropna().astype(str).tolist())

if feedback_text.strip():
    wordcloud = WordCloud(background_color='white', width=800, height=400).generate(feedback_text)
    fig13, ax13 = plt.subplots(figsize=(10, 5))
    ax13.imshow(wordcloud, interpolation='bilinear')
    ax13.axis('off')
    st.pyplot(fig13)
else:
    st.info("Not enough feedback data to generate a word cloud.")
