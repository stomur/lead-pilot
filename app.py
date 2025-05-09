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
        res = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=60
        )
        score = res.choices[0].message.content
    except Exception as e:
        st.error(f"❌ OpenAI API error while scoring lead: {e}")
        st.stop()

    st.success("Thanks! A SoKat team-member will reach out shortly.")

    # Store in Google Sheet
    try:
        ws = get_ws()
        ws.append_row([
            datetime.datetime.utcnow().isoformat(),
            name, email, company, role, ", ".join(interest), pain_pt, score
        ])
    except Exception as e:
        st.error(f"❌ Google Sheet write error: {e}")

    # Store locally as Excel backup
    row = dict(timestamp=datetime.datetime.utcnow(), name=name, email=email,
               company=company, role=role, interest=interest, pain=pain_pt, score=score)
    path = "leads_backup.xlsx"
    if os.path.exists(path):
        df = pd.read_excel(path)
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    else:
        df = pd.DataFrame([row])
    df.to_excel(path, index=False)

    # Generate follow-up email
    with st.expander("Generate personalised follow-up"):
        reply_prompt = (f"Draft a concise, helpful first-touch email from SoKat to "
                        f"{name} based on their notes: {pain_pt}. Tone: expert yet friendly.")
        try:
            reply_txt = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": reply_prompt}],
                max_tokens=180
            ).choices[0].message.content
            st.code(reply_txt, language="markdown")
        except Exception as e:
            st.error(f"❌ OpenAI API error while generating email: {e}")



