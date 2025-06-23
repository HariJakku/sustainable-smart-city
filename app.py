import streamlit as st
from ibm_watsonx_ai.foundation_models import Model
import fitz  # PyMuPDF for PDF reading
import pandas as pd
import json
from streamlit_option_menu import option_menu
import time

# --- IBM Watsonx Credentials ---
api_key = "YOUR_IBM_WATSONX_API_KEY"
project_id = "YOUR_PROJECT_ID"
base_url = "https://YOUR_REGION.ml.cloud.ibm.com"

model_id = "ibm/granite-3-3-8b-instruct"

# --- Streamlit App Config ---
st.set_page_config(page_title="Smart City AI Assistant", layout="wide", page_icon="🏙️")
st.title("🏙️ Sustainable Smart City Assistant Using IBM Granite LLM")

# --- Chat history (for chatbot only) ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Watsonx Query Function ---
def ask_watsonx(prompt):
    try:
        model = Model(
            model_id=model_id,
            credentials={"apikey": api_key, "url": base_url},
            project_id=project_id
        )

        result = model.generate_text(
            prompt=prompt,
            params={
                "max_new_tokens": 500,
                "temperature": 0.7,
                "top_p": 1.0,
                "decoding_method": "sample"
            }
        )

        if isinstance(result, dict):
            return result.get("generated_text", "⚠️ No 'generated_text' in response.")
        elif isinstance(result, str):
            try:
                parsed = json.loads(result)
                return parsed.get("generated_text", result)
            except json.JSONDecodeError:
                return result
        else:
            return "⚠️ Unexpected response type."
    except Exception as e:
        return f"❌ Watsonx Error: {str(e)}"

# --- User Dashboard Function ---
def user_dashboard():
    st.subheader("📊 User Dashboard")
    st.markdown("""
    Welcome to your Smart City Assistant dashboard! Here’s a quick overview of the modules available:
    """)

    modules = [
        ("📜", "Policy Search & Summarization", "Upload or paste city policy documents and get clear, citizen-friendly summaries."),
        ("🗣️", "Citizen Feedback Reporting", "Report issues around the city easily and help local authorities respond faster."),
        ("📈", "KPI Forecasting", "Upload KPI data and get AI-driven forecasts to help plan city resources effectively."),
        ("🌿", "Eco Tips Generator", "Get simple eco-friendly tips to promote sustainable living in your community."),
        ("🚨", "Anomaly Detection", "Detect unusual patterns in city data to catch issues early and improve city management."),
        ("💬", "Chat Assistant", "Ask questions and get instant answers about your city's sustainability and governance."),
    ]

    for icon, title, desc in modules:
        st.markdown(f"**{icon} {title}**  \n{desc}\n")

# --- Sidebar Styled Menu ---
with st.sidebar:
    selected = option_menu(
        "📚 Smart City Modules",
        ["User Dashboard", "Policy Search & Summarization", "Citizen Feedback Reporting", "KPI Forecasting", "Eco Tips Generator", "Anomaly Detection", "Chat Assistant"],
        icons=["speedometer2", "file-earmark-text", "chat-left-text", "graph-up", "tree", "exclamation-triangle", "robot"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "5px", "background-color": "#fafafa"},
            "icon": {"color": "green", "font-size": "18px"},
            "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
            "nav-link-selected": {"background-color": "#02ab21", "color": "white"},
        }
    )

# --- Module Logic ---
if selected == "User Dashboard":
    user_dashboard()

elif selected == "Policy Search & Summarization":
    st.subheader("📜 Upload City Policy PDF or Paste Text")
    policy_file = st.file_uploader("Upload a policy document (PDF)", type="pdf")
    user_text = st.text_area("Or paste policy text here")
    extract_text = ""

    if policy_file:
        doc = fitz.open(stream=policy_file.read(), filetype="pdf")
        for page in doc:
            extract_text += page.get_text()

    if user_text:
        extract_text += "\n" + user_text

    summarize_button = st.button("🔍 Summarize")
    if extract_text and summarize_button:
        with st.spinner("⏳ Please wait, summarizing policy content..."):
            time.sleep(1)
            prompt = f"Summarize this city policy document in a citizen-friendly manner:\n{extract_text}"
            result = ask_watsonx(prompt)
        st.success("✅ Summary generated!")
        st.text_area("📝 Citizen-Friendly Summary", result, height=300)

elif selected == "Citizen Feedback Reporting":
    st.subheader("📣 Report a City Issue")
    category = st.selectbox("Select Issue Category", ["Water", "Electricity", "Sanitation", "Roads", "Others"])
    description = st.text_area("Describe the issue you noticed")
    if st.button("Submit Feedback"):
        st.success(f"🗂️ Feedback logged under '{category}' category.")
        st.write(f"**Description:** {description}")

elif selected == "KPI Forecasting":
    st.subheader("📈 Upload Last Year’s KPI (CSV)")
    kpi_file = st.file_uploader("Upload a CSV file (e.g., water usage)", type="csv")
    if kpi_file:
        df = pd.read_csv(kpi_file)
        st.dataframe(df)
        with st.spinner("⏳ Please wait, generating forecast insights..."):
            time.sleep(1)
            prompt = f"Given the following KPI data, forecast next year's trend:\n{df.to_string(index=False)}"
            forecast = ask_watsonx(prompt)
        st.success("✅ Forecast generated!")
        st.text_area("🔮 Forecasted Insights", forecast, height=300)

elif selected == "Eco Tips Generator":
    st.subheader("🌿 Generate Eco-Friendly Living Tips")
    keyword = st.text_input("Enter an environmental keyword (e.g., 'plastic', 'solar')")
    if st.button("Generate Tips") and keyword:
        with st.spinner("⏳ Please wait, generating tips..."):
            time.sleep(1)
            prompt = f"Generate 5 eco-friendly tips related to {keyword} that students can follow."
            tips = ask_watsonx(prompt)
        st.success("✅ Eco tips generated!")
        st.markdown("### 🌱 Eco Tips")
        st.markdown(tips)

elif selected == "Anomaly Detection":
    st.subheader("⚠️ Detect Anomalies in KPI Data")
    anomaly_file = st.file_uploader("Upload KPI CSV (e.g., energy consumption by zone)", type="csv")
    if anomaly_file:
        df = pd.read_csv(anomaly_file)
        st.dataframe(df)
        with st.spinner("⏳ Please wait, analyzing for anomalies..."):
            time.sleep(1)
            prompt = f"Analyze the following KPI data and detect any unusual patterns or anomalies:\n{df.to_string(index=False)}"
            anomalies = ask_watsonx(prompt)
        st.success("✅ Anomalies detected!")
        st.text_area("🚨 Detected Anomalies", anomalies, height=300)

elif selected == "Chat Assistant":
    st.subheader("💬 Ask Anything About Your City")
    user_query = st.chat_input("Ask how your city can improve sustainability, reduce emissions, etc.")
    if user_query:
        st.session_state.chat_history.append(("user", user_query))
        with st.spinner("⏳ Thinking..."):
            response = ask_watsonx(f"User: {user_query}\nAssistant:")
        st.session_state.chat_history.append(("assistant", response))

    for role, msg in st.session_state.chat_history:
        with st.chat_message(role):
            st.markdown(msg)
