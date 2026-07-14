import streamlit as st
import json
import os
import google.generativeai as genai

# MUST BE THE FIRST COMMAND
st.set_page_config(page_title="Customer Context 360", layout="wide")

# Safely get the API Key from Streamlit Secrets
api_key = None
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except:
    api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.warning("⚠️ GEMINI_API_KEY not found! Please add it to your Streamlit Advanced Settings > Secrets.")
else:
    genai.configure(api_key=api_key)

# We use gemini-1.5-flash as it is lightning fast
model = genai.GenerativeModel('gemini-pro')

# --- DUMMY DATA ---
mock_db = {
    "Acme Corp": {
        "zoho_crm": {"arr": "\$120,000", "renewal_date": "2024-11-15", "health_score": "Yellow", "plan": "Enterprise"},
        "zendesk": [
            {"id": "T-101", "issue": "API Rate limit exceeded", "priority": "High", "status": "Open"},
            {"id": "T-102", "issue": "How to add new users?", "priority": "Low", "status": "Closed"}
        ],
        "slack": [
            {"user": "CSM_Sarah", "message": "Heads up, Acme's VP of Ops (our main champion) is leaving next month."},
            {"user": "AE_John", "message": "If they fix the API issue, they mentioned wanting to add 50 more seats."}
        ]
    },
    "Globex Inc": {
        "zoho_crm": {"arr": "\$45,000", "renewal_date": "2025-03-01", "health_score": "Green", "plan": "Pro"},
        "zendesk": [
            {"id": "T-204", "issue": "Best practices for reporting?", "priority": "Low", "status": "Closed"}
        ],
        "slack": [
            {"user": "CSM_Sarah", "message": "Globex is loving the new dashboard feature. Engagement is up 40%."},
            {"user": "AE_John", "message": "They just acquired a smaller startup, might need to consolidate their instances."}
        ]
    }
}

# --- AI PROCESSING FUNCTION ---
def analyze_customer(company_name, data):
    prompt = f"""
    You are an expert Customer Success and RevOps AI. 
    Analyze the following customer data from 3 sources (CRM, Support, Internal Chat) for {company_name}.
    
    Raw Data: {json.dumps(data, indent=2)}
    
    Provide a formatted Markdown report with exactly these sections:
    1. 📝 **Account Summary:** (2-3 sentences max)
    2. ⚠️ **Key Risks:** (Bullet points)
    3. 🚀 **Key Opportunities:** (Bullet points)
    4. 🎯 **Next Best Action:** (One highly specific, actionable directive for the account owner)
    """
    
    response = model.generate_content(prompt)
    return response.text

# --- STREAMLIT UI ---
st.title("🔄 Customer Context 360 AI")
st.markdown("Aggregating CRM, Support, and Slack data into one actionable view.")

st.sidebar.header("Select Account")
selected_company = st.sidebar.selectbox("Choose a customer:", list(mock_db.keys()))

st.write(f"### Raw Data Sources for {selected_company}")
col1, col2, col3 = st.columns(3)

data = mock_db[selected_company]
with col1:
    st.subheader("🔵 Zoho CRM")
    st.json(data["zoho_crm"])
with col2:
    st.subheader("🟢 Zendesk Support")
    st.json(data["zendesk"])
with col3:
    st.subheader("🟣 Slack (Internal)")
    for msg in data["slack"]:
        st.info(f"**{msg['user']}**: {msg['message']}")

st.divider()

if st.button("🧠 Generate AI Insights & Next Best Action", type="primary"):
    if not api_key:
        st.error("Cannot generate insights because the API key is missing.")
    else:
        with st.spinner('Consolidating data and analyzing via Gemini AI...'):
            try:
                ai_report = analyze_customer(selected_company, data)
                st.success("Analysis Complete!")
                with st.container():
                    st.markdown(ai_report)
            except Exception as e:
                st.error(f"Error connecting to AI: {e}")
