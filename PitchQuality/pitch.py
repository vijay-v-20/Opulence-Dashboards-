import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Assume df is already defined above
# Style settings (define or adjust as needed)
MATERIAL_STYLE = {
    'primary': '#2196F3',
    'accent': '#FFC107',
}

with tab4:
    st.subheader("Intern Profile Cards")

    # Ensure pitch/reply columns are numeric
    filtered_df['Total pitches'] = pd.to_numeric(filtered_df['Total pitches'], errors='coerce').fillna(0).astype(int)
    filtered_df['Total Reply Recived'] = pd.to_numeric(filtered_df['Total Reply Recived'], errors='coerce').fillna(0).astype(int)

    for i, row in filtered_df.iterrows():
        with st.expander(f"{row['Intern Name']} - {row['Pitch Company']}"):
            col1, col2 = st.columns([3, 2])

            with col1:
                st.markdown(f"**University:** {row.get('College/University', 'N/A')}")
                st.markdown(f"**Grade:** {row.get('Grade', 'N/A')}")
                total_pitches = row['Total pitches']
                replies_received = row['Total Reply Recived']

                # Calculate reply percentage
                reply_percentage = (replies_received / total_pitches * 100) if total_pitches > 0 else 0
                st.markdown(f"**Replies Received (%):** {reply_percentage:.1f}%")
                st.markdown(f"**Status:** {row.get('Evaluation Status', 'N/A')}")
                st.markdown(f"**Comments:** {row.get('Committee Comments', 'No comments')}")

            with col2:
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
