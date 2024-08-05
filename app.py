import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
import numpy as np

# Function to calculate the next Friday from a given date
def get_next_friday(start_date):
    days_ahead = 4 - start_date.weekday()  # Friday is the 4th day of the week
    if days_ahead <= 0:
        days_ahead += 7
    return start_date + timedelta(days=days_ahead)

# Streamlit app
st.title("Ticket Report Generator")

uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)

    # Convert date columns to datetime
    df['Created Time (Ticket)'] = pd.to_datetime(df['Created Time (Ticket)'], format='%d %b %Y %I:%M %p')
    df['Ticket Closed Time'] = pd.to_datetime(df['Ticket Closed Time'], format='%d %b %Y %I:%M %p', errors='coerce')

    # Report 1: Summary Report
    st.header("Summary Report")

    # Exclude ElastAlert tickets
    df_filtered = df[~df['Subject'].str.contains('ElastAlert', case=False, na=False)]

    # Define the expected TAT for each priority
    expected_tat = {'P1': 1, 'P2': 3, 'P3': 7, 'P4': 30}

    # Initialize the report data
    summary_report_data = []

    # Process each priority
    for priority in ['P1', 'P2', 'P3', 'P4']:
        priority_df = df_filtered[df_filtered['Priority (Ticket)'].str.contains(priority, case=False)]

        # Tickets Raised
        tickets_raised = len(priority_df)

        # Not an Issue
        not_an_issue_df = priority_df[priority_df['Status (Ticket)'].str.lower().isin(['closed', 'duplicate'])]
        not_an_issue = len(not_an_issue_df)

        # Bugs
        bugs = len(priority_df[priority_df['Category (Ticket)'].str.lower() == 'bug'])

        # Tickets Closed
        closed_tickets_df = priority_df[priority_df['Status (Ticket)'].str.lower().isin(['closed', 'duplicate'])]
        closed_tickets = len(closed_tickets_df)

        # Actual TAT
        if closed_tickets > 0:
            closed_tickets_df['TAT'] = (closed_tickets_df['Ticket Closed Time'] - closed_tickets_df['Created Time (Ticket)']).dt.days
            closed_tickets_df['TAT'] = closed_tickets_df['TAT'].apply(lambda x: max(x, 1))  # Ensure minimum TAT is 1 day
            actual_tat = closed_tickets_df['TAT'].mean()
        else:
            actual_tat = 'NA'

        # Pending Tickets
        pending_tickets_df = priority_df[priority_df['Status (Ticket)'].str.lower().isin(['open', 'ps inprogress'])]
        pending_tickets = len(pending_tickets_df)

        # Target ETA
        if pending_tickets > 0:
            next_friday = get_next_friday(datetime.now())
            target_eta = next_friday.strftime('%d %b %Y')
        else:
            target_eta = 'NA'

        # Append data to the report
        summary_report_data.append({
            'Ticket Priority': priority,
            'Tickets Raised': tickets_raised,
            'Not an Issue': not_an_issue,
            'Bugs': bugs,
            'Tickets Closed': closed_tickets,
            'Expected TAT': expected_tat[priority],
            'Actual TAT': round(actual_tat, 2) if actual_tat != 'NA' else actual_tat,
            'Pending Tickets': pending_tickets,
            'Target ETA': target_eta
        })

    # Create a DataFrame for the report
    summary_report_df = pd.DataFrame(summary_report_data)

    # Display the final report
    st.write(summary_report_df)

    # Report 2: Detailed Report
    st.header("Detailed Report")

    # Initialize the report data
    detailed_report_data = []

    # Process each priority
    for priority in ['P1', 'P2', 'P3', 'P4']:
        priority_df = df[df['Priority (Ticket)'].str.contains(priority, case=False)]

        # Not an Issue
        not_an_issue = len(priority_df[priority_df['Status (Ticket)'].str.lower().isin(['closed', 'duplicate'])])

        # Tickets Closed
        closed_tickets = len(priority_df[priority_df['Status (Ticket)'].str.lower().isin(['closed', 'duplicate'])])

        # Actual TAT
        if closed_tickets > 0:
            closed_tickets_df = priority_df[priority_df['Status (Ticket)'].str.lower().isin(['closed', 'duplicate'])]
            closed_tickets_df['TAT'] = (closed_tickets_df['Ticket Closed Time'] - closed_tickets_df['Created Time (Ticket)']).dt.days
            closed_tickets_df['TAT'] = closed_tickets_df['TAT'].apply(lambda x: max(x, 1))  # Ensure minimum TAT is 1 day
            actual_tat = closed_tickets_df['TAT'].mean()
        else:
            actual_tat = 'NA'

        # Append data to the report
        detailed_report_data.append({
            'Priority': priority,
            'Not an Issue': not_an_issue,
            'Closed Tickets': closed_tickets,
            'Expected TAT': expected_tat[priority],
            'Actual TAT': round(actual_tat, 2) if actual_tat != 'NA' else actual_tat
        })

    # Create a DataFrame for the detailed report
    detailed_report_df = pd.DataFrame(detailed_report_data)

    # Display the detailed report
    st.write(detailed_report_df)

    # Provide download link for the summary report
    st.download_button(
        label="Download Summary Report as Excel",
        data=summary_report_df.to_excel(index=False),
        file_name='summary_report.xlsx'
    )

    # Provide download link for the detailed report
    st.download_button(
        label="Download Detailed Report as Excel",
        data=detailed_report_df.to_excel(index=False),
        file_name='detailed_report.xlsx'
    )
