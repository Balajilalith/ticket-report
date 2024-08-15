import streamlit as st
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# Define your Streamlit app logic here
st.title("Loan File Generator")

# Function to generate random data
def generate_random_data():
    # Logic to generate random data for all required fields
    return {
        "Group ID": f"C{random.randint(2000000, 2999999)}-G{random.randint(1, 9)}",
        "Bank Account Number": f"{random.randint(100000000000, 999999999999)}",
        "KYC POI Proof No": f"RPS{random.randint(1000000, 9999999)}",
        "KYC POA Proof No": f"RJ{random.randint(100000000, 999999999)}",
        "Partner Application ID": f"RPSTEST{random.randint(1, 99)}P",
        "Partner Customer ID": f"RPSTEST{random.randint(1, 99)}P",
        "Mobile No.": f"{random.randint(9000000000, 9999999999)}",
        "Co-Applicant 1 Mobile Number": f"{random.randint(9000000000, 9999999999)}",
        "Co-Applicant 1 Alternate contact number": f"{random.randint(9000000000, 9999999999)}",
        "Applicant First Name": "Mani",
        "Applicant Last Name": "Shree"
    }

# Display a button for file generation
if st.button("Generate Loan Files"):
    data = generate_random_data()
    st.write("Generated Data:", data)

    # Example to generate DataFrame and display it
    df = pd.DataFrame([data])
    st.dataframe(df)

    # Logic to save the generated data to file if needed
    csv = df.to_csv(index=False)
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name='generated_loan_file.csv',
        mime='text/csv',
    )
