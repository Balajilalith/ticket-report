import streamlit as st
import pandas as pd
import numpy as np
import io
import calendar
from datetime import datetime, timedelta

# Function to process the uploaded file and generate reports
def process_file(uploaded_file, holidays):
    # Load the file
    df = pd.read_excel(uploaded_file)
    
    # Convert dates
    df['Created Time'] = pd.to_datetime(df['Created Time (Ticket)'], format='%d %b %Y %I:%M %p', errors='coerce')
    df['Ticket Closed Time'] = pd.to_datetime(df['Ticket Closed Time (Ticket)'], format='%d %b %Y %I:%M %p', errors='coerce')
    
    # Filter out "ElastAlert" from Summary Report
    summary_df = df[~df['Subject'].str.contains("ElastAlert", na=False)]
    
    # Add 1 day minimum TAT and calculate Actual TAT
    df['Actual TAT'] = (df['Ticket Closed Time'] - df['Created Time']).dt.days + 1
    
    # Apply holiday logic - remove holiday dates from Actual TAT
    if holidays:
        for holiday in holidays:
            summary_df['Actual TAT'] = summary_df.apply(lambda row: row['Actual TAT'] - 1 
                                                        if holiday >= row['Created Time'] and holiday <= row['Ticket Closed Time'] 
                                                        else row['Actual TAT'], axis=1)

    # Generate Detailed Summary Report
    detailed_summary_df = summary_df.groupby(['Priority (Ticket)']).agg(
        Tickets_Raised=('Ticket Id', 'count'),
        Not_an_Issue=('Status (Ticket)', lambda x: (x == 'Closed').sum() + (x == 'Duplicate').sum()),
        Bugs=('Category (Ticket)', lambda x: (x == 'Bug').sum()),
        Tickets_Closed=('Status (Ticket)', lambda x: (x == 'Closed').sum() + (x == 'Duplicate').sum()),
        Expected_TAT=('Priority (Ticket)', lambda x: get_expected_tat(x)),
        Actual_TAT=('Actual TAT', 'mean'),
        Pending_Tickets=('Status (Ticket)', lambda x: (x == 'PS Inprogress').sum()),
        Target_ETA=('Created Time', lambda x: calculate_target_eta(x))
    ).reset_index()

    # Generate Alerts Report
    alerts_df = df[df['Subject'].str.contains("ElastAlert", na=False)]
    alerts_summary_df = alerts_df.groupby(['Priority (Ticket)']).agg(
        Tickets_Raised=('Ticket Id', 'count'),
        Not_an_Issue=('Status (Ticket)', lambda x: (x == 'Closed').sum() + (x == 'Duplicate').sum()),
        Bugs=('Category (Ticket)', lambda x: (x == 'Bug').sum()),
        Tickets_Closed=('Status (Ticket)', lambda x: (x == 'Closed').sum() + (x == 'Duplicate').sum()),
        Expected_TAT=('Priority (Ticket)', lambda x: get_expected_tat(x)),
        Actual_TAT=('Actual TAT', 'mean'),
        Pending_Tickets=('Status (Ticket)', lambda x: (x == 'PS Inprogress').sum()),
        Target_ETA=('Created Time', lambda x: calculate_target_eta(x))
    ).reset_index()

    return summary_df, detailed_summary_df, alerts_summary_df

# Function to get expected TAT based on priority
def get_expected_tat(priority):
    if 'P1' in priority:
        return 1
    elif 'P2' in priority:
        return 3
    elif 'P3' in priority:
        return 7
    elif 'P4' in priority:
        return 30
    else:
        return np.nan

# Function to calculate Target ETA
def calculate_target_eta(created_times):
    return created_times.apply(lambda x: next_friday(x) if pd.notna(x) else np.nan)

# Function to find the next Friday after the given date
def next_friday(date):
    days_ahead = 4 - date.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    return date + timedelta(days=days_ahead)

# Streamlit app logic
st.title("Ticket Report Generator")

uploaded_file = st.file_uploader("Choose an Excel file", type=["xls", "xlsx", "csv"])

# Date picker for selecting holidays
holidays = st.multiselect("Select Holidays", pd.date_range(start="2024-01-01", end="2024-12-31"), format_func=lambda x: x.strftime('%d %b %Y'))

if uploaded_file is not None:
    summary_report_df, detailed_summary_report_df, alerts_report_df = process_file(uploaded_file, holidays)

    # Show summary report
    st.subheader("Summary Report")
    st.dataframe(summary_report_df)

    # Provide download link for the summary report
    summary_excel = io.BytesIO()
    with pd.ExcelWriter(summary_excel, engine='xlsxwriter') as writer:
        summary_report_df.to_excel(writer, index=False)
    summary_excel.seek(0)
    st.download_button(
        label="Download Summary Report",
        data=summary_excel,
        file_name='summary_report.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

    # Show detailed summary report
    st.subheader("Detailed Summary Report")
    st.dataframe(detailed_summary_report_df)

    detailed_summary_excel = io.BytesIO()
    with pd.ExcelWriter(detailed_summary_excel, engine='xlsxwriter') as writer:
        detailed_summary_report_df.to_excel(writer, index=False)
    detailed_summary_excel.seek(0)
    st.download_button(
        label="Download Detailed Summary Report",
        data=detailed_summary_excel,
        file_name='detailed_summary_report.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

    # Show alerts report
    st.subheader("Alerts Report")
    st.dataframe(alerts_report_df)

    alerts_excel = io.BytesIO()
    with pd.ExcelWriter(alerts_excel, engine='xlsxwriter') as writer:
        alerts_report_df.to_excel(writer, index=False)
    alerts_excel.seek(0)
    st.download_button(
        label="Download Alerts Report",
        data=alerts_excel,
        file_name='alerts_report.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

