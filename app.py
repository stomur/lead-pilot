
import streamlit as st
import gspread
import json

st.title("🔍 Google Sheets Access Debugger")

try:
    creds_dict = json.loads(st.secrets["GCP_SERVICE_ACCOUNT"])
    st.write("✅ Using service account:", creds_dict["client_email"])

    gc = gspread.service_account_from_dict(creds_dict)
    files = gc.list_spreadsheet_files()
    if not files:
        st.warning("⚠️ No spreadsheets found for this service account.")
    else:
        st.success(f"✅ Found {len(files)} spreadsheet(s).")
        for f in files:
            st.write(f"📄 `{f['name']}` (ID: `{f['id']}`)")
except Exception as e:
    st.error("❌ Failed to list accessible Google Sheets.")
    st.exception(e)
