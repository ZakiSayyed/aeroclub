import streamlit as st
import calendar
from datetime import datetime, date
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import pandas as pd
from fpdf import FPDF
import random
import time

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
    return all_records

# Function to add a booking to Google Sheets
def add_booking(name, phone_num, email, bookingdate, bookingtime, fee, bookingnum, status):
    try:
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

        # Convert selected_time to string
        selected_time_str = bookingtime.strftime("%H:%M %p")  # Format as needed

        # Convert numeric data to strings if necessary
        phone_num = str(phone_num)
        bookingnum = str(bookingnum)
        fee = str(fee)  # Assuming fee is numeric

        sheet.append_row([name, phone_num, email, bookingdate, selected_time_str, fee, bookingnum, status])
        return True
    except Exception as e:
        st.error(f"Error adding booking: {e}")
        return False

# Function to update booking status in Google Sheets
def update_status(bookingnum, status):
    try:
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
            if record['Booking number'] == int(bookingnum):
                row = all_records.index(record) + 2  # Adjust for 1-based indexing and header row
                sheet.update_cell(row, 8, status)  # Update status in column H (8th column)
                return True

        st.warning("Booking number not found")
        return False
    except Exception as e:
        st.error(f"Error updating status: {e}")
        return False

# Function to check booking details
def check_booking_details(bookingnum, phonenum):
    try:
        users = get_records()
        for user in users:
            if user['Booking number'] == int(bookingnum) and user['Phone number'] == int(phonenum):
                return user
        st.warning("Booking details not found")
        return None
    except Exception as e:
        st.error(f"Error checking booking details: {e}")
        return None

# Function to generate PDF invoice
def generate_pdf(name, phone, email, date, time, fee, bknnum, status):
    try:
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
    except Exception as e:
        st.error(f"Error generating PDF: {e}")
        return None

# Streamlit UI
st.title("Aeroclub Booking System")

menu = ["Create Booking", "Booking Details"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Create Booking":
    st.header("Create a Booking")

    # Get all records from Google Sheets
    data = get_records()

    # Convert booking dates to a set for quick lookup
    booked_dates = {
        str(record['Booking date'])
        for record in data
        if 'Booking date' in record and record['Status'].lower() == 'open'
    }

    # Function to check availability
    def check_availability(date_str):
        return date_str not in booked_dates

    # Initialize session state for month, year, and selected date
    if 'month' not in st.session_state:
        st.session_state.month = datetime.now().month
    if 'year' not in st.session_state:
        st.session_state.year = datetime.now().year
    if 'selected_date' not in st.session_state:
        st.session_state.selected_date = None

    # Navigation buttons
    col1, col2, col3, col4, col5 = st.columns(5)
    if col1.button("Back"):
        if st.session_state.month == 1:
            st.session_state.month = 12
            st.session_state.year -= 1
        else:
            st.session_state.month -= 1

    if col5.button("Next"):
        if st.session_state.month == 12:
            st.session_state.month = 1
            st.session_state.year += 1
        else:
            st.session_state.month += 1

    # Display the calendar for the current month and year
    year = st.session_state.year
    month = st.session_state.month
    cal = calendar.Calendar()

    st.write(f"### {calendar.month_name[month]} {year}")

    today = datetime.now()

    if col3.button("Today"):
        # Reset session state variables
        st.session_state.selected_date = date.today().isoformat()
        st.session_state.month = datetime.now().month
        st.session_state.year = datetime.now().year
        
        # Rerun the script to reflect changes
        st.rerun()
    # Fetch day names for the current month and year
    day_names = calendar.weekheader(2).split()

    cols = st.columns(7)
    for i, day_name in enumerate(day_names):
        cols[i].write(day_name)

    # Display the calendar
    for week in cal.monthdayscalendar(year, month):
        cols = st.columns(7)
        for i, day in enumerate(week):
            if day == 0:
                cols[i].write("")
            else:
                date_str = f"{year}-{month:02d}-{day:02d}"
                if check_availability(date_str):
                    if date(year, month, day) == date.today():
                        if cols[i].button(f"{day}", key=f"today_{day}"):
                            st.session_state.selected_date = date_str
                    else:
                        if cols[i].button(f"{day}", key=f"available_{day}"):
                            st.session_state.selected_date = date_str
                else:
                    cols[i].markdown(
                        f"<span style='display:inline-block; width:42px; height:42px; line-height:42px; text-align:center; color:white; background-color:red; border-radius:0;'>{day}</span>",
                        unsafe_allow_html=True
                    )

    
    if st.session_state.selected_date:
        st.write(f"### Selected Date: {st.session_state.selected_date}")
        selected_time = st.time_input("Pick a time:", key="time")
        st.write(f"You have selected {st.session_state.selected_date} at {selected_time}")

        # User details input
        name = st.text_input("Full Name")
        phone = st.text_input("Phone Number")
        email = st.text_input("Email Address")
        date = st.session_state.selected_date
        # Fee for booking
        fee = 100  # Set a fixed fee for the booking

        if st.button("Confirm Booking"):
            if name and phone and email:
                # Generate booking number randomly
                booking_num = random.randint(1000, 9999)
                status = 'open'
                pdf_file = generate_pdf(name, phone, email, date, selected_time, fee, booking_num, status)
                if pdf_file:
                    if add_booking(name, phone, email, date, selected_time, fee, booking_num, status):
                        with open(pdf_file, "rb") as f:
                            st.download_button(label="Download Invoice", data=f, file_name=pdf_file,
                                               mime="application/pdf")
                        st.success("Booking confirmed! Your invoice is ready for download.")
                        st.balloons()
                        time.sleep(5)
                    else:
                        st.error("Failed to add booking")
                else:
                    st.error("Failed to generate PDF")
            else:
                st.warning("Please fill out all the details.")
    else:
        st.session_state.selected_date = 0

elif choice == "Booking Details":
    st.header("Booking Details")

    booking_num = st.text_input("Enter Booking Number")
    phone_num = st.text_input("Enter Phone Number")

    if st.button("Check Booking"):
        if booking_num and phone_num:
            booking_details = check_booking_details(booking_num, phone_num)
            if booking_details:
                with st.expander(f"{booking_details['Name']}"):
                    st.write(f"Name: {booking_details['Name']}")
                    st.write(f"Phone Number: {booking_details['Phone number']}")
                    st.write(f"Email: {booking_details['Email']}")
                    st.write(f"Booking Date: {booking_details['Booking date']}")
                    st.write(f"Booking Time: {booking_details['Booking time']}")
                    st.write(f"Fee: ${booking_details['Fee']}")
                    st.write(f"Booking Number: {booking_details['Booking number']}")
                    st.write(f"Status: {booking_details['Status']}")
            else:
                st.error("Booking not found")
        else:
            st.warning("Please enter both Booking Number and Phone Number")

    if st.button("Close Booking"):
        if booking_num and phone_num:
            if update_status(booking_num, 'closed'):
                st.success("Booking closed successfully")
            else:
                st.error("Failed to close booking")
        else:
            st.warning("Please enter both Booking Number and Phone Number")
