import streamlit as st
import pandas as pd
import numpy as np
import io
from datetime import datetime, timedelta
import plotly.express as px

# Function to calculate business days
def add_business_days(start_date, days):
    current_date = start_date
    while days > 0:
        current_date += timedelta(days=1)
        if current_date.weekday() < 5:  # Monday to Friday are considered business days
            days -= 1
    return current_date

# Function to handle file upload and data extraction
def load_file(uploaded_file):
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    return df

# Function to generate the summary report
def generate_summary_report(df):
    priority_order = ['P1-Urgent', 'P2-High', 'P3-Medium', 'P4-Low']
    priority_expected_tat = {'P1-Urgent': 1, 'P2-High': 3, 'P3-Medium': 7, 'P4-Low': 30}
    
    summary_report = {
        'Ticket Priority': [],
        'Tickets Raised': [],
        'Not an Issue': [],
        'Bugs': [],
        'Tickets Closed': [],
        'Expected TAT': [],
        'Actual TAT': [],
        'Pending Tickets': [],
        'Target ETA': []
    }
    
    for priority in priority_order:
        filtered_df = df[(df['Priority (Ticket)'] == priority) & (~df['Subject'].str.contains('ElastAlert', na=False))]
        tickets_raised = len(filtered_df)
        not_an_issue = len(filtered_df[(filtered_df['Status (Ticket)'].isin(['Closed', 'Duplicate']))])
        bugs = len(filtered_df[(filtered_df['Category (Ticket)'] == 'Bug')])
        tickets_closed = len(filtered_df[(filtered_df['Status (Ticket)'].isin(['Closed', 'Duplicate']))])
        pending_tickets = len(filtered_df[~filtered_df['Status (Ticket)'].isin(['Closed', 'Duplicate'])])
        actual_tat = 'NA'
        if tickets_closed > 0:
            filtered_df['TAT'] = (pd.to_datetime(filtered_df['Ticket Closed Time']) - pd.to_datetime(filtered_df['Created Time (Ticket)'])).dt.days + 1
            actual_tat = round(filtered_df['TAT'].mean(), 2)
        
        target_eta = 'NA'
        if pending_tickets > 0:
            last_open_ticket_date = pd.to_datetime(filtered_df[~filtered_df['Status (Ticket)'].isin(['Closed', 'Duplicate'])]['Created Time (Ticket)']).max()
            target_eta = add_business_days(last_open_ticket_date, priority_expected_tat[priority.split('-')[1].strip()]).strftime('%d %b %Y')

        summary_report['Ticket Priority'].append(priority)
        summary_report['Tickets Raised'].append(tickets_raised)
        summary_report['Not an Issue'].append(not_an_issue)
        summary_report['Bugs'].append(bugs)
        summary_report['Tickets Closed'].append(tickets_closed)
        summary_report['Expected TAT'].append(priority_expected_tat[priority.split('-')[1].strip()])
        summary_report['Actual TAT'].append(actual_tat)
        summary_report['Pending Tickets'].append(pending_tickets)
        summary_report['Target ETA'].append(target_eta)
    
    return pd.DataFrame(summary_report)

# Function to generate the detailed report
def generate_detailed_report(df):
    priority_order = ['P1-Urgent', 'P2-High', 'P3-Medium', 'P4-Low']
    priority_expected_tat = {'P1-Urgent': 1, 'P2-High': 3, 'P3-Medium': 7, 'P4-Low': 30}
    
    detailed_report = {
        'Teams': [],
        'Priority': [],
        'Not an Issue': [],
        'Closed Tickets': [],
        'Expected TAT': [],
        'Actual TAT': []
    }

    for priority in priority_order:
        filtered_df = df[(df['Priority (Ticket)'] == priority) & (~df['Subject'].str.contains('ElastAlert', na=False))]
        not_an_issue = len(filtered_df[(filtered_df['Category (Ticket)'].isin(['Query', 'Access Request']))])
        closed_tickets = len(filtered_df[(filtered_df['Status (Ticket)'].isin(['Closed', 'Duplicate']))])
        actual_tat = 'NA'
        if closed_tickets > 0:
            filtered_df['TAT'] = (pd.to_datetime(filtered_df['Ticket Closed Time']) - pd.to_datetime(filtered_df['Created Time (Ticket)'])).dt.days + 1
            actual_tat = round(filtered_df['TAT'].mean(), 2)
        
        detailed_report['Teams'].append('kiCredit')
        detailed_report['Priority'].append(priority)
        detailed_report['Not an Issue'].append(not_an_issue)
        detailed_report['Closed Tickets'].append(closed_tickets)
        detailed_report['Expected TAT'].append(priority_expected_tat[priority.split('-')[1].strip()])
        detailed_report['Actual TAT'].append(actual_tat)
    
    return pd.DataFrame(detailed_report)

# Function to generate the alerts report
def generate_alerts_report(df):
    priority_order = ['P1-Urgent', 'P2-High', 'P3-Medium', 'P4-Low']
    priority_expected_tat = {'P1-Urgent': 1, 'P2-High': 3, 'P3-Medium': 7, 'P4-Low': 30}
    
    alerts_report = {
        'Teams': [],
        'Priority': [],
        'Not an Issue': [],
        'Closed Tickets': [],
        'Expected TAT': [],
        'Actual TAT': []
    }

    for priority in priority_order:
        filtered_df = df[(df['Priority (Ticket)'] == priority) & (df['Subject'].str.contains('ElastAlert', na=False))]
        not_an_issue = len(filtered_df[(filtered_df['Category (Ticket)'].isin(['Query', 'Access Request']))])
        closed_tickets = len(filtered_df[(filtered_df['Status (Ticket)'].isin(['Closed', 'Duplicate']))])
        actual_tat = 'NA'
        if closed_tickets > 0:
            filtered_df['TAT'] = (pd.to_datetime(filtered_df['Ticket Closed Time']) - pd.to_datetime(filtered_df['Created Time (Ticket)'])).dt.days + 1
            actual_tat = round(filtered_df['TAT'].mean(), 2)
        
        alerts_report['Teams'].append('Alerts')
        alerts_report['Priority'].append(priority)
        alerts_report['Not an Issue'].append(not_an_issue)
        alerts_report['Closed Tickets'].append(closed_tickets)
        alerts_report['Expected TAT'].append(priority_expected_tat[priority.split('-')[1].strip()])
        alerts_report['Actual TAT'].append(actual_tat)
    
    return pd.DataFrame(alerts_report)

# Streamlit app
st.title('Ticket Report Generator')

uploaded_file = st.file_uploader("Upload your ticket data file (CSV, XLSX, or XLS)", type=['csv', 'xlsx', 'xls'])

if uploaded_file:
    df = load_file(uploaded_file)
    
    st.write("### Original Data")
    st.dataframe(df)
    
    summary_report_df = generate_summary_report(df)
    detailed_report_df = generate_detailed_report(df)
    alerts_report_df = generate_alerts_report(df)
    
    st.write("### Summary Report (Excluding ElastAlert)")
    st.dataframe(summary_report_df)
    
    st.write("### Detailed Report")
    st.dataframe(detailed_report_df)
    
    st.write("### Alerts Report (ElastAlert)")
    st.dataframe(alerts_report_df)
    
    # Generate graphs
    st.write("### Graphs")
    
    # Graph for summary report
    fig_summary = px.bar(summary_report_df, x='Ticket Priority', y=['Tickets Raised', 'Not an Issue', 'Bugs', 'Tickets Closed', 'Pending Tickets'], title="Summary Report Graph")
    st.plotly_chart(fig_summary)
    
    # Graph for detailed report
    fig_detailed = px.bar(detailed_report_df, x='Priority', y=['Not an Issue', 'Closed Tickets'], title="Detailed Report Graph")
    st.plotly_chart(fig_detailed)
    
    # Graph for alerts report
    fig_alerts = px.bar(alerts_report_df, x='Priority', y=['Not an Issue', 'Closed Tickets'], title="Alerts Report Graph")
    st.plotly_chart(fig_alerts)
    
    # Save and provide download link for the reports
    summary_excel = io.BytesIO()
    detailed_excel = io.BytesIO()
    alerts_excel = io.BytesIO()
    full_excel = io.BytesIO()

    with pd.ExcelWriter(summary_excel, engine='xlsxwriter') as writer:
        summary_report_df.to_excel(writer, index=False)
    summary_excel.seek(0)

    with pd.ExcelWriter(detailed_excel, engine='xlsxwriter') as writer:
        detailed_report_df.to_excel(writer, index=False)
    detailed_excel.seek(0)

    with pd.ExcelWriter(alerts_excel, engine='xlsxwriter') as writer:
        alerts_report_df.to_excel(writer, index=False)
    alerts_excel.seek(0)
    
    with pd.ExcelWriter(full_excel, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    full_excel.seek(0)

    st.download_button(label='Download Summary Report', data=summary_excel, file_name='summary_report.xlsx')
    st.download_button(label='Download Detailed Report', data=detailed_excel, file_name='detailed_report.xlsx')
    st.download_button(label='Download Alerts Report', data=alerts_excel, file_name='alerts_report.xlsx')
    st.download_button(label='Download Full Report', data=full_excel, file_name='full_report.xlsx')
