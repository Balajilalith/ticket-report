import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
import io
import plotly.express as px

st.title("Ticket Report Generator")

uploaded_file = st.file_uploader("Upload Excel or CSV", type=["xlsx","xls","csv"])

def get_next_friday(start_date):
    days_ahead = 4 - start_date.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    return start_date + timedelta(days_ahead)

if uploaded_file:

    # Read file safely
    try:
        if uploaded_file.name.endswith(("xlsx","xls")):
            df = pd.read_excel(uploaded_file, engine="openpyxl")
        else:
            df = pd.read_csv(uploaded_file)
    except Exception as e:
        st.error(f"File reading error: {e}")
        st.stop()

    # Clean column names
    df.columns = df.columns.str.strip()

    # Required columns
    required_cols = [
        'Created Time (Ticket)',
        'Ticket Closed Time',
        'Subject',
        'Priority (Ticket)',
        'Status (Ticket)',
        'Category (Ticket)'
    ]

    missing_cols = [col for col in required_cols if col not in df.columns]

    if missing_cols:
        st.error(f"Missing columns in file: {missing_cols}")
        st.write("Available columns:", df.columns.tolist())
        st.stop()

    # Convert dates safely
    df['Created Time (Ticket)'] = pd.to_datetime(
        df['Created Time (Ticket)'], errors='coerce'
    )

    df['Ticket Closed Time'] = pd.to_datetime(
        df['Ticket Closed Time'], errors='coerce'
    )

    # Remove ElastAlert tickets
    df_non_elastalert = df[~df['Subject'].str.contains("ElastAlert", case=False, na=False)]

    expected_tat = {'P1':1,'P2':3,'P3':7,'P4':30}

    # ---------------- SUMMARY REPORT ----------------

    st.header("Summary Report")

    summary_data = []

    for priority in ['P1','P2','P3','P4']:

        priority_df = df_non_elastalert[
            df_non_elastalert['Priority (Ticket)'].str.contains(priority, case=False, na=False)
        ]

        closed_df = priority_df[
            priority_df['Status (Ticket)'].str.lower().isin(['closed','duplicate'])
        ].copy()

        not_issue = closed_df[
            closed_df['Category (Ticket)'].str.lower().isin(['query','access request'])
        ].shape[0]

        closed_count = closed_df.shape[0]

        if closed_count > 0:
            closed_df['TAT'] = (
                closed_df['Ticket Closed Time'] - closed_df['Created Time (Ticket)']
            ).dt.days + 1
            actual_tat = round(closed_df['TAT'].mean(),2)
        else:
            actual_tat = None

        summary_data.append({
            "Priority":priority,
            "Not an Issue":not_issue,
            "Closed Tickets":closed_count,
            "Expected TAT":expected_tat[priority],
            "Actual TAT":actual_tat
        })

    summary_df = pd.DataFrame(summary_data)

    st.dataframe(summary_df)

    # Download summary
    summary_buffer = io.BytesIO()
    summary_df.to_excel(summary_buffer,index=False)
    summary_buffer.seek(0)

    st.download_button(
        "Download Summary",
        summary_buffer,
        "summary_report.xlsx"
    )

    # ---------------- DETAILED REPORT ----------------

    st.header("Detailed Report")

    detailed_data = []

    for priority in ['P1','P2','P3','P4']:

        priority_df = df_non_elastalert[
            df_non_elastalert['Priority (Ticket)'].str.contains(priority, case=False, na=False)
        ]

        raised = len(priority_df)

        closed_df = priority_df[
            priority_df['Status (Ticket)'].str.lower().isin(['closed','duplicate'])
        ].copy()

        bugs = priority_df[
            priority_df['Category (Ticket)'].str.lower() == 'bug'
        ].shape[0]

        not_issue = closed_df.shape[0]

        if not closed_df.empty:
            closed_df['TAT'] = (
                closed_df['Ticket Closed Time'] - closed_df['Created Time (Ticket)']
            ).dt.days + 1
            actual_tat = round(closed_df['TAT'].mean(),2)
        else:
            actual_tat = None

        pending_df = priority_df[
            ~priority_df['Status (Ticket)'].str.lower().isin(['closed','duplicate'])
        ].copy()

        if not pending_df.empty:
            pending_df['Target ETA'] = pending_df['Created Time (Ticket)'].apply(get_next_friday)
            target_eta = pending_df['Target ETA'].max()
        else:
            target_eta = None

        detailed_data.append({
            "Priority":priority,
            "Tickets Raised":raised,
            "Not an Issue":not_issue,
            "Bugs":bugs,
            "Tickets Closed":len(closed_df),
            "Expected TAT":expected_tat[priority],
            "Actual TAT":actual_tat,
            "Pending Tickets":len(pending_df),
            "Target ETA":target_eta
        })

    detailed_df = pd.DataFrame(detailed_data)

    st.dataframe(detailed_df)

    # Download detailed
    detailed_buffer = io.BytesIO()
    detailed_df.to_excel(detailed_buffer,index=False)
    detailed_buffer.seek(0)

    st.download_button(
        "Download Detailed",
        detailed_buffer,
        "detailed_report.xlsx"
    )

    # ---------------- ALERT REPORT ----------------

    st.header("Alerts Report")

    alerts_df = df[df['Subject'].str.contains("ElastAlert", case=False, na=False)]

    alerts_summary = alerts_df.groupby('Priority (Ticket)').size().reset_index(name='Count')

    st.dataframe(alerts_summary)

    # ---------------- GRAPHS ----------------

    st.header("Graphs")

    fig = px.bar(summary_df, x="Priority", y="Closed Tickets", title="Closed Tickets by Priority")
    st.plotly_chart(fig)
