import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

# Function to find the next Friday from a given date
def get_next_friday(start_date):
    days_ahead = 4 - start_date.weekday()  # Friday is the 4th day of the week
    if days_ahead <= 0:
        days_ahead += 7
    return start_date + timedelta(days=days_ahead)

# Title of the app
st.title("Ticket Priority Report Generator")

# File uploader
uploaded_file = st.file_uploader("Choose an Excel file", type=["xls", "xlsx"])

if uploaded_file:
    # Load the Excel file based on the extension
    if uploaded_file.name.endswith('.xls'):
        df = pd.read_excel(uploaded_file, engine='xlrd')
    else:
        df = pd.read_excel(uploaded_file)

    # Convert date columns to datetime
    df['Created Time (Ticket)'] = pd.to_datetime(df['Created Time (Ticket)'], format='%d %b %Y %I:%M %p')
    df['Ticket Closed Time'] = pd.to_datetime(df['Ticket Closed Time'], format='%d %b %Y %I:%M %p', errors='coerce')

    # Exclude ElastAlert tickets
    df = df[~df['Subject'].str.contains('ElastAlert', case=False, na=False)]

    # Define the expected TAT for each priority
    expected_tat = {'P1': 1, 'P2': 3, 'P3': 7, 'P4': 30}

    # Initialize the report data
    report_data = []

    # Process each priority
    for priority in ['P1', 'P2', 'P3', 'P4']:
        priority_df = df[df['Priority (Ticket)'].str.contains(priority, case=False)]

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
        report_data.append({
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
    report_df = pd.DataFrame(report_data)

    # Display the final report
    st.write(report_df)

    # Provide download link for the report
    report_df.to_excel("ticket_priority_report.xlsx", index=False)
    with open("ticket_priority_report.xlsx", "rb") as file:
        st.download_button(
            label="Download Report as Excel",
            data=file,
            file_name="ticket_priority_report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
