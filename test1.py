import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import time 
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import random

# Function to get all records from Google Sheets
def get_records():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict({
        "type": "service_account",
        "project_id": st.secrets["google_sheets"]["project_id"],
        "private_key_id": st.secrets["google_sheets"]["private_key_id"],
        "private_key": st.secrets["google_sheets"]["private_key"],
        "client_email": st.secrets["google_sheets"]["client_email"],
        "client_id": st.secrets["google_sheets"]["client_id"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://accounts.google.com/o/oauth2/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": st.secrets["google_sheets"]["client_x509_cert_url"]
    }, scope)
    client = gspread.authorize(creds)
    sheet_id = '1Bsv2n_12_wmWhNI5I5HgCmBWsVyAHFw3rfTGoIrT5ho'
    sheet = client.open_by_key(sheet_id).get_worksheet(4)
    all_records = sheet.get_all_records()  
    print(all_records)
    return all_records


# Function to add a booking to Google Sheets
def add_booking(name, phone_num, email, bookingdate, bookingtime, fee, bookingnum, status):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict({
        "type": "service_account",
        "project_id": st.secrets["google_sheets"]["project_id"],
        "private_key_id": st.secrets["google_sheets"]["private_key_id"],
        "private_key": st.secrets["google_sheets"]["private_key"],
        "client_email": st.secrets["google_sheets"]["client_email"],
        "client_id": st.secrets["google_sheets"]["client_id"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://accounts.google.com/o/oauth2/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": st.secrets["google_sheets"]["client_x509_cert_url"]
    }, scope)
    client = gspread.authorize(creds)
    sheet_id = '1Bsv2n_12_wmWhNI5I5HgCmBWsVyAHFw3rfTGoIrT5ho'
    sheet = client.open_by_key(sheet_id).get_worksheet(4)
    
    # Find the row with the matching booking number
    all_records = sheet.get_all_records()
    for record in all_records:
        if record['Booking number'] == bookingnum:
            row = all_records.index(record) + 2  # Adjust for 1-based indexing and header row
            sheet.update_cell(row, 8, status)  # Update status in column H (8th column)
            return True
    
    return False  # Return false if booking number not found

# Function to check booking details
def check_booking_details(bookingnum, phonenum):
    users = get_records()
    for user in users:
        if user['Booking number'] == int(bookingnum) and user['Phone number'] == int(phonenum):
            return user['Name'], user['Phone number'], user['Email'], user['Booking date'], user['Booking time'], user['Fee'], user['Booking number'], user['Status']
    return 'no user'

# Function to generate PDF invoice
def generate_pdf(name, phone, email, date, time, fee, bknnum, status):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    pdf.cell(200, 10, txt="Booking Invoice", ln=True, align="C")
    pdf.ln(10)
    
    pdf.cell(200, 10, txt=f"Booking Number: {bknnum}", ln=True)
    pdf.cell(200, 10, txt=f"Name: {name}", ln=True)
    pdf.cell(200, 10, txt=f"Phone: {phone}", ln=True)
    pdf.cell(200, 10, txt=f"Email: {email}", ln=True)
    pdf.cell(200, 10, txt=f"Booking Date: {date}", ln=True)
    pdf.cell(200, 10, txt=f"Booking Time: {time}", ln=True)
    pdf.cell(200, 10, txt=f"Fee: ${fee}", ln=True)
    pdf.cell(200, 10, txt=f"Booking Status: {status}", ln=True)

    
    pdf.ln(10)
    pdf.cell(200, 10, txt="Thank you for your booking!", ln=True)
    
    pdf_file = f"invoice_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf.output(pdf_file)
    return pdf_file

# Streamlit UI
st.title("Aeroclub Booking System")

menu = ["Create Booking", "Booking Details"]

# Use the index of the default choice in the options list
default_index = 0  # Index of "Login" in menu (starts from 0)
choice = st.sidebar.selectbox("Menu", menu, index=default_index)

if choice == "Create Booking":
    st.header("Create a Booking")

    selected_date = str(st.date_input("Select a date for booking"))
    selected_time = str(st.time_input("Select a time for the booking"))
    # User details input
    name = st.text_input("Name")
    phone = st.text_input("Phone Number")
    email = st.text_input("Email")

    # Fee for booking
    fee = 100  # Set a fixed fee for the booking

    if st.button("Confirm Booking"):
        if name and phone and email:
            # Generate PDF
            booking_num = random.randint(1000, 9999)
            status = 'open'
            pdf_file = generate_pdf(name, phone, email, selected_date, selected_time, fee)
            add_booking(name, phone, email, selected_date, selected_time, fee, booking_num, status)
            # Download button for PDF
            with open(pdf_file, "rb") as f:
                st.download_button(label="Download Invoice", data=f, file_name=pdf_file, mime="application/pdf")
            
            st.success("Booking confirmed! Your invoice is ready for download.")
        else:
            st.error("Please fill out all the details.")

elif choice == "Booking Details":
    st.header("Bookings")
    
    booking_numb = st.text_input("Booking Number")
    phone = st.text_input("Phone Number")
    
    if st.button("Close Booking"):
        user_details = check_booking_details(booking_numb, phone)
        if user_details != 'no user':
            name, phn, email, bkndate, bkngtime, fee, bkngnum, status = user_details
            if status == 'open':
                status = 'closed'
                add_booking(name, phn, email, bkndate, bkngtime, fee, bkngnum, status)
                st.balloons()
                st.success("Booking has been closed")
                time.sleep(5)
            else:
                st.warning("Booking is already closed")
        else:
            st.error("Error confirming booking number")

    elif st.button("Check Booking Details"):
        user_details = check_booking_details(booking_numb, phone)
        if user_details != 'no user':
            name, phn, email, bkndate, bkngtime, fee, bkngnum, status = user_details
            data = {
                'Name': [name],
                'Phone Number': str(phn),
                'Email': [email],
                'Booking Date': [bkndate],
                'Booking Time': [bkngtime],
                'Fee': [fee],
                'Booking Number': str(bkngnum),
                'Status': [status],
            }
            df = pd.DataFrame(data)
            st.dataframe(df)
        else:
            st.error("Error confirming booking number")
