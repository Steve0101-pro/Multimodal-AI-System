import os
import base64
from typing import Any

import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8000").rstrip("/")
REQUEST_TIMEOUT = int(os.getenv("API_TIMEOUT_SECONDS", "180"))

st.set_page_config(page_title="Document Intelligence", page_icon="DI", layout="wide", initial_sidebar_state="expanded")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=Space+Grotesk:wght@500;700&display=swap');
    :root { color-scheme: light; --ink: #172321; --muted: #65736f; --line: #d9e2de; --paper: #f4f6f2; --surface: rgba(255,255,255,.78); --teal: #087f73; --coral: #d66a4a; }
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; color: var(--ink); }
    h1, h2, h3, h4 { font-family: 'Space Grotesk', sans-serif; letter-spacing: 0; }
    .stApp { background: radial-gradient(circle at 90% 0%, #e3eee8 0, var(--paper) 32rem); }
    .block-container { max-width: 1320px; padding-top: 2.5rem; }
    .hero { padding: 1.4rem 0 1.7rem; border-bottom: 1px solid var(--line); margin-bottom: 1.8rem; }
    .eyebrow, .section-kicker { color: var(--teal); font-weight: 700; font-size: .72rem; text-transform: uppercase; letter-spacing: .11em; }
    .hero h1 { max-width: 820px; color: var(--ink) !important; font-size: 3.25rem; line-height: 1.02; margin: .55rem 0 .75rem; }
    .hero p { max-width: 650px; color: var(--muted); font-size: 1.05rem; line-height: 1.55; }
    .section-kicker { margin-bottom: .4rem; }
    .result { background: #e4f0eb; border-left: 5px solid var(--teal); padding: 1rem 1.2rem; border-radius: 4px; color: var(--ink); }
    [data-testid="stSidebar"] { background: #172e2b; }
    [data-testid="stSidebar"] * { color: #edf5f1; }
    [data-testid="stSidebar"] hr { border-color: #3b5853; }
    [data-testid="stMetric"] { background: rgba(255,255,255,.7); border: 1px solid var(--line); padding: .8rem 1rem; border-radius: 4px; }
    div.stButton > button[kind="primary"] { background: var(--teal); border-color: var(--teal); }
    div[data-testid="stFileUploader"] { border: 1px dashed #9fbab1; border-radius: 5px; padding: .35rem; background: rgba(255,255,255,.42); }
    @media (max-width: 760px) { .hero h1 { font-size: 2.35rem; } .block-container { padding-top: 1rem; } }
    .auth-shell { max-width: 520px; margin: 4rem auto 0; padding: 2.2rem; background: var(--surface); border: 1px solid var(--line); border-radius: 6px; box-shadow: 0 18px 50px rgba(23,46,43,.08); }
    .auth-shell h1 { color: var(--ink); font-family: 'Space Grotesk', sans-serif; font-size: 2.2rem; margin: 0 0 .5rem; }
    .auth-shell p { color: var(--muted); line-height: 1.5; }
    .auth-mark { color: var(--coral); font-size: .75rem; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; }
        [data-testid="stForm"] { border: 0; padding: 0; }
        [data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea { background: var(--surface); color: var(--ink); border-color: var(--line); }
        [data-baseweb="select"] > div, [data-baseweb="input"] > div { background: var(--surface); border-color: var(--line); }
        @media (prefers-color-scheme: dark) {
            :root { color-scheme: dark; --ink: #edf4f0; --muted: #a6b7b1; --line: #3a504b; --paper: #101918; --surface: #1a2927; --teal: #5ac8b5; --coral: #f08a68; }
            .stApp { background: radial-gradient(circle at 90% 0%, #203b36 0, var(--paper) 34rem); }
            .hero h1, .auth-shell h1, html, body, [class*="css"] { color: var(--ink) !important; }
            .hero p, .auth-shell p { color: var(--muted) !important; }
            [data-testid="stMetric"], div[data-testid="stFileUploader"] { background: var(--surface); border-color: var(--line); }
            [data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea, [data-baseweb="select"] > div, [data-baseweb="input"] > div { background: var(--surface); color: var(--ink); border-color: var(--line); }
            div[data-testid="stFileUploader"] section, div[data-testid="stFileUploader"] small { color: var(--muted); }
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def api_request(method: str, path: str, **kwargs: Any) -> requests.Response:
    headers = kwargs.pop("headers", {})
    token = st.session_state.get("token")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return requests.request(method, f"{API_URL}{path}", headers=headers, timeout=REQUEST_TIMEOUT, **kwargs)


def error_message(response: requests.Response) -> str:
    try:
        detail = response.json().get("detail", response.text)
    except ValueError:
        detail = response.text
    return str(detail) or f"Request failed with status {response.status_code}"


def authenticate(endpoint: str, email: str, password: str) -> bool:
    response = requests.post(
        f"{API_URL}/auth/{endpoint}",
        json={"email": email, "password": password},
        timeout=30,
    )
    if response.ok:
        st.session_state.token = response.json()["access_token"]
        return True
    st.error(error_message(response))
    return False


def request_password_reset(email: str) -> bool:
    response = requests.post(
        f"{API_URL}/auth/forgot-password",
        json={"email": email},
        timeout=30,
    )
    if response.status_code == 202:
        st.success("If that email is registered, recovery instructions have been sent.")
        return True
    st.error(error_message(response))
    return False


def reset_password(token: str, password: str) -> bool:
    response = requests.post(
        f"{API_URL}/auth/reset-password",
        json={"token": token, "password": password},
        timeout=30,
    )
    if response.status_code == 204:
        st.success("Password updated. You can now sign in.")
        return True
    st.error(error_message(response))
    return False


if "token" not in st.session_state:
    with st.sidebar:
        st.markdown("## Document Intelligence")
        st.caption("A private workspace for turning documents and voice into useful answers.")
        st.divider()
        st.caption("API service")
        st.code(API_URL, language=None)
    _, auth_column, _ = st.columns([1, 1.25, 1])
    with auth_column:
        st.markdown('<div class="auth-shell"><div class="auth-mark">Private workspace</div><h1>Welcome back.</h1><p>Sign in to extract documents, ask visual questions, and review generated answers.</p></div>', unsafe_allow_html=True)
        auth_mode = st.radio("Account action", ["Sign in", "Create account", "Recover password"], horizontal=True, label_visibility="collapsed")
        if auth_mode == "Recover password":
            with st.form("forgot_password"):
                recovery_email = st.text_input("Account email")
                recovery_submitted = st.form_submit_button("Send recovery instructions", type="primary", use_container_width=True)
            if recovery_submitted and recovery_email:
                request_password_reset(recovery_email)

            with st.form("reset_password"):
                reset_token = st.text_input("Recovery token", type="password")
                new_password = st.text_input("New password", type="password")
                reset_submitted = st.form_submit_button("Set new password", use_container_width=True)
            if reset_submitted:
                if not reset_token or not new_password:
                    st.warning("Enter the recovery token and a new password.")
                else:
                    reset_password(reset_token, new_password)
            st.stop()

        with st.form("authentication"):
            email = st.text_input("Email", placeholder="you@example.com")
            password = st.text_input("Password", type="password", help="Use at least 8 characters with uppercase, lowercase, and a number.")
            submitted = st.form_submit_button(auth_mode, type="primary", use_container_width=True)
        if submitted:
            if not email or not password:
                st.warning("Enter both email and password.")
            else:
                endpoint = "login" if auth_mode == "Sign in" else "register"
                if authenticate(endpoint, email, password):
                    st.rerun()
    st.stop()

with st.sidebar:
    st.markdown("## Workspace")
    st.caption(f"API: `{API_URL}`")
    if st.button("Sign out", use_container_width=True):
        st.session_state.clear()
        st.rerun()
    st.divider()
    st.caption("Your files are processed by the FastAPI service and stored using the configured storage provider.")

st.markdown(
    '<div class="hero"><div class="eyebrow">Document intelligence workspace</div><h1>Make every document easier to understand.</h1><p>Extract invoice fields, ask questions with your voice, and listen to grounded answers from one focused workspace.</p></div>',
    unsafe_allow_html=True,
)

extract_tab, multimodal_tab, health_tab = st.tabs(["Extract a document", "Ask with voice + image", "Service health"])

with extract_tab:
    st.markdown('<div class="section-kicker">Workflow 01</div>', unsafe_allow_html=True)
    st.subheader("Invoice extraction")
    st.caption("Turn an invoice image into searchable text and structured fields.")
    extraction_mode = st.radio("Processing mode", ["OCR + structured data", "Vision language model"], horizontal=True)
    document = st.file_uploader("Choose a PNG or JPEG", type=["png", "jpg", "jpeg"], key="document")
    if document and st.button("Process document", type="primary"):
        endpoint = "/documents/vlm" if extraction_mode.startswith("Vision") else "/documents/"
        with st.spinner("Reading document..."):
            response = api_request("POST", endpoint, files={"file": (document.name, document.getvalue(), document.type)})
        if response.ok:
            payload = response.json()
            st.success(f"Processed {payload['filename']}")
            st.metric("Processing mode", extraction_mode)
            left, right = st.columns(2)
            with left:
                st.markdown("#### Extracted text")
                st.text_area("Text", payload.get("extracted_text") or "No text returned.", height=280, label_visibility="collapsed")
            with right:
                st.markdown("#### Structured fields")
                invoice = (payload.get("layout_data") or {}).get("invoice_data")
                st.json(invoice or {"status": "No structured invoice fields returned"})
            st.caption(f"Document ID: {payload['id']} | Stored at: {payload['storage_path']}")
        else:
            st.error(error_message(response))

with multimodal_tab:
    st.markdown('<div class="section-kicker">Workflow 02</div>', unsafe_allow_html=True)
    st.subheader("Voice + image question")
    st.caption("Pair a spoken question with an image when visual context matters.")
    audio = st.file_uploader("Audio input", type=["mp3", "wav", "m4a", "mp4", "ogg", "webm"], key="audio")
    image = st.file_uploader("Optional image", type=["jpg", "jpeg", "png", "webp"], key="image")
    prompt = st.text_input("Additional prompt", placeholder="Read the total and explain any due date.")
    if audio and st.button("Run multimodal pipeline", type="primary"):
        files = {"audio": (audio.name, audio.getvalue(), audio.type)}
        if image:
            files["image"] = (image.name, image.getvalue(), image.type)
        data = {"user_prompt": prompt} if prompt else {}
        with st.spinner("Transcribing, reasoning, and generating a response..."):
            response = api_request("POST", "/multimodal/voice-image", files=files, data=data)
        if response.ok:
            payload = response.json()
            st.success("Response ready")
            st.markdown("**Transcript**")
            st.write(payload["transcript"])
            st.markdown("**Answer**")
            st.write(payload["response_text"])
            st.audio(base64.b64decode(payload["audio_base64"]), format=payload.get("audio_content_type", "audio/wav"))
            st.divider()
            st.markdown("**Was this answer useful?**")
            feedback_left, feedback_right = st.columns([1, 2])
            with feedback_left:
                rating = st.select_slider("Rating", options=[1, 2, 3, 4, 5], value=5, key="feedback_rating")
            with feedback_right:
                feedback_comment = st.text_input("Optional note", placeholder="What should improve?", key="feedback_comment")
            if st.button("Send feedback", key="send_feedback"):
                feedback_response = api_request(
                    "POST",
                    "/feedback",
                    json={
                        "conversation_id": payload["conversation_id"],
                        "rating": rating,
                        "comment": feedback_comment or None,
                        "model_version": "configured",
                        "prompt_version": "v1",
                    },
                )
                if feedback_response.ok:
                    st.success("Feedback recorded for review.")
                else:
                    st.error(error_message(feedback_response))
            st.caption(f"Conversation: {payload['conversation_id']} | Generated audio: {payload['audio_storage_path']}")
        else:
            st.error(error_message(response))

with health_tab:
    st.markdown('<div class="section-kicker">System observability</div>', unsafe_allow_html=True)
    st.subheader("Runtime status")
    if st.button("Refresh health"):
        for label, endpoint in [("API", "/"), ("Redis", "/health/redis"), ("Full", "/health/full")]:
            response = api_request("GET", endpoint)
            if response.ok:
                st.metric(label, "Healthy")
                st.json(response.json())
            else:
                st.metric(label, f"HTTP {response.status_code}")
