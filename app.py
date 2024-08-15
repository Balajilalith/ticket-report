import streamlit as st
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# Generate random data based on your requirements
def generate_random_data():
    group_id_series = random.randint(2092527, 3092527)
    current_date = datetime.now()
    date_of_application = current_date - timedelta(days=5)

    flat_data = {
        "Group ID": f"C{group_id_series}-G{random.randint(1, 9)}",
        "Bank Account Number": f"{random.randint(100000000000, 999999999999)}",
        "KYC POI Proof No": f"RPS{random.randint(1000000, 9999999)}",
        "KYC POA Proof No": f"RJ{random.randint(100000000, 999999999)}",
        "Partner Application ID": f"RPSTEST{random.randint(1, 99)}P",
        "Partner Customer ID": f"RPSTEST{random.randint(1, 99)}P",
        "Mobile No.": f"{random.randint(9000000000, 9999999999)}",
        "Co-Applicant 1 Mobile Number": f"{random.randint(9000000000, 9999999999)}",
        "Co-Applicant 1 Alternate contact number": f"{random.randint(9000000000, 9999999999)}",
        "Applicant First Name": "Mani",
        "Applicant Last Name": "Shree",
        "Date of Application": date_of_application.strftime("%d/%m/%Y"),
        "Loan Amount": 60000
    }
    
    lrr_data = {
        "NAME_OF_BC": "MIDLAND MICROFIN LIMITED",
        "APPLICATION_DATE": flat_data["Date of Application"],
        "DAY_OF_MEETING": date_of_application.strftime("%A").upper(),
        "NAME_JLG_CENTRE": flat_data["Group ID"].split("-")[0],
        "FIRST_NAME": flat_data["Applicant First Name"],
        "SANCTIONED_DATE": current_date.strftime("%d-%m-%Y"),
        "SANCTIONED_AMT": flat_data["Loan Amount"],
        "URNID": random.randint(10000000, 99999999),
        "APPLICATION_FORM_NO": flat_data["Partner Application ID"],
        "MEMBER_CLIENT_ID": flat_data["Partner Customer ID"]
    }
    
    lbd_data = {
        "PINSTID": lrr_data["URNID"],
        "NAME_OF_BC": lrr_data["NAME_OF_BC"],
        "UNIQUE_REFERENCE_NUMBER": random.randint(1000000, 9999999),
        "CLIENT_ID": lrr_data["MEMBER_CLIENT_ID"],
        "APPLICATION_FORM_NO": lrr_data["APPLICATION_FORM_NO"],
        "CUSTOMER_NAME": lrr_data["FIRST_NAME"],
        "CUSTOMER_ID": lrr_data["MEMBER_CLIENT_ID"],
        "SANCTION_AMOUNT": lrr_data["SANCTIONED_AMT"],
        "SANCTION_DATE": lrr_data["SANCTIONED_DATE"],
        "ACCOUNT_NUMBER": flat_data["Bank Account Number"],
        "ACCOUNT_OPENING_DATE": current_date.strftime("%Y-%m-%d %H:%M:%S"),
        "EXPIRY_DATE": (current_date + timedelta(days=30)).strftime("%d-%m-%Y")
    }
    
    adr_stage1_data = {
        "Partner Loan ID": flat_data["Partner Application ID"],
        "Partner Customer ID": flat_data["Partner Customer ID"],
        "Originator Decision": "APPROVE",
        "Installment Start Date": (current_date + timedelta(days=30)).strftime("%d-%m-%Y"),
        "Interest Start Date": (current_date + timedelta(days=1)).strftime("%d-%m-%Y")
    }
    
    adr_stage2_data = {
        "Partner Loan ID": flat_data["Partner Application ID"],
        "Partner Customer ID": flat_data["Partner Customer ID"],
        "Originator Disbursement Date": current_date.strftime("%d-%m-%Y"),
        "Originator Disbursement Amount": flat_data["Loan Amount"],
        "Bc Reimbursement Ac No": flat_data["Bank Account Number"]
    }

    return flat_data, lrr_data, lbd_data, adr_stage1_data, adr_stage2_data

# Main Streamlit app
st.title("Loan File Generator")

if st.button("Generate Loan Files"):
    flat_data, lrr_data, lbd_data, adr_stage1_data, adr_stage2_data = generate_random_data()
    
    # Create DataFrames
    df_flat = pd.DataFrame([flat_data])
    df_lrr = pd.DataFrame([lrr_data])
    df_lbd = pd.DataFrame([lbd_data])
    df_adr_stage1 = pd.DataFrame([adr_stage1_data])
    df_adr_stage2 = pd.DataFrame([adr_stage2_data])

    # Convert DataFrames to CSV
    flat_csv = df_flat.to_csv(index=False).encode('utf-8')
    lrr_csv = df_lrr.to_csv(index=False).encode('utf-8')
    lbd_csv = df_lbd.to_csv(index=False).encode('utf-8')
    adr_stage1_csv = df_adr_stage1.to_csv(index=False).encode('utf-8')
    adr_stage2_csv = df_adr_stage2.to_csv(index=False).encode('utf-8')

    # Download buttons
    st.download_button("Download Flat File", data=flat_csv, file_name='flat_file.csv', mime='text/csv')
    st.download_button("Download LRR File", data=lrr_csv, file_name='lrr_file.csv', mime='text/csv')
    st.download_button("Download LBD File", data=lbd_csv, file_name='lbd_file.csv', mime='text/csv')
    st.download_button("Download ADR Stage 1 File", data=adr_stage1_csv, file_name='adr_stage1_file.csv', mime='text/csv')
    st.download_button("Download ADR Stage 2 File", data=adr_stage2_csv, file_name='adr_stage2_file.csv', mime='text/csv')
