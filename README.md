## Quick start
1.  `git clone https://github.com/<you>/lead-pilot && cd lead-pilot`
2.  `pip install -r requirements.txt`
3.  Add `.streamlit/secrets.toml` with your keys.
4.  `streamlit run app.py`
   *Local file `leads_backup.xlsx` is auto‑created.*
5.  Push to GitHub → connect repo on **streamlit.io** for free hosting.

## Customising
* Edit the GPT prompt in `app.py` to change scoring rubric or e‑mail style.
* To store only in Google Sheets (no Excel), delete the “backup” block.
* To send real e‑mails automatically, create a SendGrid key and un‑comment
  sendgrid integration (sample code included at bottom of `app.py`).
