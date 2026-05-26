import os
import re
import requests
import pdfplumber
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

SERPER_API_KEY = os.getenv("SERPER_API_KEY")

st.set_page_config(
    page_title="Fact-Check Agent",
    page_icon="🔎",
    layout="wide"
)

st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1180px;
}

.top-card {
    background: #111827;
    border: 1px solid #283142;
    border-radius: 16px;
    padding: 24px 28px;
    margin-bottom: 24px;
}

.app-title {
    font-size: 34px;
    font-weight: 700;
    margin: 0;
}

.app-subtitle {
    font-size: 16px;
    color: #a7b0c0;
    margin-top: 8px;
}

.info-card {
    background: #101820;
    border: 1px solid #2a3545;
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 16px;
}

.claim-card {
    background: #111111;
    border: 1px solid #303030;
    border-radius: 14px;
    padding: 18px 20px;
    margin-bottom: 16px;
}

.status-ok {
    color: #22c55e;
    font-weight: 700;
}

.status-warn {
    color: #facc15;
    font-weight: 700;
}

.status-bad {
    color: #ef4444;
    font-weight: 700;
}

.small-muted {
    color: #9ca3af;
    font-size: 14px;
}

a {
    color: #60a5fa !important;
}
</style>
""", unsafe_allow_html=True)


st.markdown("""
<div class="top-card">
    <div class="app-title">Fact-Check Agent</div>
    <div class="app-subtitle">
        Upload a PDF and check factual claims using live web search.
    </div>
</div>
""", unsafe_allow_html=True)


def read_pdf(file):
    text = ""

    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

    return text


def get_claims(text):
    lines = text.split("\n")
    claims = []

    for line in lines:
        line = line.strip()

        has_number = re.search(r"\d", line)
        enough_text = len(line) > 18

        if has_number and enough_text:
            claims.append(line)

    clean_claims = []

    for item in claims:
        if item not in clean_claims:
            clean_claims.append(item)

    return clean_claims[:12]


def check_on_web(claim):
    if not SERPER_API_KEY:
        return {
            "status": "No API Key",
            "source_title": "API key not added",
            "source_link": "",
            "note": "Add SERPER_API_KEY in .env file."
        }

    url = "https://google.serper.dev/search"

    headers = {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "q": claim,
        "num": 3
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=20)
        data = response.json()

        results = data.get("organic", [])

        if len(results) == 0:
            return {
                "status": "No Result",
                "source_title": "No strong web source found",
                "source_link": "",
                "note": "Could not find a reliable matching result."
            }

        first = results[0]

        return {
            "status": "Needs Review",
            "source_title": first.get("title", "Source"),
            "source_link": first.get("link", ""),
            "note": first.get("snippet", "Web result found. Please compare the claim with source.")
        }

    except Exception as e:
        return {
            "status": "Error",
            "source_title": "Search failed",
            "source_link": "",
            "note": str(e)
        }


left, right = st.columns([2, 1], gap="large")

with left:
    st.subheader("Upload PDF")

    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=["pdf"],
        label_visibility="collapsed"
    )

    if uploaded_file:
        with st.spinner("Reading PDF and checking claims..."):
            pdf_text = read_pdf(uploaded_file)
            claims = get_claims(pdf_text)

        if not claims:
            st.warning("No clear factual claims were detected in this PDF.")

        else:
            st.subheader("Detected Claims")

            for index, claim in enumerate(claims, start=1):
                result = check_on_web(claim)
                status = result["status"]

                if status == "Needs Review":
                    status_class = "status-warn"
                elif status == "No API Key":
                    status_class = "status-bad"
                elif status == "No Result":
                    status_class = "status-bad"
                else:
                    status_class = "status-ok"

                source_link = result["source_link"]

                if source_link:
                    source_html = f'<a href="{source_link}" target="_blank">{result["source_title"]}</a>'
                else:
                    source_html = result["source_title"]

                st.markdown(f"""
                <div class="claim-card">
                    <div class="small-muted">Claim {index}</div>
                    <div style="font-size:16px; margin-top:6px;"><b>{claim}</b></div>
                    <br>
                    <div class="{status_class}">Status: {status}</div>
                    <br>
                    <div><b>Source:</b> {source_html}</div>
                    <div class="small-muted" style="margin-top:8px;">{result["note"]}</div>
                </div>
                """, unsafe_allow_html=True)

    else:
        st.info("Upload a PDF to start checking claims.")


with right:
    st.markdown("""
    <div class="info-card">
        <h3 style="margin-top:0;">How it works</h3>
        <p>1. Upload a PDF file.</p>
        <p>2. The app finds lines containing numbers, dates or percentages.</p>
        <p>3. It searches the web for matching evidence.</p>
        <p>4. You can review the source and decide if the claim is correct.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="info-card">
        <h3 style="margin-top:0;">Best PDF type</h3>
        <p>Use reports or documents having statistics, dates, market size, company facts, or technical figures.</p>
    </div>
    """, unsafe_allow_html=True)

    if not SERPER_API_KEY:
        st.warning("SERPER_API_KEY missing. Add it in .env file for web verification.")
