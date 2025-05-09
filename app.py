import os, datetime, json, streamlit as st, openai, gspread, pandas as pd

# Set OpenAI key from secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Set up Google Sheets service account
creds_dict = json.loads(st.secrets["GCP_SERVICE_ACCOUNT"])
gc = gspread.service_account_from_dict(creds_dict)

# Sheet settings
SHEET = "SoKat Leads"
WORKSHEET = "Sheet1"

@st.cache_resource(show_spinner=False)
def get_ws():
    sh = gc.open(SHEET)
    return sh.worksheet(WORKSHEET)

# UI
st.title("🚀 Connect with SoKat AI")

with st.form(key="lead_form"):
    name = st.text_input("Full name")
    email = st.text_input("Work email")
    company = st.text_input("Company / agency")
    role = st.text_input("Your role")
    interest = st.multiselect(
        "What can we help you with?",
        ["AI Training", "NLP & Chatbots", "Predictive Analytics", "Risk / Fraud Detection", "Other"]
    )
    pain_pt = st.text_area("Briefly describe your challenge")
    submitted = st.form_submit_button("Submit")

if submitted:
    prompt = (f"You are SoKat's BD assistant. Rate 0–10 how well this prospect "
              f"matches the services SoKat offers, and summarise in 1 sentence.\n\n"
              f"Prospect: {company}, role {role}\nInterest: {interest}\nPain: {pain_pt}")
    
    # Call GPT to score
    try:
        res = openai.chat


