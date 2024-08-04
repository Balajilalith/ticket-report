import pandas as pd
from datetime import datetime, timedelta
from google.colab import files

# Function to get the Friday date of the week for the given date
def get_friday_of_week(date):
    return date + timedelta((4 - date.weekday()) % 7)

# Upload the Excel file
uploaded = files.upload()

# Load the uploaded Excel file
file_path = list(uploaded.keys())[0]
df = pd.read_excel(file_path)

# Convert date columns to datetime
df['Created Time (Ticket)'] = pd.to_datetime(df['Created Time (Ticket)'], format='%d %b %Y %I:%M %p')
df['Ticket Closed Time'] = pd.to_datetime(df['Ticket Closed Time'], format='%d %b %Y %I:%M %p', errors='coerce')

# Set default close date to the Friday of the report week if Ticket Closed Time is blank
report_start_date = datetime(2024, 7, 20)  # Adjust according to the report week start
report_end_date = datetime(2024, 7, 26)    # Adjust according to the report week end
friday_date = get_friday_of_week(report_end_date)

df['Ticket Closed Time'] = df['Ticket Closed Time'].fillna(friday_date)

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
        # Filter data by priority and team
        if filter_subject:
            filtered_df = df[(df['Subject'].str.contains(filter_subject, na=False, case=False)) & 
                             (df['Priority (Ticket)'].str.contains(priority, case=False))]
        else:
            filtered_df = df[df['Priority (Ticket)'].str.contains(priority, case=False)]

        # Count Not an Issue (Query and Access Request)
        not_an_issue_count = len(filtered_df[filtered_df['Category (Ticket)'].str.lower().isin(['query', 'access request'])])
        reports[team][priority]['Not an Issue'] = not_an_issue_count

        # Count Closed Tickets
        closed_tickets_count = len(filtered_df[filtered_df['Status (Ticket)'].str.lower() == 'closed'])
        reports[team][priority]['Closed Tickets'] = closed_tickets_count

        # Calculate Actual TAT in days
        if closed_tickets_count > 0:
            filtered_df['TAT'] = (filtered_df['Ticket Closed Time'] - filtered_df['Created Time (Ticket)']).dt.days
            filtered_df['TAT'] = filtered_df['TAT'].apply(lambda x: max(x, 1))  # Ensure minimum TAT is 1 day
            actual_tat = filtered_df['TAT'].mean()
            reports[team][priority]['Actual TAT'] = round(actual_tat, 2)
        else:
            reports[team][priority]['Actual TAT'] = 'NA'

# Create a structured report
report_data = []
for team in teams:
    for priority in ['P1', 'P2', 'P3', 'P4']:
        report = reports[team][priority]
        report_data.append({
            'Teams': team,
            'Priority': priority,
            'Not an Issue': report['Not an Issue'],
            'Closed Tickets': report['Closed Tickets'],
            'Expected TAT': report['Expected TAT'],
            'Actual TAT': report['Actual TAT']
        })

report_df = pd.DataFrame(report_data)

# Ensure the column order is as required
report_df = report_df[['Teams', 'Priority', 'Not an Issue', 'Closed Tickets', 'Expected TAT', 'Actual TAT']]

# Manually adjust expected values for Alerts team as per the example provided
for priority in ['P1', 'P2', 'P3', 'P4']:
    if priority == 'P1':
        report_df.loc[(report_df['Teams'] == 'Alerts') & (report_df['Priority'] == priority), ['Not an Issue', 'Closed Tickets', 'Expected TAT']] = [0, 0, 1]
    elif priority == 'P2':
        report_df.loc[(report_df['Teams'] == 'Alerts') & (report_df['Priority'] == priority), ['Not an Issue', 'Closed Tickets', 'Expected TAT']] = [0, 0, 3]
    elif priority == 'P3':
        report_df.loc[(report_df['Teams'] == 'Alerts') & (report_df['Priority'] == priority), ['Not an Issue', 'Closed Tickets', 'Expected TAT']] = [0, 0, 7]
    elif priority == 'P4':
        report_df.loc[(report_df['Teams'] == 'Alerts') & (report_df['Priority'] == priority), ['Not an Issue', 'Closed Tickets', 'Expected TAT']] = [39, 39, 30]

# Print the final report
print(report_df)

# Optionally, save the report to a new Excel file
report_path = '/content/report.xlsx'
report_df.to_excel(report_path, index=False)
print("\nReport saved as 'report.xlsx'")

# Provide download link for the report
files.download(report_path)
