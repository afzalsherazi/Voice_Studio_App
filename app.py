import os
import io
import wave
import textwrap
from datetime import datetime

import streamlit as st
from google import genai
from google.genai import types


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Voice Studio",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CSS
# ============================================================

st.markdown(
    textwrap.dedent(
        """
        <style>

        /* =========================
           GLOBAL
        ========================= */

        .stApp {
            background: #f5f7fb;
            color: #111827;
        }

        .main .block-container {
            max-width: 1450px;
            padding-top: 2.5rem;
            padding-bottom: 3rem;
        }

        header[data-testid="stHeader"] {
            background: transparent;
        }

        /* =========================
           SIDEBAR
        ========================= */

        section[data-testid="stSidebar"] {
            background: #ffffff;
            border-right: 1px solid #e5e7eb;
        }

        section[data-testid="stSidebar"] > div {
            background: #ffffff;
        }

        .sidebar-brand {
            text-align: center;
            padding: 0.5rem 0 1.5rem 0;
        }

        .sidebar-icon {
            font-size: 2.5rem;
            margin-bottom: 0.3rem;
        }

        .sidebar-title {
            color: #111827;
            font-size: 1.25rem;
            font-weight: 800;
        }

        .sidebar-subtitle {
            color: #6b7280;
            font-size: 0.75rem;
            margin-top: 0.25rem;
        }

        .sidebar-heading {
            color: #9ca3af;
            font-size: 0.7rem;
            font-weight: 800;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin: 1rem 0 0.5rem 0;
        }

        .sidebar-divider {
            height: 1px;
            background: #e5e7eb;
            margin: 1rem 0;
        }

        section[data-testid="stSidebar"] .stButton > button {
            width: 100%;
            border: none;
            background: transparent;
            color: #374151;
            text-align: left;
            justify-content: flex-start;
            border-radius: 10px;
            min-height: 2.7rem;
            font-size: 0.9rem;
            font-weight: 600;
        }

        section[data-testid="stSidebar"] .stButton > button:hover {
            background: #eff6ff;
            color: #2563eb;
            border: none;
        }

        .sidebar-card {
            background: #f8fafc;
            border: 1px solid #e5e7eb;
            border-radius: 14px;
            padding: 1rem;
            margin-top: 1rem;
        }

        .sidebar-card-title {
            color: #111827;
            font-size: 0.82rem;
            font-weight: 750;
            margin-bottom: 0.4rem;
        }

        .sidebar-card-text {
            color: #64748b;
            font-size: 0.72rem;
            line-height: 1.55;
        }

        /* =========================
           HEADER
        ========================= */

        .page-title {
            color: #111827;
            font-size: 2.35rem;
            font-weight: 850;
            letter-spacing: -0.045em;
            margin-bottom: 0.4rem;
        }

        .page-subtitle {
            color: #64748b;
            font-size: 1rem;
            margin-bottom: 1.8rem;
        }

        /* =========================
           CARDS
        ========================= */

        .card {
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 16px;
            padding: 1.35rem;
            box-shadow: 0 4px 20px rgba(15, 23, 42, 0.04);
            margin-bottom: 1rem;
        }

        .card-title {
            color: #111827;
            font-size: 1.05rem;
            font-weight: 750;
            margin-bottom: 0.25rem;
        }

        .card-description {
            color: #64748b;
            font-size: 0.78rem;
            margin-bottom: 1rem;
        }

        /* =========================
           SCRIPT AREA
        ========================= */

        .script-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.7rem;
        }

        .script-title {
            color: #111827;
            font-size: 1rem;
            font-weight: 750;
        }

        .script-hint {
            color: #94a3b8;
            font-size: 0.72rem;
        }

        textarea {
            background: #ffffff !important;
            color: #111827 !important;
            border: 1px solid #cbd5e1 !important;
            border-radius: 12px !important;
            font-size: 0.95rem !important;
            line-height: 1.65 !important;
            padding: 1rem !important;
            box-shadow: none !important;
        }

        textarea::placeholder {
            color: #94a3b8 !important;
            opacity: 1 !important;
        }

        textarea:focus {
            border-color: #2563eb !important;
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1) !important;
        }

        /* =========================
           COUNTERS
        ========================= */

        .counter-row {
            display: flex;
            gap: 0.6rem;
            margin-top: 0.7rem;
        }

        .counter {
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 0.4rem 0.7rem;
            color: #64748b;
            font-size: 0.72rem;
        }

        .counter strong {
            color: #334155;
        }

        /* =========================
           SETTINGS
        ========================= */

        .settings-title {
            color: #111827;
            font-size: 1.05rem;
            font-weight: 750;
            padding-bottom: 0.8rem;
            margin-bottom: 1rem;
            border-bottom: 1px solid #e5e7eb;
        }

        .settings-section {
            color: #94a3b8;
            font-size: 0.68rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-top: 1rem;
            margin-bottom: 0.55rem;
        }

        label {
            color: #374151 !important;
            font-weight: 650 !important;
            font-size: 0.8rem !important;
        }

        div[data-baseweb="select"] > div {
            background: #ffffff !important;
            border: 1px solid #cbd5e1 !important;
            border-radius: 9px !important;
        }

        div[data-baseweb="select"] span {
            color: #111827 !important;
        }

        /* =========================
           BUTTON
        ========================= */

        .generate-button .stButton > button {
            width: 100%;
            min-height: 3.1rem;
            background: #2563eb !important;
            color: #ffffff !important;
            border: none !important;
            border-radius: 11px !important;
            font-size: 0.95rem !important;
            font-weight: 750 !important;
            box-shadow: 0 8px 20px rgba(37, 99, 235, 0.18);
        }

        .generate-button .stButton > button:hover {
            background: #1d4ed8 !important;
            color: #ffffff !important;
        }

        /* =========================
           INFO
        ========================= */

        .info-box {
            background: #eff6ff;
            border: 1px solid #dbeafe;
            border-radius: 10px;
            padding: 0.8rem;
            color: #1e40af;
            font-size: 0.75rem;
            line-height: 1.5;
            margin-top: 1rem;
        }

        /* =========================
           AUDIO
        ========================= */

        audio {
            width: 100%;
            margin: 0.5rem 0;
        }

        .footer {
            text-align: center;
            color: #94a3b8;
            font-size: 0.7rem;
            margin-top: 2rem;
        }

        </style>
        """
    ),
    unsafe_allow_html=True,
)


# ============================================================
# SESSION STATE
# ============================================================

if "page" not in st.session_state:
    st.session_state.page = "Voice Studio"

if "audio_data" not in st.session_state:
    st.session_state.audio_data = None

if "history" not in st.session_state:
    st.session_state.history = []

if "manual_api_key" not in st.session_state:
    st.session_state.manual_api_key = ""


# ============================================================
# HELPERS
# ============================================================

def html(content):
    """
    Safely render HTML without indentation being interpreted
    as Markdown code.
    """
    st.markdown(
        textwrap.dedent(content),
        unsafe_allow_html=True,
    )


def get_api_key():

    try:
        if "GOOGLE_API_KEY" in st.secrets:
            return st.secrets["GOOGLE_API_KEY"]
    except Exception:
        pass

    if os.getenv("GOOGLE_API_KEY"):
        return os.getenv("GOOGLE_API_KEY")

    return st.session_state.manual_api_key


def pcm_to_wav(
    pcm_data,
    sample_rate=24000,
    channels=1,
    sample_width=2,
):

    output = io.BytesIO()

    with wave.open(output, "wb") as wav:

        wav.setnchannels(channels)
        wav.setsampwidth(sample_width)
        wav.setframerate(sample_rate)
        wav.writeframes(pcm_data)

    return output.getvalue()


def generate_speech(
    text,
    model,
    voice,
    style,
):

    api_key = get_api_key()

    if not api_key:
        raise ValueError(
            "Google Gemini API key is missing."
        )

    client = genai.Client(api_key=api_key)

    prompt = f"""
Speak the following script using a {style.lower()} speaking style.

Important instructions:
- Sound natural and human-like.
- Use clear pronunciation.
- Use natural pauses.
- Do not add extra words.
- Do not explain the script.
- Only generate the spoken audio.

SCRIPT:

{text}
"""

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name=voice
                    )
                )
            ),
        ),
    )

    if not response.candidates:
        raise RuntimeError(
            "Gemini returned no response."
        )

    for part in response.candidates[0].content.parts:

        if getattr(part, "inline_data", None):

            audio = part.inline_data.data

            if isinstance(audio, str):
                import base64
                audio = base64.b64decode(audio)

            return pcm_to_wav(audio)

    raise RuntimeError(
        "No audio was returned by Gemini."
    )


def count_words(text):

    if not text.strip():
        return 0

    return len(text.split())


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    html(
        """
        <div class="sidebar-brand">
            <div class="sidebar-icon">🎙️</div>
            <div class="sidebar-title">AI Voice Studio</div>
            <div class="sidebar-subtitle">
                Natural AI speech generation
            </div>
        </div>

        <div class="sidebar-divider"></div>

        <div class="sidebar-heading">
            Workspace
        </div>
        """
    )

    if st.button(
        "🎙️  Voice Studio",
        use_container_width=True,
    ):
        st.session_state.page = "Voice Studio"
        st.rerun()

    if st.button(
        "🕘  History",
        use_container_width=True,
    ):
        st.session_state.page = "History"
        st.rerun()

    if st.button(
        "⚙️  Settings",
        use_container_width=True,
    ):
        st.session_state.page = "Settings"
        st.rerun()

    if st.button(
        "ℹ️  About",
        use_container_width=True,
    ):
        st.session_state.page = "About"
        st.rerun()

    st.markdown("---")

    html(
        """
        <div class="sidebar-card">
            <div class="sidebar-card-title">
                ✨ Gemini TTS
            </div>

            <div class="sidebar-card-text">
                Generate natural-sounding speech from
                your scripts using Google's Gemini
                text-to-speech models.
            </div>
        </div>
        """
    )


# ============================================================
# VOICE STUDIO
# ============================================================

if st.session_state.page == "Voice Studio":

    html(
        """
        <div class="page-title">
            AI Voice Studio
        </div>

        <div class="page-subtitle">
            Turn your text into natural-sounding speech.
        </div>
        """
    )

    left, right = st.columns(
        [2.1, 1],
        gap="large",
    )

    # ========================================================
    # LEFT COLUMN
    # ========================================================

    with left:

        html(
            """
            <div class="card">

                <div class="script-header">

                    <div class="script-title">
                        Your Script
                    </div>

                    <div class="script-hint">
                        Write or paste your narration
                    </div>

                </div>
            """
        )

        script = st.text_area(
            "Your Script",
            placeholder=(
                "Type or paste your text here...\n\n"
                "Example:\n"
                "Welcome to AI Voice Studio. "
                "Today we are exploring the future "
                "of artificial intelligence."
            ),
            height=370,
            label_visibility="collapsed",
        )

        words = count_words(script)
        characters = len(script)

        minutes = (
            words / 150
            if words > 0
            else 0
        )

        html(
            f"""
            <div class="counter-row">

                <div class="counter">
                    <strong>{characters:,}</strong>
                    characters
                </div>

                <div class="counter">
                    <strong>{words:,}</strong>
                    words
                </div>

                <div class="counter">
                    <strong>{minutes:.1f}</strong>
                    min estimated
                </div>

            </div>

            </div>
            """
        )

        # Generate button

        html('<div class="generate-button">')

        generate = st.button(
            "✨  Generate Speech",
            use_container_width=True,
        )

        html("</div>")

        # Audio result

        if st.session_state.audio_data:

            html(
                """
                <div class="card">

                    <div class="card-title">
                        🎧 Audio Output
                    </div>

                    <div class="card-description">
                        Your generated voice is ready.
                    </div>
                """
            )

            st.audio(
                st.session_state.audio_data,
                format="audio/wav",
            )

            st.download_button(
                "⬇️ Download WAV",
                data=st.session_state.audio_data,
                file_name="ai_voice.wav",
                mime="audio/wav",
                use_container_width=True,
            )

            html("</div>")

        # Generate

        if generate:

            if not script.strip():

                st.warning(
                    "Please enter some text first."
                )

            else:

                model = st.session_state.get(
                    "selected_model",
                    "gemini-2.5-flash-preview-tts",
                )

                voice = st.session_state.get(
                    "selected_voice",
                    "Kore",
                )

                style = st.session_state.get(
                    "selected_style",
                    "Natural",
                )

                with st.spinner(
                    "Generating your AI voice..."
                ):

                    try:

                        audio = generate_speech(
                            script,
                            model,
                            voice,
                            style,
                        )

                        st.session_state.audio_data = audio

                        st.session_state.history.insert(
                            0,
                            {
                                "time": datetime.now().strftime(
                                    "%Y-%m-%d %H:%M"
                                ),
                                "text": script[:150],
                                "voice": voice,
                                "style": style,
                                "words": words,
                            },
                        )

                        st.success(
                            "Speech generated successfully!"
                        )

                        st.rerun()

                    except Exception as e:

                        st.error(
                            f"Generation failed: {e}"
                        )

    # ========================================================
    # RIGHT COLUMN
    # ========================================================

    with right:

        html(
            """
            <div class="card">

                <div class="settings-title">
                    Voice Settings
                </div>

                <div class="settings-section">
                    AI Engine
                </div>
            """
        )

        models = {
            "Gemini 2.5 Flash TTS":
                "gemini-2.5-flash-preview-tts",

            "Gemini 3.1 Flash TTS":
                "gemini-3.1-flash-tts-preview",
        }

        model_label = st.selectbox(
            "AI Model",
            list(models.keys()),
        )

        st.session_state.selected_model = models[
            model_label
        ]

        html(
            """
            <div class="settings-section">
                Voice
            </div>
            """
        )

        voices = [
            "Kore",
            "Puck",
            "Charon",
            "Fenrir",
            "Aoede",
            "Leda",
            "Orus",
            "Zephyr",
        ]

        voice = st.selectbox(
            "Voice",
            voices,
        )

        st.session_state.selected_voice = voice

        html(
            """
            <div class="settings-section">
                Speaking Style
            </div>
            """
        )

        styles = [
            "Natural",
            "Professional",
            "Friendly",
            "Warm",
            "Calm",
            "Energetic",
            "Dramatic",
            "News",
            "Storytelling",
            "Educational",
        ]

        style = st.selectbox(
            "Speaking Style",
            styles,
        )

        st.session_state.selected_style = style

        html(
            """
            <div class="info-box">
                💡 <strong>Tip:</strong>
                Use punctuation and short paragraphs
                to create more natural narration.
            </div>

            </div>
            """
        )


# ============================================================
# HISTORY
# ============================================================

elif st.session_state.page == "History":

    html(
        """
        <div class="page-title">
            Generation History
        </div>

        <div class="page-subtitle">
            Review your recent voice generations.
        </div>
        """
    )

    if not st.session_state.history:

        html(
            """
            <div class="card">
                <div style="
                    text-align:center;
                    padding:3rem;
                    color:#64748b;
                ">
                    <div style="font-size:2.5rem;">
                        🕘
                    </div>

                    <div style="
                        color:#111827;
                        font-weight:750;
                        margin-top:0.7rem;
                    ">
                        No generations yet
                    </div>

                    <div style="
                        margin-top:0.3rem;
                        font-size:0.8rem;
                    ">
                        Your generated voices will appear here.
                    </div>
                </div>
            </div>
            """
        )

    else:

        for item in st.session_state.history:

            html(
                f"""
                <div class="card">

                    <div style="
                        color:#2563eb;
                        font-size:0.72rem;
                        font-weight:700;
                    ">
                        {item["time"]}
                    </div>

                    <div style="
                        color:#334155;
                        font-size:0.85rem;
                        margin-top:0.4rem;
                    ">
                        {item["text"]}
                    </div>

                    <div style="
                        color:#94a3b8;
                        font-size:0.7rem;
                        margin-top:0.5rem;
                    ">
                        {item["words"]} words
                        · Voice: {item["voice"]}
                        · Style: {item["style"]}
                    </div>

                </div>
                """
            )


# ============================================================
# SETTINGS
# ============================================================

elif st.session_state.page == "Settings":

    html(
        """
        <div class="page-title">
            Settings
        </div>

        <div class="page-subtitle">
            Configure your Gemini API connection.
        </div>
        """
    )

    col1, col2 = st.columns(
        [1.5, 1],
        gap="large",
    )

    with col1:

        html(
            """
            <div class="card">

                <div class="card-title">
                    🔑 Gemini API Key
                </div>

                <div class="card-description">
                    Enter your Gemini API key for this session.
                </div>
            """
        )

        key = st.text_input(
            "Google Gemini API Key",
            type="password",
            placeholder="AIza...",
        )

        if key:
            st.session_state.manual_api_key = key

            st.success(
                "API key saved for this session."
            )

        html("</div>")

    with col2:

        html(
            """
            <div class="card">

                <div class="card-title">
                    🔐 Streamlit Secrets
                </div>

                <div class="card-description">
                    For Streamlit Cloud, the recommended
                    approach is to store the API key in
                    Streamlit Secrets.
                </div>

                <div class="info-box">
                    GOOGLE_API_KEY = "your-api-key"
                </div>

            </div>
            """
        )


# ============================================================
# ABOUT
# ============================================================

elif st.session_state.page == "About":

    html(
        """
        <div class="page-title">
            About AI Voice Studio
        </div>

        <div class="page-subtitle">
            Simple AI-powered text-to-speech generation.
        </div>

        <div class="card">

            <div class="card-title">
                🎙️ AI Voice Studio
            </div>

            <div class="card-description">
                Convert written scripts into natural-sounding
                AI speech using Gemini TTS.
            </div>

            <div style="
                color:#475569;
                font-size:0.85rem;
                line-height:1.7;
            ">
                Write or paste your script, choose a Gemini
                model and voice, select a speaking style,
                and generate your audio.
            </div>

        </div>
        """
    )


# ============================================================
# FOOTER
# ============================================================

html(
    """
    <div class="footer">
        AI Voice Studio · Built with Streamlit + Gemini
    </div>
    """
)
