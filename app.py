import os, datetime, json, streamlit as st, openai, gspread, pandas as pd
from google.oauth2.service_account import Credentials

# --- CONFIG ---
openai.api_key = st.secrets["OPENAI_API_KEY"]
creds = Credentials.from_service_account_info(
    json.loads(st.secrets["GCP_SERVICE_ACCOUNT"])
)
SHEET       = "SoKat Leads"
WORKSHEET   = "Sheet1"

def get_ws():
    gc = gspread.authorize(creds)
    sh = gc.open(SHEET)
    return sh.worksheet(WORKSHEET)

# --- UI ---
st.title("🚀  Connect with SoKat AI")
with st.form(key="lead_form"):
    name      = st.text_input("Full name")
    email     = st.text_input("Work e‑mail")
    company   = st.text_input("Company / agency")
    role      = st.text_input("Your role")
    interest  = st.multiselect(
        "What can we help you with?",
        ["AI Training", "NLP & Chatbots", "Predictive Analytics",
         "Risk / Fraud Detection", "Other"]
    )
    pain_pt   = st.text_area("Briefly describe your challenge")
    submitted = st.form_submit_button("Submit")

if submitted:
    # 1) call GPT‑4o to score fit
    prompt = (f"You are SoKat's BD assistant. Rate 0‑10 how well this prospect "
              f"matches the services SoKat offers, and summarise in 1 sentence.\n\n"
              f"Prospect: {company}, role {role}\nInterest: {interest}\nPain: {pain_pt}")
    res = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=60
    )
    score  = res.choices[0].message.content
    st.success("Thanks! A SoKat team‑member will reach out shortly.")
    
    # 2) write to Google Sheet
    ws = get_ws()
    ws.append_row([
        datetime.datetime.utcnow().isoformat(),
        name, email, company, role, ", ".join(interest), pain_pt, score
    ])
    
    # 3) also keep local Excel backup
    row = dict(timestamp=datetime.datetime.utcnow(), name=name, email=email,
               company=company, role=role, interest=interest, pain=pain_pt, score=score)
    path = "leads_backup.xlsx"
    if os.path.exists(path):
        df = pd.read_excel(path)
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    else:
        df = pd.DataFrame([row])
    df.to_excel(path, index=False)
    
    # 4) (optional) generate reply e‑mail
    with st.expander("Generate personalised follow‑up"):
        reply_prompt = (f"Draft a concise, helpful first‑touch e‑mail from SoKat to "
                        f"{name} based on their notes: {pain_pt}. Tone: expert yet friendly.")
        reply_txt = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": reply_prompt}],
            max_tokens=180
        ).choices[0].message.content
        st.code(reply_txt, language="markdown")
