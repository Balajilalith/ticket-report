import streamlit as st
import pandas as pd
import numpy as np
import io
from datetime import timedelta

# Function to process the file and generate the reports
def process_file(uploaded_file, holidays):
    # Load data from file based on file extension
    if uploaded_file.name.endswith('.xlsx') or uploaded_file.name.endswith('.xls'):
        df = pd.read_excel(uploaded_file)
    elif uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        st.error('Unsupported file type. Please upload an Excel or CSV file.')
        return None, None, None, None

    # Convert date columns to datetime
    df['Created Time (Ticket)'] = pd.to_datetime(df['Created Time (Ticket)'], format='%d %b %Y %I:%M %p', errors='coerce')
    df['Ticket Closed Time (Ticket)'] = pd.to_datetime(df['Ticket Closed Time (Ticket)'], format='%d %b %Y %I:%M %p', errors='coerce')

    # Exclude tickets with "ElastAlert" in the subject for the Summary Report
    summary_df = df[~df['Subject'].str.contains('ElastAlert', na=False)]

    # Detailed Summary Report (for reference only, no changes made here)
    detailed_summary_df = summary_df.copy()

    # Alerts Report: Filter data for tickets with "ElastAlert" in the subject
    alerts_df = df[df['Subject'].str.contains('ElastAlert', na=False)]

    # Adjust TAT calculation to exclude holidays
    def calculate_tat(row):
        if pd.isna(row['Ticket Closed Time (Ticket)']):
            return np.nan
        created_time = row['Created Time (Ticket)']
        closed_time = row['Ticket Closed Time (Ticket)']
        tat_days = np.busday_count(created_time.date(), closed_time.date(), holidays=holidays)
        return max(tat_days, 1)  # Ensure a minimum of 1 day for TAT

    summary_df['Actual TAT'] = summary_df.apply(calculate_tat, axis=1)

    # Additional Reports/Graphs can be generated here

    return summary_df, detailed_summary_df, alerts_df, df

# Streamlit app code
st.title('Ticket Report Generator')

# File upload
uploaded_file = st.file_uploader("Upload your Excel or CSV file", type=["xlsx", "xls", "csv"])

# Holiday selection
holidays = st.multiselect("Select holidays (if any) within the reporting week", options=pd.date_range(start='2024-08-10', end='2024-08-16').tolist())

# Convert holidays to numpy array format for np.busday_count
holidays = np.array([h.date() for h in holidays])

if uploaded_file:
    summary_report_df, detailed_summary_report_df, alerts_report_df, df = process_file(uploaded_file, holidays)

    if summary_report_df is not None:
        # Download link for Summary Report
        summary_excel = io.BytesIO()
        with pd.ExcelWriter(summary_excel, engine='xlsxwriter') as writer:
            summary_report_df.to_excel(writer, index=False)
        summary_excel.seek(0)
        st.download_button(
            label="Download Summary Report",
            data=summary_excel,
            file_name='summary_report.xlsx'
        )

        # Download link for Detailed Summary Report
        detailed_summary_excel = io.BytesIO()
        with pd.ExcelWriter(detailed_summary_excel, engine='xlsxwriter') as writer:
            detailed_summary_report_df.to_excel(writer, index=False)
        detailed_summary_excel.seek(0)
        st.download_button(
            label="Download Detailed Summary Report",
            data=detailed_summary_excel,
            file_name='detailed_summary_report.xlsx'
        )

        # Download link for Alerts Report
        alerts_excel = io.BytesIO()
        with pd.ExcelWriter(alerts_excel, engine='xlsxwriter') as writer:
            alerts_report_df.to_excel(writer, index=False)
        alerts_excel.seek(0)
        st.download_button(
            label="Download Alerts Report",
            data=alerts_excel,
            file_name='alerts_report.xlsx'
        )

        # Download link for Complete Data (Original)
        original_excel = io.BytesIO()
        with pd.ExcelWriter(original_excel, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
        original_excel.seek(0)
        st.download_button(
            label="Download Complete Data (Original)",
            data=original_excel,
            file_name='complete_data.xlsx'
        )

        # Placeholder for Graphs/Additional Reports
        st.subheader("Graphs/Additional Reports")
        st.write("Graphs will be generated based on the data.")

        # (Placeholder for graph code, depending on requirements)
