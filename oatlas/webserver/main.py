# app.py
import base64
import random
import string
from datetime import datetime

import streamlit as st

from oatlas.config import Config
from oatlas.logger import get_logger
from oatlas.webserver.static.custom_css import main_css

log = get_logger()

APP_NAME = Config.web.app_name
LOGO_PATH = Config.web.logo_path

st.set_page_config(page_title=APP_NAME, page_icon=LOGO_PATH, layout="wide")


def load_css():
    st.markdown(
        main_css,
        unsafe_allow_html=True,
    )


# ------------------ Utility ------------------ #
def get_base64_image(image_path):
    with open(image_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()


# ------------------ Auth ------------------ #
if "session_api_key" not in st.session_state:
    st.session_state.session_api_key = "".join(
        random.choices(string.ascii_uppercase + string.digits, k=8)
    )
    log.info(f"API Key for this session: {st.session_state.session_api_key}")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "current_page" not in st.session_state:
    st.session_state.current_page = "Dashboard"


def authentication_screen():
    st.markdown(f"<h2 class='center-header'>Welcome to {APP_NAME}</h2>", unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align:center;'>Please enter your API key to continue.</p>",
        unsafe_allow_html=True,
    )
    st.caption("Check your terminal/console for the API key.")

    api_key = st.text_input("API Key", type="password")
    if st.button("Enter"):
        if api_key == st.session_state.session_api_key:
            st.session_state.authenticated = True
            st.success("Correct key! Entering dashboard...")
            st.rerun()
        else:
            st.error("NAHH, we need the right API key")


def dashboard():
    st.markdown(
        f"<h1 class='center-header'>"
        f"<img src='data:image/png;base64,{get_base64_image(LOGO_PATH)}' width='50'> "
        f"{APP_NAME} Dashboard</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='text-align:center;'>Welcome to the main control panel.</p>",
        unsafe_allow_html=True,
    )

    st.subheader("Currently Running Scans")

    # Just pushing random values here to ensure the dashboard looks nice
    scan_data = [
        {
            "id": f"scan-{i+1}",
            "target": f"192.168.0.{i+2}",
            "status": random.choice(["Running", "Queued", "Completed"]),
            "start_time": datetime.now().strftime("%H:%M:%S"),
        }
        for i in range(5)
    ]
    for scan in scan_data:
        status_color = (
            "green"
            if scan["status"] == "Completed"
            else ("orange" if scan["status"] == "Running" else "grey")
        )
        st.markdown(
            f"<span style='color:cyan; font-weight:bold;'>{scan['id']}</span> | "
            f"Target: <span style='color:lightgreen;'>{scan['target']}</span> | "
            f"Status: <span style='color:{status_color}; font-weight:bold;'>{scan['status']}</span> | "
            f"Started: {scan['start_time']}",
            unsafe_allow_html=True,
        )


def results():
    st.title("📂 Scan Results")
    st.info("This page will show completed scan results once implemented.")
    st.dataframe(
        {
            "Scan ID": ["scan-1", "scan-2"],
            "Target": ["192.168.0.10", "example.com"],
            "Status": ["Completed", "Completed"],
            "Findings": ["3 vulnerabilities", "No issues found"],
        }
    )


def crawler():
    st.title("🕷️ Crawler")
    st.info("This page will allow running and viewing crawler outputs in the future.")
    target = st.text_input("Enter a URL to crawl")
    if st.button("Start Crawl"):
        st.success(f"Crawling started for: {target}")


def new_scan():
    st.title("👀 new-scan")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_input = st.chat_input("Type your instructions or drop files...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # This is just a placeholder for now, we'll need to start working here.
        response = f"✅ Instruction received: **{user_input}**\n\nStarting scan..."
        st.session_state.messages.append({"role": "assistant", "content": response})

        with st.chat_message("assistant"):
            st.markdown(response)

    uploaded_images = st.file_uploader(
        "Upload Images", type=["png", "jpg", "jpeg"], accept_multiple_files=True
    )
    if uploaded_images:
        st.info(f"📷 {len(uploaded_images)} image(s) uploaded.")

    uploaded_files = st.file_uploader(
        "Upload Text Files", type=["txt"], accept_multiple_files=True
    )
    if uploaded_files:
        st.info(f"📄 {len(uploaded_files)} text file(s) uploaded.")


def navigation():
    st.sidebar.markdown("## 🔍 Navigation")
    for page in ["Dashboard", "Results", "Crawler", "new-scan"]:
        if st.sidebar.button(
            page,
            key=page,
            help=f"Go to {page}",
            on_click=lambda p=page: st.session_state.update(current_page=p),
            args=(),
        ):
            st.session_state.current_page = page
            st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.caption(f"Session Key: `{st.session_state.session_api_key}`")
    st.sidebar.caption(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


load_css()

if not st.session_state.authenticated:
    authentication_screen()
else:
    navigation()
    if st.session_state.current_page == "Dashboard":
        dashboard()
    elif st.session_state.current_page == "Results":
        results()
    elif st.session_state.current_page == "Crawler":
        crawler()
    elif st.session_state.current_page == "new-scan":
        new_scan()
