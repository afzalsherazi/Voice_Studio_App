import os
import io
import wave
import base64
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
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* ========================================================
       GLOBAL
    ======================================================== */

    .stApp {
        background: #F8FAFC;
        color: #0F172A;
    }

    .main .block-container {
        max-width: 1500px;
        padding-top: 2rem;
        padding-bottom: 3rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }

    /* Remove excessive Streamlit top spacing */
    header[data-testid="stHeader"] {
        background: transparent;
    }

    /* ========================================================
       SIDEBAR
    ======================================================== */

    section[data-testid="stSidebar"] {
        background: #FFFFFF;
        border-right: 1px solid #E2E8F0;
    }

    section[data-testid="stSidebar"] > div {
        background: #FFFFFF;
    }

    .sidebar-logo {
        text-align: center;
        padding: 0.5rem 0 0.7rem 0;
    }

    .sidebar-logo-icon {
        font-size: 2.5rem;
        margin-bottom: 0.2rem;
    }

    .sidebar-title {
        color: #0F172A;
        font-size: 1.25rem;
        font-weight: 800;
        letter-spacing: -0.03em;
    }

    .sidebar-subtitle {
        color: #64748B;
        font-size: 0.75rem;
        margin-top: 0.2rem;
    }

    .sidebar-divider {
        height: 1px;
        background: #E2E8F0;
        margin: 1rem 0;
    }

    .sidebar-section-title {
        color: #94A3B8;
        font-size: 0.68rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin: 0.8rem 0 0.5rem 0;
    }

    /* Sidebar buttons */

    section[data-testid="stSidebar"] .stButton > button {
        width: 100%;
        text-align: left;
        justify-content: flex-start;

        background: transparent;
        color: #475569;

        border: none;
        border-radius: 9px;

        min-height: 2.6rem;

        padding-left: 0.85rem;
        padding-right: 0.85rem;

        font-size: 0.86rem;
        font-weight: 600;

        box-shadow: none;
    }

    section[data-testid="stSidebar"] .stButton > button:hover {
        background: #F1F5F9;
        color: #2563EB;
        border: none;
    }

    .nav-active {
        background: #EFF6FF !important;
        color: #2563EB !important;
        border: 1px solid #DBEAFE !important;
    }

    .sidebar-info {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 0.9rem;
        margin-top: 1rem;
    }

    .sidebar-info-title {
        color: #0F172A;
        font-weight: 750;
        font-size: 0.78rem;
        margin-bottom: 0.3rem;
    }

    .sidebar-info-text {
        color: #64748B;
        font-size: 0.7rem;
        line-height: 1.5;
    }

    /* ========================================================
       HEADER
    ======================================================== */

    .app-header {
        margin-bottom: 1.6rem;
    }

    .app-title {
        color: #0F172A;
        font-size: 2.25rem;
        line-height: 1.1;
        font-weight: 850;
        letter-spacing: -0.045em;
        margin-bottom: 0.45rem;
    }

    .app-subtitle {
        color: #64748B;
        font-size: 0.98rem;
    }

    /* ========================================================
       CARDS
    ======================================================== */

    .card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 1.25rem;
        margin-bottom: 1rem;

        box-shadow:
            0 1px 2px rgba(15, 23, 42, 0.03),
            0 8px 25px rgba(15, 23, 42, 0.035);
    }

    .card-title {
        color: #0F172A;
        font-size: 1rem;
        font-weight: 750;
        margin-bottom: 0.25rem;
    }

    .card-subtitle {
        color: #64748B;
        font-size: 0.78rem;
        margin-bottom: 1rem;
    }

    /* ========================================================
       SCRIPT EDITOR
    ======================================================== */

    .editor-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.7rem;
    }

    .editor-title {
        color: #0F172A;
        font-size: 1rem;
        font-weight: 750;
    }

    .editor-hint {
        color: #94A3B8;
        font-size: 0.72rem;
    }

    textarea {
        background: #FFFFFF !important;
        color: #0F172A !important;

        border: 1px solid #CBD5E1 !important;
        border-radius: 12px !important;

        font-size: 0.94rem !important;
        line-height: 1.65 !important;

        padding: 1rem !important;

        box-shadow: none !important;
    }

    textarea::placeholder {
        color: #94A3B8 !important;
        opacity: 1 !important;
    }

    textarea:focus {
        border-color: #2563EB !important;

        box-shadow:
            0 0 0 3px rgba(37, 99, 235, 0.10) !important;
    }

    /* ========================================================
       COUNTERS
    ======================================================== */

    .counter-row {
        display: flex;
        gap: 0.5rem;
        margin-top: 0.65rem;
    }

    .counter {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;

        padding: 0.35rem 0.65rem;

        color: #64748B;
        font-size: 0.72rem;
    }

    .counter strong {
        color: #334155;
    }

    /* ========================================================
       FORM LABELS
    ======================================================== */

    label {
        color: #334155 !important;
        font-weight: 650 !important;
        font-size: 0.79rem !important;
    }

    /* ========================================================
       SELECTBOX
    ======================================================== */

    div[data-baseweb="select"] > div {
        background: #FFFFFF !important;

        border: 1px solid #CBD5E1 !important;
        border-radius: 9px !important;

        color: #0F172A !important;
    }

    div[data-baseweb="select"] span {
        color: #0F172A !important;
    }

    /* ========================================================
       INPUTS
    ======================================================== */

    input {
        color: #0F172A !important;
        background: #FFFFFF !important;
    }

    div[data-baseweb="input"] {
        background: #FFFFFF !important;
        border-radius: 9px !important;
    }

    /* ========================================================
       BUTTONS
    ======================================================== */

    .stButton > button {
        background: #FFFFFF;
        color: #334155;

        border: 1px solid #CBD5E1;
        border-radius: 9px;

        min-height: 2.55rem;

        font-weight: 650;

        transition: all 0.15s ease;
    }

    .stButton > button:hover {
        background: #F8FAFC;
        color: #2563EB;
        border-color: #93C5FD;
    }

    /* Generate button */

    .generate-wrapper .stButton > button {
        width: 100%;

        background: #2563EB !important;
        color: #FFFFFF !important;

        border: none !important;
        border-radius: 11px !important;

        min-height: 3.2rem !important;

        font-size: 0.98rem !important;
        font-weight: 750 !important;

        box-shadow:
            0 8px 18px rgba(37, 99, 235, 0.18);
    }

    .generate-wrapper .stButton > button:hover {
        background: #1D4ED8 !important;
        color: #FFFFFF !important;

        box-shadow:
            0 10px 24px rgba(37, 99, 235, 0.24);
    }

    /* ========================================================
       AUDIO
    ======================================================== */

    audio {
        width: 100%;
        border-radius: 10px;
    }

    /* ========================================================
       INFO BOXES
    ======================================================== */

    .info-box {
        background: #EFF6FF;
        border: 1px solid #DBEAFE;
        border-radius: 10px;

        padding: 0.8rem;

        color: #1E40AF;
        font-size: 0.76rem;
        line-height: 1.5;
    }

    .success-box {
        background: #F0FDF4;
        border: 1px solid #BBF7D0;
        border-radius: 10px;

        padding: 0.8rem;

        color: #166534;
        font-size: 0.78rem;
    }

    .warning-box {
        background: #FFFBEB;
        border: 1px solid #FDE68A;
        border-radius: 10px;

        padding: 0.8rem;

        color: #92400E;
        font-size: 0.76rem;
        line-height: 1.5;
    }

    .error-box {
        background: #FEF2F2;
        border: 1px solid #FECACA;
        border-radius: 10px;

        padding: 0.8rem;

        color: #991B1B;
        font-size: 0.76rem;
        line-height: 1.5;
    }

    /* ========================================================
       SETTINGS
    ======================================================== */

    .settings-heading {
        color: #0F172A;
        font-size: 1rem;
        font-weight: 750;

        padding-bottom: 0.7rem;
        margin-bottom: 0.8rem;

        border-bottom: 1px solid #E2E8F0;
    }

    .settings-section {
        color: #94A3B8;

        font-size: 0.67rem;
        font-weight: 750;

        text-transform: uppercase;
        letter-spacing: 0.08em;

        margin-top: 1rem;
        margin-bottom: 0.55rem;
    }

    /* ========================================================
       SLIDERS
    ======================================================== */

    div[data-testid="stSlider"] {
        padding-top: 0.1rem;
        padding-bottom: 0.45rem;
    }

    /* ========================================================
       HISTORY
    ======================================================== */

    .history-item {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;

        padding: 0.9rem;

        margin-bottom: 0.7rem;
    }

    .history-date {
        color: #2563EB;
        font-size: 0.7rem;
        font-weight: 700;
    }

    .history-text {
        color: #334155;
        font-size: 0.8rem;
        line-height: 1.45;

        margin-top: 0.35rem;
    }

    .history-meta {
        color: #94A3B8;
        font-size: 0.68rem;
        margin-top: 0.4rem;
    }

    /* ========================================================
       DOWNLOAD
    ======================================================== */

    .stDownloadButton > button {
        width: 100%;

        background: #EFF6FF !important;
        color: #1D4ED8 !important;

        border: 1px solid #BFDBFE !important;
        border-radius: 9px !important;

        font-weight: 700 !important;
    }

    .stDownloadButton > button:hover {
        background: #DBEAFE !important;
    }

    /* ========================================================
       FOOTER
    ======================================================== */

    .footer {
        text-align: center;

        color: #94A3B8;

        font-size: 0.7rem;

        padding-top: 2rem;
        padding-bottom: 1rem;
    }

    /* ========================================================
       MOBILE
    ======================================================== */

    @media (max-width: 900px) {

        .main .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
            padding-top: 1.2rem;
        }

        .app-title {
            font-size: 1.7rem;
        }

        .card {
            padding: 1rem;
        }
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SESSION STATE
# ============================================================

if "page" not in st.session_state:
    st.session_state.page = "Voice Studio"

if "history" not in st.session_state:
    st.session_state.history = []

if "audio_data" not in st.session_state:
    st.session_state.audio_data = None

if "audio_filename" not in st.session_state:
    st.session_state.audio_filename = "ai_voice.wav"

if "last_text" not in st.session_state:
    st.session_state.last_text = ""


# ============================================================
# HELPERS
# ============================================================

def get_api_key():
    """
    Get Google Gemini API key.

    Priority:
    1. Streamlit secrets
    2. Environment variable
    3. Session state
    """

    try:
        key = st.secrets.get("GOOGLE_API_KEY")
        if key:
            return key
    except Exception:
        pass

    key = os.getenv("GOOGLE_API_KEY")

    if key:
        return key

    return st.session_state.get("manual_api_key", "")


def pcm_to_wav(pcm_data, channels=1, sample_rate=24000, sample_width=2):
    """
    Convert raw PCM audio returned by Gemini into WAV bytes.
    """

    output = io.BytesIO()

    with wave.open(output, "wb") as wav_file:
        wav_file.setnchannels(channels)
        wav_file.setsampwidth(sample_width)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(pcm_data)

    return output.getvalue()


def generate_speech(
    text,
    model_name,
    voice_name,
    speaking_style,
    speed,
    stability,
    clarity,
    style_intensity,
):
    """
    Generate speech using Gemini TTS.
    """

    api_key = get_api_key()

    if not api_key:
        raise ValueError(
            "Google Gemini API key not found. "
            "Add GOOGLE_API_KEY to Streamlit Secrets."
        )

    client = genai.Client(api_key=api_key)

    # --------------------------------------------------------
    # Style prompt
    # --------------------------------------------------------

    speed_description = (
        "very slow"
        if speed < 0.80
        else "slow"
        if speed < 0.95
        else "normal"
        if speed < 1.08
        else "slightly fast"
        if speed < 1.20
        else "fast"
    )

    style_description = {
        "Natural": "Speak naturally and conversationally.",
        "Professional": "Speak in a polished, professional presenter style.",
        "Warm": "Speak warmly, naturally, and pleasantly.",
        "Friendly": "Speak in a friendly and approachable manner.",
        "Calm": "Speak calmly with relaxed pacing.",
        "Energetic": "Speak with energetic and engaging delivery.",
        "Dramatic": "Use expressive and dramatic narration.",
        "News": "Use a clear, confident news presenter style.",
        "Storytelling": "Use expressive storytelling with natural emotional variation.",
        "Educational": "Speak clearly and confidently as an educational narrator.",
    }

    style_instruction = style_description.get(
        speaking_style,
        "Speak naturally."
    )

    prompt = f"""
Generate speech from the following script.

Voice delivery instructions:
- {style_instruction}
- Speaking speed: {speed_description}.
- Voice stability preference: {stability:.2f}.
- Voice clarity preference: {clarity:.2f}.
- Style intensity: {style_intensity:.2f}.
- Keep the pronunciation clear and natural.
- Do not add words that are not in the script.
- Do not explain the script.
- Do not output anything except the requested speech.

SCRIPT:
{text}
"""

    # --------------------------------------------------------
    # Gemini TTS configuration
    # --------------------------------------------------------

    config = types.GenerateContentConfig(
        response_modalities=["AUDIO"],
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                    voice_name=voice_name
                )
            )
        ),
    )

    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
        config=config,
    )

    # --------------------------------------------------------
    # Extract audio
    # --------------------------------------------------------

    if not response.candidates:
        raise RuntimeError("Gemini returned no candidates.")

    candidate = response.candidates[0]

    if not candidate.content or not candidate.content.parts:
        raise RuntimeError("Gemini returned no audio content.")

    for part in candidate.content.parts:

        if getattr(part, "inline_data", None):

            audio_data = part.inline_data.data

            if isinstance(audio_data, str):
                try:
                    audio_data = base64.b64decode(audio_data)
                except Exception:
                    pass

            if not audio_data:
                continue

            # Gemini TTS returns raw PCM.
            wav_data = pcm_to_wav(audio_data)

            return wav_data

    raise RuntimeError(
        "No audio data was found in Gemini's response."
    )


def count_words(text):
    if not text.strip():
        return 0

    return len(text.split())


def estimate_duration(text):
    """
    Rough speech duration estimate.
    Average narration speed ≈ 150 words/minute.
    """

    words = count_words(text)

    if words == 0:
        return 0

    return words / 150


def render_header(title, subtitle):
    st.markdown(
        f"""
        <div class="app-header">
            <div class="app-title">{title}</div>
            <div class="app-subtitle">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div class="sidebar-logo">
            <div class="sidebar-logo-icon">🎙️</div>
            <div class="sidebar-title">AI Voice Studio</div>
            <div class="sidebar-subtitle">
                Natural AI speech generation
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

    st.markdown(
        '<div class="sidebar-section-title">Workspace</div>',
        unsafe_allow_html=True,
    )

    # Voice Studio
    if st.button(
        "🎙️  Voice Studio",
        key="nav_voice",
        use_container_width=True,
    ):
        st.session_state.page = "Voice Studio"

    # History
    if st.button(
        "🕘  History",
        key="nav_history",
        use_container_width=True,
    ):
        st.session_state.page = "History"

    # Settings
    if st.button(
        "⚙️  Settings",
        key="nav_settings",
        use_container_width=True,
    ):
        st.session_state.page = "Settings"

    # About
    if st.button(
        "ℹ️  About",
        key="nav_about",
        use_container_width=True,
    ):
        st.session_state.page = "About"

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="sidebar-info">
            <div class="sidebar-info-title">
                ✨ Gemini TTS
            </div>

            <div class="sidebar-info-text">
                Generate natural-sounding speech from
                your scripts using Google's Gemini
                text-to-speech models.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="footer">
            AI Voice Studio<br>
            Built with Streamlit + Gemini
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# PAGE: VOICE STUDIO
# ============================================================

if st.session_state.page == "Voice Studio":

    render_header(
        "AI Voice Studio",
        "Turn your text into natural-sounding speech.",
    )

    left_col, right_col = st.columns(
        [2.05, 1],
        gap="large",
    )

    # ========================================================
    # LEFT
    # ========================================================

    with left_col:

        st.markdown(
            """
            <div class="card">
                <div class="editor-header">
                    <div class="editor-title">
                        Your Script
                    </div>

                    <div class="editor-hint">
                        Write or paste your narration
                    </div>
                </div>
            """,
            unsafe_allow_html=True,
        )

        script = st.text_area(
            "Script",
            value=st.session_state.last_text,
            height=360,
            placeholder=(
                "Type or paste your text here...\n\n"
                "Example:\n"
                "Welcome to AI Voice Studio. "
                "Today we are exploring the future of artificial intelligence."
            ),
            label_visibility="collapsed",
            key="script_input",
        )

        words = count_words(script)
        characters = len(script)
        duration = estimate_duration(script)

        st.markdown(
            f"""
            <div class="counter-row">
                <div class="counter">
                    <strong>{characters:,}</strong> characters
                </div>

                <div class="counter">
                    <strong>{words:,}</strong> words
                </div>

                <div class="counter">
                    <strong>{duration:.1f}</strong> min estimated
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("</div>", unsafe_allow_html=True)

        # ----------------------------------------------------
        # Generate
        # ----------------------------------------------------

        st.markdown(
            '<div class="generate-wrapper">',
            unsafe_allow_html=True,
        )

        generate = st.button(
            "✨  Generate Speech",
            use_container_width=True,
        )

        st.markdown("</div>", unsafe_allow_html=True)

        # ----------------------------------------------------
        # Audio output
        # ----------------------------------------------------

        if st.session_state.audio_data:

            st.markdown(
                """
                <div class="card">
                    <div class="card-title">
                        🎧 Audio Output
                    </div>

                    <div class="card-subtitle">
                        Your generated voice is ready.
                    </div>
                """,
                unsafe_allow_html=True,
            )

            st.audio(
                st.session_state.audio_data,
                format="audio/wav",
            )

            st.download_button(
                label="⬇️ Download WAV Audio",
                data=st.session_state.audio_data,
                file_name=st.session_state.audio_filename,
                mime="audio/wav",
                use_container_width=True,
            )

            st.markdown("</div>", unsafe_allow_html=True)

        # ----------------------------------------------------
        # Generate speech
        # ----------------------------------------------------

        if generate:

            if not script.strip():

                st.error(
                    "Please enter some text before generating speech."
                )

            elif len(script) > 30000:

                st.error(
                    "Your script is too long. "
                    "Please split it into smaller sections."
                )

            else:

                # Settings from session state
                selected_model = st.session_state.get(
                    "selected_model",
                    "gemini-2.5-flash-preview-tts",
                )

                selected_voice = st.session_state.get(
                    "selected_voice",
                    "Kore",
                )

                selected_style = st.session_state.get(
                    "selected_style",
                    "Natural",
                )

                selected_speed = st.session_state.get(
                    "selected_speed",
                    1.0,
                )

                selected_stability = st.session_state.get(
                    "selected_stability",
                    0.70,
                )

                selected_clarity = st.session_state.get(
                    "selected_clarity",
                    0.80,
                )

                selected_intensity = st.session_state.get(
                    "selected_intensity",
                    0.50,
                )

                with st.spinner(
                    "Generating your AI voice..."
                ):

                    try:

                        audio = generate_speech(
                            text=script,
                            model_name=selected_model,
                            voice_name=selected_voice,
                            speaking_style=selected_style,
                            speed=selected_speed,
                            stability=selected_stability,
                            clarity=selected_clarity,
                            style_intensity=selected_intensity,
                        )

                        st.session_state.audio_data = audio
                        st.session_state.last_text = script

                        timestamp = datetime.now().strftime(
                            "%Y%m%d_%H%M%S"
                        )

                        st.session_state.audio_filename = (
                            f"ai_voice_{timestamp}.wav"
                        )

                        # Add history
                        st.session_state.history.insert(
                            0,
                            {
                                "time": datetime.now().strftime(
                                    "%Y-%m-%d %H:%M"
                                ),
                                "text": script[:160],
                                "words": words,
                                "voice": selected_voice,
                                "model": selected_model,
                                "style": selected_style,
                            },
                        )

                        # Keep last 20
                        st.session_state.history = (
                            st.session_state.history[:20]
                        )

                        st.success(
                            "Speech generated successfully!"
                        )

                        st.rerun()

                    except Exception as e:

                        st.error(
                            f"Speech generation failed: {str(e)}"
                        )

    # ========================================================
    # RIGHT SETTINGS
    # ========================================================

    with right_col:

        st.markdown(
            """
            <div class="card">

                <div class="settings-heading">
                    Voice Settings
                </div>

                <div class="settings-section">
                    AI Engine
                </div>

            """,
            unsafe_allow_html=True,
        )

        # ----------------------------------------------------
        # Model
        # ----------------------------------------------------

        model_options = {
            "Gemini 2.5 Flash TTS": "gemini-2.5-flash-preview-tts",
            "Gemini 3.1 Flash TTS": "gemini-3.1-flash-tts-preview",
            "Gemini 2.5 Pro TTS": "gemini-2.5-pro-preview-tts",
        }

        current_model = st.session_state.get(
            "selected_model",
            "gemini-2.5-flash-preview-tts",
        )

        current_model_label = next(
            (
                label
                for label, model in model_options.items()
                if model == current_model
            ),
            "Gemini 2.5 Flash TTS",
        )

        model_label = st.selectbox(
            "AI Model",
            options=list(model_options.keys()),
            index=list(model_options.keys()).index(
                current_model_label
            ),
            key="model_selector",
        )

        st.session_state.selected_model = model_options[
            model_label
        ]

        # ----------------------------------------------------
        # Voice
        # ----------------------------------------------------

        st.markdown(
            '<div class="settings-section">Voice</div>',
            unsafe_allow_html=True,
        )

        voice_options = [
            "Kore",
            "Puck",
            "Charon",
            "Fenrir",
            "Aoede",
            "Leda",
            "Orus",
            "Zephyr",
            "Callirrhoe",
            "Autonoe",
            "Enceladus",
            "Iapetus",
            "Umbriel",
            "Algieba",
            "Despina",
            "Erinome",
            "Gacrux",
            "Laomedeia",
            "Achernar",
            "Schedar",
            "Achird",
            "Zubenelgenubi",
            "Sadachbia",
            "Sadaltager",
            "Sulafat",
        ]

        voice = st.selectbox(
            "Voice",
            voice_options,
            index=voice_options.index(
                st.session_state.get(
                    "selected_voice",
                    "Kore",
                )
            )
            if st.session_state.get(
                "selected_voice",
                "Kore",
            )
            in voice_options
            else 0,
        )

        st.session_state.selected_voice = voice

        # ----------------------------------------------------
        # Speaking style
        # ----------------------------------------------------

        style_options = [
            "Natural",
            "Professional",
            "Warm",
            "Friendly",
            "Calm",
            "Energetic",
            "Dramatic",
            "News",
            "Storytelling",
            "Educational",
        ]

        speaking_style = st.selectbox(
            "Speaking Style",
            style_options,
            index=style_options.index(
                st.session_state.get(
                    "selected_style",
                    "Natural",
                )
            ),
        )

        st.session_state.selected_style = speaking_style

        # ----------------------------------------------------
        # Voice controls
        # ----------------------------------------------------

        st.markdown(
            '<div class="settings-section">Voice Controls</div>',
            unsafe_allow_html=True,
        )

        speed = st.slider(
            "Speaking Speed",
            min_value=0.60,
            max_value=1.40,
            value=float(
                st.session_state.get(
                    "selected_speed",
                    1.0,
                )
            ),
            step=0.05,
            help="Controls the requested speaking pace.",
        )

        st.session_state.selected_speed = speed

        stability = st.slider(
            "Voice Stability",
            min_value=0.0,
            max_value=1.0,
            value=float(
                st.session_state.get(
                    "selected_stability",
                    0.70,
                )
            ),
            step=0.05,
        )

        st.session_state.selected_stability = stability

        clarity = st.slider(
            "Voice Clarity",
            min_value=0.0,
            max_value=1.0,
            value=float(
                st.session_state.get(
                    "selected_clarity",
                    0.80,
                )
            ),
            step=0.05,
        )

        st.session_state.selected_clarity = clarity

        intensity = st.slider(
            "Style Intensity",
            min_value=0.0,
            max_value=1.0,
            value=float(
                st.session_state.get(
                    "selected_intensity",
                    0.50,
                )
            ),
            step=0.05,
        )

        st.session_state.selected_intensity = intensity

        st.markdown("</div>", unsafe_allow_html=True)

        # ----------------------------------------------------
        # Tip
        # ----------------------------------------------------

        st.markdown(
            """
            <div class="info-box">
                <strong>💡 Tip</strong><br>
                Use punctuation, short paragraphs, and natural
                wording to get better narration results.
            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# PAGE: HISTORY
# ============================================================

elif st.session_state.page == "History":

    render_header(
        "Generation History",
        "Review your recent voice generations.",
    )

    if not st.session_state.history:

        st.markdown(
            """
            <div class="card">
                <div style="
                    text-align:center;
                    padding:2rem;
                ">
                    <div style="font-size:2.5rem;">
                        🕘
                    </div>

                    <div style="
                        color:#0F172A;
                        font-size:1rem;
                        font-weight:750;
                        margin-top:0.7rem;
                    ">
                        No generations yet
                    </div>

                    <div style="
                        color:#64748B;
                        font-size:0.8rem;
                        margin-top:0.3rem;
                    ">
                        Generate your first voice from the
                        Voice Studio.
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    else:

        if st.button(
            "🗑️ Clear History",
            key="clear_history",
        ):

            st.session_state.history = []
            st.rerun()

        for item in st.session_state.history:

            st.markdown(
                f"""
                <div class="history-item">

                    <div class="history-date">
                        {item["time"]}
                    </div>

                    <div class="history-text">
                        {item["text"]}
                    </div>

                    <div class="history-meta">
                        {item["words"]} words
                        &nbsp; • &nbsp;
                        Voice: {item["voice"]}
                        &nbsp; • &nbsp;
                        Style: {item["style"]}
                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )


# ============================================================
# PAGE: SETTINGS
# ============================================================

elif st.session_state.page == "Settings":

    render_header(
        "Settings",
        "Configure your Gemini API connection.",
    )

    col1, col2 = st.columns(
        [1.5, 1],
        gap="large",
    )

    with col1:

        st.markdown(
            """
            <div class="card">

                <div class="card-title">
                    🔑 Gemini API
                </div>

                <div class="card-subtitle">
                    Your API key is used only for the current
                    Streamlit session when entered here.
                </div>

            """,
            unsafe_allow_html=True,
        )

        api_key = st.text_input(
            "Google Gemini API Key",
            type="password",
            value=st.session_state.get(
                "manual_api_key",
                "",
            ),
            placeholder="AIza...",
        )

        if api_key:
            st.session_state.manual_api_key = api_key

            st.markdown(
                """
                <div class="success-box">
                    ✓ API key is available for this session.
                </div>
                """,
                unsafe_allow_html=True,
            )

        else:

            st.markdown(
                """
                <div class="warning-box">
                    No API key entered. For Streamlit Cloud,
                    the recommended method is to store your
                    key in Streamlit Secrets as
                    <strong>GOOGLE_API_KEY</strong>.
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("</div>", unsafe_allow_html=True)

    with col2:

        st.markdown(
            """
            <div class="card">

                <div class="card-title">
                    🔐 Recommended
                </div>

                <div class="card-subtitle">
                    Use Streamlit Secrets instead of putting
                    your API key directly into your source code.
                </div>

                <div class="info-box">
                    In Streamlit Cloud, open your app settings,
                    choose Secrets, and add:
                    <br><br>
                    <strong>
                    GOOGLE_API_KEY = "your-key-here"
                    </strong>
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# PAGE: ABOUT
# ============================================================

elif st.session_state.page == "About":

    render_header(
        "About AI Voice Studio",
        "A simple AI-powered text-to-speech workspace.",
    )

    col1, col2 = st.columns(
        [1.4, 1],
        gap="large",
    )

    with col1:

        st.markdown(
            """
            <div class="card">

                <div class="card-title">
                    🎙️ AI Voice Studio
                </div>

                <div class="card-subtitle">
                    Convert written scripts into natural-sounding
                    AI speech.
                </div>

                <p style="
                    color:#475569;
                    font-size:0.85rem;
                    line-height:1.7;
                ">
                    AI Voice Studio provides a clean workspace
                    for generating narration from text using
                    Google's Gemini text-to-speech models.
                </p>

                <p style="
                    color:#475569;
                    font-size:0.85rem;
                    line-height:1.7;
                ">
                    You can choose a Gemini TTS model, select
                    a voice, adjust speaking style and control
                    the requested delivery characteristics.
                </p>

            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:

        st.markdown(
            """
            <div class="card">

                <div class="card-title">
                    ✨ Features
                </div>

                <div style="
                    color:#475569;
                    font-size:0.82rem;
                    line-height:2;
                ">
                    🎙️ Multiple Gemini voices<br>
                    🤖 Multiple TTS models<br>
                    🎚️ Speaking speed control<br>
                    🎭 Speaking styles<br>
                    🎧 Built-in audio player<br>
                    ⬇️ WAV download<br>
                    🕘 Session history<br>
                    ☁️ Streamlit Cloud ready
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
        AI Voice Studio · Streamlit · Google Gemini TTS
    </div>
    """,
    unsafe_allow_html=True,
)
