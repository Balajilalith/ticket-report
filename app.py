import streamlit as st
import pandas as pd
import numpy as np
import io
from datetime import datetime, timedelta
import plotly.express as px

# Function to process uploaded file and generate reports
def process_file(uploaded_file):
    # Load the uploaded file
    file_extension = uploaded_file.name.split('.')[-1].lower()
    if file_extension == 'csv':
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    # Convert date columns to datetime
    df['Created Time (Ticket)'] = pd.to_datetime(df['Created Time (Ticket)'], format='%d %b %Y %I:%M %p')
    df['Ticket Closed Time'] = pd.to_datetime(df['Ticket Closed Time (Ticket)'], format='%d %b %Y %I:%M %p', errors='coerce')

    # Define the teams
    teams = ['kiCredit', 'Alerts']

    # Initialize the report dictionaries
    reports = {team: {'P1': {'Not an Issue': 0, 'Closed Tickets': 0, 'Expected TAT': 1, 'Actual TAT': 'NA'},
                      'P2': {'Not an Issue': 0, 'Closed Tickets': 0, 'Expected TAT': 3, 'Actual TAT': 'NA'},
                      'P3': {'Not an Issue': 0, 'Closed Tickets': 0, 'Expected TAT': 7, 'Actual TAT': 'NA'},
                      'P4': {'Not an Issue': 0, 'Closed Tickets': 0, 'Expected TAT': 30, 'Actual TAT': 'NA'}}
               for team in teams}

    # Process each team
    for team in teams:
        if team == 'Alerts':
            filter_subject = 'ElastAlert'
        else:
            filter_subject = None

        for priority in ['P1', 'P2', 'P3', 'P4']:
            # Filter data by team
            if filter_subject:
                filtered_df = df[(df['Subject'].str.contains(filter_subject, na=False)) & 
                                 (df['Priority (Ticket)'] == priority)]
            else:
                filtered_df = df[(df['Priority (Ticket)'] == priority)]

            # Count Not an Issue
            not_an_issue_count = len(filtered_df[(filtered_df['Category (Ticket)'].isin(['Query', 'Access Request'])) & 
                                                 (filtered_df['Status (Ticket)'].isin(['Closed', 'Duplicate']))])
            reports[team][priority]['Not an Issue'] = not_an_issue_count

            # Count Closed Tickets
            closed_tickets_count = len(filtered_df[filtered_df['Status (Ticket)'].isin(['Closed', 'Duplicate'])])
            reports[team][priority]['Closed Tickets'] = closed_tickets_count

            # Calculate Actual TAT
            if closed_tickets_count > 0:
                filtered_df['TAT'] = (filtered_df['Ticket Closed Time (Ticket)'] - filtered_df['Created Time (Ticket)']).dt.days + 1
                actual_tat = filtered_df['TAT'].mean()
                reports[team][priority]['Actual TAT'] = round(actual_tat, 2)
            else:
                reports[team][priority]['Actual TAT'] = 'NA'

    # Generate summary report
    summary_report_data = [
        {'Teams': team, 'Priority': priority, 'Not an Issue': reports[team][priority]['Not an Issue'],
         'Closed Tickets': reports[team][priority]['Closed Tickets'], 'Expected TAT': reports[team][priority]['Expected TAT'],
         'Actual TAT': reports[team][priority]['Actual TAT']}
        for team in teams for priority in ['P1', 'P2', 'P3', 'P4']
    ]

    summary_report_df = pd.DataFrame(summary_report_data)
    
    # Exclude 'ElastAlert' from the summary report
    df_summary = df[~df['Subject'].str.contains('ElastAlert', na=False)]

    # Generate detailed summary report
    detailed_summary_report_data = [
        {'Teams': team, 'Priority': priority, 'Not an Issue': len(df_summary[(df_summary['Priority (Ticket)'] == priority) & 
                                                                              (df_summary['Category (Ticket)'].isin(['Query', 'Access Request'])) & 
                                                                              (df_summary['Status (Ticket)'].isin(['Closed', 'Duplicate']))]),
         'Closed Tickets': len(df_summary[(df_summary['Priority (Ticket)'] == priority) & 
                                          (df_summary['Status (Ticket)'].isin(['Closed', 'Duplicate']))]),
         'Expected TAT': reports[team][priority]['Expected TAT'],
         'Actual TAT': reports[team][priority]['Actual TAT']}
        for team in teams for priority in ['P1', 'P2', 'P3', 'P4']
    ]

    detailed_summary_report_df = pd.DataFrame(detailed_summary_report_data)

    # Generate Alerts report
    alerts_df = df[df['Subject'].str.contains('ElastAlert', na=False)]
    alerts_report_data = [
        {'Priority': priority, 'Tickets raised': len(alerts_df[alerts_df['Priority (Ticket)'] == priority]),
         'Not an Issue': len(alerts_df[(alerts_df['Priority (Ticket)'] == priority) & 
                                       (alerts_df['Status (Ticket)'].isin(['Closed', 'Duplicate']))]),
         'Bugs': len(alerts_df[(alerts_df['Priority (Ticket)'] == priority) & 
                               (alerts_df['Category (Ticket)'] == 'Bug')]),
         'Tickets Closed': len(alerts_df[(alerts_df['Priority (Ticket)'] == priority) & 
                                         (alerts_df['Status (Ticket)'].isin(['Closed', 'Duplicate']))]),
         'Expected TAT': reports['Alerts'][priority]['Expected TAT'],
         'Actual TAT': reports['Alerts'][priority]['Actual TAT'],
         'Pending Tickets': len(alerts_df[(alerts_df['Priority (Ticket)'] == priority) & 
                                          (alerts_df['Status (Ticket)'].isin(['PS Inprogress', 'UnderDev']))]),
         'Target ETA': 'NA' if len(alerts_df[(alerts_df['Priority (Ticket)'] == priority) & 
                                             (alerts_df['Status (Ticket)'].isin(['PS Inprogress', 'UnderDev']))]) == 0 else
                       (alerts_df['Created Time (Ticket)'] + pd.DateOffset(days=reports['Alerts'][priority]['Expected TAT']))
                       .apply(lambda x: x + pd.offsets.Week(weekday=4))  # Friday of upcoming week
                       .dt.strftime('%d %b %Y')
        }
        for priority in ['P1', 'P2', 'P3', 'P4']
    ]

    alerts_report_df = pd.DataFrame(alerts_report_data)

    return summary_report_df, detailed_summary_report_df, alerts_report_df, df

# Streamlit UI
st.title('Ticket Report Generation')

uploaded_file = st.file_uploader("Upload your file (CSV, XLSX, XLS)", type=['csv', 'xlsx', 'xls'])

if uploaded_file:
    summary_report_df, detailed_summary_report_df, alerts_report_df, df = process_file(uploaded_file)

    # Display summary report
    st.header('Summary Report')
    st.dataframe(summary_report_df)

    # Display detailed summary report
    st.header('Detailed Summary Report')
    st.dataframe(detailed_summary_report_df)

    # Display alerts report
    st.header('Alerts Report')
    st.dataframe(alerts_report_df)

    # Generate and display graphs
    st.header('Graphs')

    # Summary Report Graph
    summary_fig = px.bar(summary_report_df, x='Teams', y=['Not an Issue', 'Closed Tickets'],
                         color='Priority', barmode='group', title='Summary Report')
    st.plotly_chart(summary_fig)

    # Detailed Summary Report Graph
    detailed_summary_fig = px.bar(detailed_summary_report_df, x='Teams', y=['Not an Issue', 'Closed Tickets'],
                                  color='Priority', barmode='group', title='Detailed Summary Report')
    st.plotly_chart(detailed_summary_fig)

    # Alerts Report Graph
    alerts_fig = px.bar(alerts_report_df, x='Priority', y=['Tickets raised', 'Not an Issue', 'Bugs', 'Tickets Closed'],
                        barmode='group', title='Alerts Report')
    st.plotly_chart(alerts_fig)

    # Provide download links for the reports
    st.header('Download Reports')

    # Summary Report
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

    # Detailed Summary Report
    detailed_summary_excel = io.BytesIO()
    with pd.ExcelWriter(detailed_summary_excel, engine='xlsxwriter') as writer:
        detailed_summary_report_df.to_excel(writer, index=False)
    detailed_summary_excel.seek(0)
    st.download_button(
        label="Download Detailed Summary Report",
        data=detailed_summary_excel,
        file_name="detailed_summary_report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # Alerts Report
    alerts_excel = io.BytesIO()
    with pd.ExcelWriter(alerts_excel, engine='xlsxwriter') as writer:
        alerts_report_df.to_excel(writer, index=False)
    alerts_excel.seek(0)
    st.download_button(
        label="Download Alerts Report",
        data=alerts_excel,
        file_name="alerts_report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    
    # Original Data Report
    original_data_excel = io.BytesIO()
    with pd.ExcelWriter(original_data_excel, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    original_data_excel.seek(0)
    st.download_button(
        label="Download Original Data Report",
        data=original_data_excel,
        file_name="original_data_report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
