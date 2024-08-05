import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
import io

# Helper functions
def get_next_friday(start_date):
    days_ahead = 4 - start_date.weekday()  # Friday is the 4th day of the week
    if days_ahead <= 0:
        days_ahead += 7
    return start_date + timedelta(days_ahead)

def add_business_days(start_date, days):
    current_date = start_date
    while days > 0:
        current_date += timedelta(1)
        if current_date.weekday() < 5:  # Mon-Fri are considered business days
            days -= 1
    return current_date

# Streamlit app setup
st.title("Ticket Report Generator")
uploaded_file = st.file_uploader("Choose an Excel or CSV file", type=["xlsx", "xls", "csv"])

# File reading
if uploaded_file is not None:
    file_extension = uploaded_file.name.split('.')[-1]
    if file_extension == 'xlsx' or file_extension == 'xls':
        df = pd.read_excel(uploaded_file)
    elif file_extension == 'csv':
        df = pd.read_csv(uploaded_file)

    # Date conversion
    df['Created Time (Ticket)'] = pd.to_datetime(df['Created Time (Ticket)'], format='%d %b %Y %I:%M %p')
    df['Ticket Closed Time'] = pd.to_datetime(df['Ticket Closed Time'], format='%d %b %Y %I:%M %p', errors='coerce')

    # Summary Report
    st.header("Summary Report")
    df_filtered = df[~df['Subject'].str.contains('ElastAlert', case=False, na=False)]
    expected_tat = {'P1': 1, 'P2': 3, 'P3': 7, 'P4': 30}
    summary_report_data = []

    for priority in ['P1', 'P2', 'P3', 'P4']:
        priority_df = df_filtered[df_filtered['Priority (Ticket)'].str.contains(priority, case=False)]

        tickets_raised = len(priority_df)
        not_an_issue_df = priority_df[priority_df['Status (Ticket)'].str.lower().isin(['closed', 'duplicate'])]
        not_an_issue = len(not_an_issue_df)
        bugs = len(priority_df[priority_df['Category (Ticket)'].str.lower() == 'bug'])
        closed_tickets_df = priority_df[priority_df['Status (Ticket)'].str.lower().isin(['closed', 'duplicate'])]
        tickets_closed = len(closed_tickets_df)

        if tickets_closed > 0:
            closed_tickets_df['TAT'] = (closed_tickets_df['Ticket Closed Time'] - closed_tickets_df['Created Time (Ticket)']).dt.days + 1
            actual_tat = closed_tickets_df['TAT'].mean()
        else:
            actual_tat = 'NA'

        pending_tickets = len(priority_df[~priority_df['Status (Ticket)'].str.lower().isin(['closed', 'duplicate'])])

        if pending_tickets > 0:
            target_eta_date = get_next_friday(datetime.now())
        else:
            target_eta_date = 'NA'

        summary_report_data.append({
            'Ticket Priority': priority,
            'Tickets Raised': tickets_raised,
            'Not an Issue': not_an_issue,
            'Bugs': bugs,
            'Tickets Closed': tickets_closed,
            'Expected TAT': expected_tat[priority],
            'Actual TAT': actual_tat,
            'Pending Tickets': pending_tickets,
            'Target ETA': target_eta_date
        })

    summary_report_df = pd.DataFrame(summary_report_data)
    st.dataframe(summary_report_df)

    # Provide download link for the summary report
    summary_excel = io.BytesIO()
    with pd.ExcelWriter(summary_excel, engine='xlsxwriter') as writer:
        summary_report_df.to_excel(writer, index=False)
    summary_excel.seek(0)
    st.download_button(
        label="Download Summary Report",
        data=summary_excel,
        file_name="summary_report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # Detailed Report
    st.header("Detailed Report")
    teams = ['kiCredit', 'Alerts']
    reports = {team: {'P1': {'Not an Issue': 0, 'Closed Tickets': 0, 'Expected TAT': 1, 'Actual TAT': 'NA'},
                      'P2': {'Not an Issue': 0, 'Closed Tickets': 0, 'Expected TAT': 3, 'Actual TAT': 'NA'},
                      'P3': {'Not an Issue': 0, 'Closed Tickets': 0, 'Expected TAT': 7, 'Actual TAT': 'NA'},
                      'P4': {'Not an Issue': 0, 'Closed Tickets': 0, 'Expected TAT': 30, 'Actual TAT': 'NA'}}
               for team in teams}

    for team in teams:
        if team == 'Alerts':
            filter_subject = 'ElastAlert'
        else:
            filter_subject = None

        for priority in ['P1', 'P2', 'P3', 'P4']:
            if filter_subject:
                filtered_df = df[(df['Subject'].str.contains(filter_subject, na=False)) & 
                                 (df['Priority (Ticket)'] == priority)]
            else:
                filtered_df = df[(df['Priority (Ticket)'] == priority)]

            not_an_issue_count = len(filtered_df[filtered_df['Category (Ticket)'] == 'Query'])
            reports[team][priority]['Not an Issue'] = not_an_issue_count

            closed_tickets_count = len(filtered_df[filtered_df['Status (Ticket)'].str.lower().isin(['closed', 'duplicate'])])
            reports[team][priority]['Closed Tickets'] = closed_tickets_count

            if closed_tickets_count > 0:
                filtered_df['TAT'] = (filtered_df['Ticket Closed Time'] - filtered_df['Created Time (Ticket)']).dt.days + 1
                actual_tat = filtered_df['TAT'].mean()
                reports[team][priority]['Actual TAT'] = round(actual_tat, 2)
            else:
                reports[team][priority]['Actual TAT'] = 'NA'

    detailed_report_data = []
    for team in teams:
        for priority in ['P1', 'P2', 'P3', 'P4']:
            report = reports[team][priority]
            detailed_report_data.append({
                'Teams': team,
                'Priority': priority,
                'Not an Issue': report['Not an Issue'],
                'Closed Tickets': report['Closed Tickets'],
                'Expected TAT': report['Expected TAT'],
                'Actual TAT': report['Actual TAT']
            })

    detailed_report_df = pd.DataFrame(detailed_report_data)
    st.dataframe(detailed_report_df)

    # Provide download link for the detailed report
    detailed_excel = io.BytesIO()
    with pd.ExcelWriter(detailed_excel, engine='xlsxwriter') as writer:
        detailed_report_df.to_excel(writer, index=False)
    detailed_excel.seek(0)
    st.download_button(
        label="Download Detailed Report",
        data=detailed_excel,
        file_name="detailed_report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
