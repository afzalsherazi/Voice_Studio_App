import html
import io
import json
import re
import struct
import wave
from datetime import datetime

import streamlit as st
import streamlit.components.v1 as components

from google import genai
from google.genai import types


# ============================================================
# APPLICATION CONFIGURATION
# ============================================================

APP_TITLE = "AI Voice Studio"

# Current Gemini TTS model.
# If Google changes the model name, change this single constant.
DEFAULT_MODEL = "gemini-3.1-flash-tts-preview"

# Alternative currently documented Gemini TTS model.
ALTERNATIVE_MODEL = "gemini-2.5-flash-preview-tts"

# Gemini TTS currently returns PCM at 24 kHz in the documented example.
SAMPLE_RATE = 24000
CHANNELS = 1
SAMPLE_WIDTH = 2  # 16-bit PCM

# Keep requests reasonably small for a free/demo application.
MAX_CHARACTERS = 12000


# ============================================================
# VOICE CONFIGURATION
# ============================================================

VOICE_OPTIONS = {
    "Kore — Firm": {
        "name": "Kore",
        "description": "Firm and clear",
    },
    "Puck — Upbeat": {
        "name": "Puck",
        "description": "Upbeat and lively",
    },
    "Charon — Informative": {
        "name": "Charon",
        "description": "Informative and professional",
    },
    "Fenrir — Excitable": {
        "name": "Fenrir",
        "description": "Energetic and expressive",
    },
    "Aoede — Breezy": {
        "name": "Aoede",
        "description": "Warm and relaxed",
    },
    "Leda — Youthful": {
        "name": "Leda",
        "description": "Youthful and bright",
    },
    "Orus — Firm": {
        "name": "Orus",
        "description": "Strong and controlled",
    },
    "Zephyr — Bright": {
        "name": "Zephyr",
        "description": "Bright and clear",
    },
}


# ============================================================
# SPEAKING STYLES
# ============================================================

STYLE_INSTRUCTIONS = {
    "Natural": "Speak naturally with a relaxed and balanced delivery.",
    "Professional": (
        "Speak professionally, clearly and confidently. "
        "Use precise pronunciation and a polished delivery."
    ),
    "Friendly": (
        "Speak in a warm, friendly and approachable way. "
        "Sound helpful and natural."
    ),
    "Energetic": (
        "Speak with energetic, lively and engaging delivery. "
        "Keep the speech clear and enthusiastic."
    ),
    "Calm": (
        "Speak calmly and smoothly with a relaxed, reassuring delivery."
    ),
    "Narration": (
        "Use a polished narration style with clear pronunciation, "
        "controlled pacing and expressive emphasis."
    ),
    "News": (
        "Use a professional news-reader style. "
        "Speak clearly, confidently and objectively."
    ),
    "Storytelling": (
        "Use expressive storytelling. "
        "Vary emphasis naturally and make the delivery engaging."
    ),
    "Podcast": (
        "Use a natural conversational podcast style. "
        "Sound relaxed, intelligent and engaging."
    ),
    "Deep & Dramatic": (
        "Use a dramatic, serious and expressive delivery. "
        "Emphasize important words naturally."
    ),
}


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title=APP_TITLE,
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

    /* ---------- Global ---------- */

    .stApp {
        background:
            radial-gradient(
                circle at top right,
                rgba(37, 99, 235, 0.12),
                transparent 35%
            ),
            #07111f;
        color: #f8fafc;
    }

    .main .block-container {
        max-width: 1500px;
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }

    /* ---------- Sidebar ---------- */

    [data-testid="stSidebar"] {
        background: #081321;
        border-right: 1px solid rgba(148, 163, 184, 0.12);
    }

    [data-testid="stSidebar"] h1 {
        font-size: 1.35rem;
    }

    .sidebar-brand {
        padding: 0.5rem 0 1.4rem 0;
    }

    .sidebar-brand-icon {
        font-size: 2rem;
    }

    .sidebar-brand-title {
        font-size: 1.25rem;
        font-weight: 800;
        margin-top: 0.35rem;
    }

    .sidebar-brand-subtitle {
        color: #94a3b8;
        font-size: 0.78rem;
    }

    /* ---------- Header ---------- */

    .app-header {
        margin-bottom: 1.4rem;
    }

    .app-title {
        font-size: 2rem;
        line-height: 1.1;
        font-weight: 800;
        letter-spacing: -0.03em;
    }

    .app-subtitle {
        color: #94a3b8;
        margin-top: 0.45rem;
        font-size: 0.95rem;
    }

    /* ---------- Cards ---------- */

    .studio-card {
        background: rgba(15, 27, 45, 0.94);
        border: 1px solid rgba(148, 163, 184, 0.13);
        border-radius: 18px;
        padding: 1.15rem;
        box-shadow: 0 14px 35px rgba(0, 0, 0, 0.16);
        margin-bottom: 1rem;
    }

    .card-title {
        font-weight: 700;
        font-size: 1rem;
        margin-bottom: 0.65rem;
    }

    .card-description {
        color: #94a3b8;
        font-size: 0.82rem;
        line-height: 1.45;
    }

    /* ---------- Text area ---------- */

    textarea {
        background-color: #091525 !important;
        color: #f8fafc !important;
        border-radius: 14px !important;
    }

    textarea:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 1px #3b82f6 !important;
    }

    /* ---------- Buttons ---------- */

    .stButton > button {
        border-radius: 10px;
        border: 1px solid rgba(148, 163, 184, 0.18);
        background: #111f32;
        color: #f8fafc;
        font-weight: 600;
        min-height: 2.6rem;
    }

    .stButton > button:hover {
        border-color: #3b82f6;
        color: #ffffff;
    }

    .generate-button button {
        background: linear-gradient(135deg, #2563eb, #3b82f6) !important;
        border: none !important;
        min-height: 3.2rem !important;
        font-size: 1rem !important;
        font-weight: 800 !important;
        box-shadow: 0 8px 24px rgba(37, 99, 235, 0.25);
    }

    /* ---------- Metrics ---------- */

    .counter-row {
        display: flex;
        gap: 0.6rem;
        margin-top: 0.7rem;
        margin-bottom: 0.9rem;
    }

    .counter {
        background: #0b192b;
        border: 1px solid rgba(148, 163, 184, 0.10);
        border-radius: 9px;
        padding: 0.35rem 0.65rem;
        color: #94a3b8;
        font-size: 0.78rem;
    }

    .counter strong {
        color: #e2e8f0;
    }

    /* ---------- Info ---------- */

    .info-box {
        background: rgba(37, 99, 235, 0.08);
        border: 1px solid rgba(59, 130, 246, 0.20);
        border-radius: 12px;
        padding: 0.75rem;
        color: #cbd5e1;
        font-size: 0.78rem;
        line-height: 1.5;
    }

    .warning-box {
        background: rgba(245, 158, 11, 0.08);
        border: 1px solid rgba(245, 158, 11, 0.20);
        border-radius: 12px;
        padding: 0.75rem;
        color: #fbbf24;
        font-size: 0.78rem;
        line-height: 1.5;
    }

    .success-box {
        background: rgba(34, 197, 94, 0.08);
        border: 1px solid rgba(34, 197, 94, 0.20);
        border-radius: 12px;
        padding: 0.75rem;
        color: #86efac;
        font-size: 0.82rem;
    }

    /* ---------- History ---------- */

    .history-item {
        background: #0b192b;
        border: 1px solid rgba(148, 163, 184, 0.10);
        border-radius: 10px;
        padding: 0.7rem;
        margin-bottom: 0.55rem;
    }

    .history-time {
        color: #60a5fa;
        font-size: 0.72rem;
    }

    .history-text {
        color: #e2e8f0;
        font-size: 0.8rem;
        margin-top: 0.25rem;
    }

    /* ---------- Footer ---------- */

    .footer {
        text-align: center;
        color: #64748b;
        font-size: 0.75rem;
        padding-top: 2rem;
    }

    /* ---------- Responsive ---------- */

    @media (max-width: 900px) {
        .app-title {
            font-size: 1.55rem;
        }
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SESSION STATE
# ============================================================

if "history" not in st.session_state:
    st.session_state.history = []

if "generated_audio" not in st.session_state:
    st.session_state.generated_audio = None

if "generated_filename" not in st.session_state:
    st.session_state.generated_filename = "ai_voice.wav"

if "generation_info" not in st.session_state:
    st.session_state.generation_info = None

if "text_input" not in st.session_state:
    st.session_state.text_input = ""


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def get_api_key():
    """
    Read the Gemini API key from Streamlit secrets.

    The key is never placed into session_state or displayed.
    """
    try:
        key = st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        return ""

    if not key:
        return ""

    return str(key).strip()


def count_words(text):
    """Count words using a Unicode-friendly regex."""
    return len(re.findall(r"\S+", text.strip()))


def clear_text():
    """Clear the text editor."""
    st.session_state.text_input = ""
    st.session_state.generated_audio = None
    st.session_state.generation_info = None


def clear_history():
    """Clear session history."""
    st.session_state.history = []


def build_tts_prompt(
    text,
    speaking_style,
    custom_style,
    speed,
    consistency,
    character,
    style_intensity,
):
    """
    Build a natural-language TTS instruction.

    Gemini TTS uses natural-language instructions for controllable
    delivery rather than ElevenLabs-specific parameters.
    """

    base_style = STYLE_INSTRUCTIONS.get(
        speaking_style,
        STYLE_INSTRUCTIONS["Natural"],
    )

    custom_style = custom_style.strip()

    # Speed is communicated as natural language because Gemini TTS
    # does not expose an ElevenLabs-style speed slider parameter.
    if speed < 0.85:
        pace_instruction = (
            "Speak noticeably slower than normal, with comfortable pauses."
        )
    elif speed < 0.95:
        pace_instruction = (
            "Speak slightly slower than normal with clear pacing."
        )
    elif speed <= 1.05:
        pace_instruction = "Use a natural, moderate speaking pace."
    elif speed <= 1.15:
        pace_instruction = (
            "Speak slightly faster than normal while maintaining clarity."
        )
    else:
        pace_instruction = (
            "Speak noticeably faster than normal while maintaining clear "
            "pronunciation."
        )

    # Application-level consistency control.
    if consistency < 0.35:
        consistency_instruction = (
            "Allow expressive vocal variation and natural emotional changes."
        )
    elif consistency < 0.70:
        consistency_instruction = (
            "Keep the delivery reasonably consistent while allowing "
            "natural expressive variation."
        )
    else:
        consistency_instruction = (
            "Keep the delivery consistent, controlled and steady."
        )

    # Application-level voice character control.
    if character < 0.35:
        character_instruction = (
            "Keep the vocal character close to a neutral interpretation."
        )
    elif character < 0.70:
        character_instruction = (
            "Use a moderately distinctive vocal character."
        )
    else:
        character_instruction = (
            "Use a clearly pronounced and distinctive vocal character."
        )

    # Style intensity.
    if style_intensity < 0.35:
        intensity_instruction = (
            "Keep stylistic expression subtle."
        )
    elif style_intensity < 0.70:
        intensity_instruction = (
            "Use noticeable emotional and stylistic expression."
        )
    else:
        intensity_instruction = (
            "Use strong expressive delivery and clear stylistic emphasis."
        )

    prompt_parts = [
        "Generate natural spoken audio for the following text.",
        base_style,
        pace_instruction,
        consistency_instruction,
        character_instruction,
        intensity_instruction,
    ]

    if custom_style:
        prompt_parts.append(
            f"Additional speaking direction: {custom_style}"
        )

    prompt_parts.append(
        "\nIMPORTANT: Speak only the supplied text. "
        "Do not read these instructions aloud."
    )

    prompt_parts.append(
        f"\nTEXT TO SPEAK:\n{text}"
    )

    return "\n\n".join(prompt_parts)


def extract_audio_bytes(response):
    """
    Extract inline PCM audio bytes from a Gemini GenerateContent response.
    """
    try:
        candidates = getattr(response, "candidates", None)

        if not candidates:
            raise ValueError("Gemini returned no candidates.")

        content = getattr(candidates[0], "content", None)

        if content is None:
            raise ValueError("Gemini returned no content.")

        parts = getattr(content, "parts", None)

        if not parts:
            raise ValueError("Gemini returned no audio parts.")

        for part in parts:
            inline_data = getattr(part, "inline_data", None)

            if inline_data is not None:
                data = getattr(inline_data, "data", None)

                if data:
                    return data

        raise ValueError("Gemini response did not contain audio data.")

    except Exception as exc:
        raise ValueError(
            f"Unable to extract audio from Gemini response: {exc}"
        ) from exc


def pcm_to_wav(
    pcm_bytes,
    sample_rate=SAMPLE_RATE,
    channels=CHANNELS,
    sample_width=SAMPLE_WIDTH,
):
    """
    Convert raw PCM bytes to a valid WAV file.

    Gemini's documented TTS response is raw PCM, so simply naming
    the file .wav is not sufficient.
    """
    output = io.BytesIO()

    with wave.open(output, "wb") as wav_file:
        wav_file.setnchannels(channels)
        wav_file.setsampwidth(sample_width)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(pcm_bytes)

    return output.getvalue()


def adjust_pcm_speed(
    pcm_bytes,
    speed,
    channels=CHANNELS,
    sample_width=SAMPLE_WIDTH,
):
    """
    Locally adjust PCM playback speed using linear sample interpolation.

    This is an application-level audio transformation. It does not claim
    that Gemini exposes a direct speed API parameter.

    Values above 1.0 make audio faster.
    Values below 1.0 make audio slower.
    """

    if abs(speed - 1.0) < 0.001:
        return pcm_bytes

    if sample_width != 2:
        return pcm_bytes

    if channels != 1:
        return pcm_bytes

    if len(pcm_bytes) < 4:
        return pcm_bytes

    sample_count = len(pcm_bytes) // 2

    try:
        samples = struct.unpack(
            "<{}h".format(sample_count),
            pcm_bytes[: sample_count * 2],
        )
    except struct.error:
        return pcm_bytes

    if len(samples) < 2:
        return pcm_bytes

    new_count = max(
        2,
        int(len(samples) / speed),
    )

    result = bytearray(new_count * 2)

    max_index = len(samples) - 1

    for i in range(new_count):
        source_position = i * speed

        if source_position >= max_index:
            source_position = max_index

        left_index = int(source_position)
        right_index = min(left_index + 1, max_index)

        fraction = source_position - left_index

        value = (
            samples[left_index]
            + (samples[right_index] - samples[left_index]) * fraction
        )

        value = max(-32768, min(32767, int(value)))

        struct.pack_into(
            "<h",
            result,
            i * 2,
            value,
        )

    return bytes(result)


def process_audio(pcm_bytes, speed):
    """
    Apply local speed processing and return a valid WAV file.
    """
    processed_pcm = adjust_pcm_speed(pcm_bytes, speed)

    return pcm_to_wav(
        processed_pcm,
        sample_rate=SAMPLE_RATE,
        channels=CHANNELS,
        sample_width=SAMPLE_WIDTH,
    )


def generate_speech(
    text,
    model,
    voice_name,
    speaking_style,
    custom_style,
    speed,
    consistency,
    character,
    style_intensity,
):
    """
    Generate TTS audio using the official Google GenAI Python SDK.
    """

    api_key = get_api_key()

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured in Streamlit Secrets."
        )

    client = genai.Client(api_key=api_key)

    prompt = build_tts_prompt(
        text=text,
        speaking_style=speaking_style,
        custom_style=custom_style,
        speed=speed,
        consistency=consistency,
        character=character,
        style_intensity=style_intensity,
    )

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name=voice_name,
                    )
                )
            ),
        ),
    )

    pcm_bytes = extract_audio_bytes(response)

    if not pcm_bytes:
        raise RuntimeError(
            "Gemini returned an empty audio response."
        )

    wav_bytes = process_audio(
        pcm_bytes=pcm_bytes,
        speed=speed,
    )

    return wav_bytes


def add_history(
    text,
    voice,
    model,
    style,
):
    """Add a generation event to session history."""
    preview = text.strip().replace("\n", " ")

    if len(preview) > 110:
        preview = preview[:107] + "..."

    st.session_state.history.insert(
        0,
        {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "voice": voice,
            "model": model,
            "style": style,
            "text": preview,
        },
    )

    # Keep memory small.
    st.session_state.history = st.session_state.history[:20]


# ============================================================
# BROWSER TTS
# ============================================================

def render_browser_tts(text):
    """
    Render a browser-native SpeechSynthesis fallback.

    This runs on the user's browser and does not require an API key.
    """

    safe_text = json.dumps(text)

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                margin: 0;
                background: transparent;
                font-family: Arial, sans-serif;
            }}

            .wrapper {{
                display: flex;
                gap: 8px;
                flex-wrap: wrap;
            }}

            button {{
                border: 1px solid rgba(148,163,184,.25);
                background: #111f32;
                color: #f8fafc;
                padding: 10px 16px;
                border-radius: 9px;
                cursor: pointer;
                font-size: 14px;
                font-weight: 600;
            }}

            button:hover {{
                border-color: #3b82f6;
            }}

            #status {{
                color: #94a3b8;
                font-size: 12px;
                margin-top: 8px;
            }}
        </style>
    </head>

    <body>

        <div class="wrapper">
            <button onclick="speak()">🔊 Speak in Browser</button>
            <button onclick="stopSpeech()">⏹ Stop</button>
        </div>

        <div id="status">
            Browser TTS — Free fallback
        </div>

        <script>
            const text = {safe_text};

            function speak() {{
                if (!('speechSynthesis' in window)) {{
                    document.getElementById("status").innerText =
                        "Browser speech synthesis is not supported.";
                    return;
                }}

                window.speechSynthesis.cancel();

                const utterance =
                    new SpeechSynthesisUtterance(text);

                utterance.rate = 1.0;
                utterance.pitch = 1.0;

                utterance.onstart = function() {{
                    document.getElementById("status").innerText =
                        "Browser TTS is speaking...";
                }};

                utterance.onend = function() {{
                    document.getElementById("status").innerText =
                        "Browser TTS finished.";
                }};

                utterance.onerror = function() {{
                    document.getElementById("status").innerText =
                        "Browser TTS could not speak this text.";
                }};

                window.speechSynthesis.speak(utterance);
            }}

            function stopSpeech() {{
                if ('speechSynthesis' in window) {{
                    window.speechSynthesis.cancel();
                    document.getElementById("status").innerText =
                        "Browser TTS stopped.";
                }}
            }}
        </script>

    </body>
    </html>
    """

    components.html(
        html_content,
        height=72,
        scrolling=False,
    )


# ============================================================
# SIDEBAR
# ============================================================

def render_sidebar():
    with st.sidebar:

        st.markdown(
            """
            <div class="sidebar-brand">
                <div class="sidebar-brand-icon">🎙️</div>
                <div class="sidebar-brand-title">
                    AI Voice Studio
                </div>
                <div class="sidebar-brand-subtitle">
                    Natural AI speech generation
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        page = st.radio(
            "Navigation",
            [
                "🎙️ Voice Studio",
                "🕘 History",
                "⚙️ Settings",
                "ℹ️ About",
            ],
            label_visibility="collapsed",
        )

        st.markdown("---")

        st.markdown(
            """
            <div class="info-box">
                <strong>Gemini TTS</strong><br>
                Powered by Google's Gemini text-to-speech API.
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("")

        st.caption("No database • Session-based history")
        st.caption("Designed for Streamlit Community Cloud")

    return page


# ============================================================
# SETTINGS PANEL
# ============================================================

def render_settings():
    st.markdown(
        '<div class="card-title">Voice Settings</div>',
        unsafe_allow_html=True,
    )

    provider = st.selectbox(
        "Provider",
        [
            "Google Gemini TTS",
            "Browser TTS — Free fallback",
        ],
        index=0,
    )

    model = st.selectbox(
        "AI Model",
        [
            DEFAULT_MODEL,
            ALTERNATIVE_MODEL,
        ],
        index=0,
        help=(
            "The default uses the currently documented Gemini 3.1 "
            "Flash TTS preview model."
        ),
    )

    voice_label = st.selectbox(
        "Voice",
        list(VOICE_OPTIONS.keys()),
        index=0,
    )

    voice_data = VOICE_OPTIONS[voice_label]

    st.caption(
        f"{voice_data['name']} — {voice_data['description']}"
    )

    speaking_style = st.selectbox(
        "Speaking Style",
        list(STYLE_INSTRUCTIONS.keys()),
        index=0,
    )

    custom_style = st.text_area(
        "Custom Style",
        placeholder=(
            "Example: Speak naturally, confidently and professionally. "
            "Use moderate pacing and clear pronunciation."
        ),
        height=90,
    )

    speed = st.slider(
        "Speed",
        min_value=0.7,
        max_value=1.3,
        value=1.0,
        step=0.05,
        help=(
            "Speed is represented in the Gemini prompt and then "
            "applied locally to the generated PCM audio."
        ),
    )

    consistency = st.slider(
        "Voice Consistency",
        min_value=0.0,
        max_value=1.0,
        value=0.65,
        step=0.05,
        help=(
            "Application-level style control. This is not an "
            "ElevenLabs stability parameter."
        ),
    )

    character = st.slider(
        "Voice Character",
        min_value=0.0,
        max_value=1.0,
        value=0.50,
        step=0.05,
        help=(
            "Application-level prompt control. It does not clone "
            "or match another person's voice."
        ),
    )

    style_intensity = st.slider(
        "Style Intensity",
        min_value=0.0,
        max_value=1.0,
        value=0.50,
        step=0.05,
        help="Controls how strongly the selected style is expressed.",
    )

    st.markdown(
        """
        <div class="warning-box">
            <strong>Important:</strong><br>
            Voice Consistency, Voice Character and Style Intensity
            are application-level controls. They are not ElevenLabs
            parameters and do not perform voice cloning.
        </div>
        """,
        unsafe_allow_html=True,
    )

    return {
        "provider": provider,
        "model": model,
        "voice_label": voice_label,
        "voice_name": voice_data["name"],
        "speaking_style": speaking_style,
        "custom_style": custom_style,
        "speed": speed,
        "consistency": consistency,
        "character": character,
        "style_intensity": style_intensity,
    }


# ============================================================
# HISTORY PAGE
# ============================================================

def render_history():
    st.markdown(
        '<div class="app-header">'
        '<div class="app-title">Generation History</div>'
        '<div class="app-subtitle">'
        "Recent speech generations from this browser session."
        "</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    if st.button(
        "🗑️ Clear History",
        on_click=clear_history,
    ):
        st.rerun()

    if not st.session_state.history:
        st.info(
            "No generation history yet. Generate some speech "
            "from Voice Studio."
        )
        return

    for item in st.session_state.history:

        st.markdown(
            f"""
            <div class="history-item">
                <div class="history-time">
                    {html.escape(item["time"])}
                </div>

                <div class="history-text">
                    {html.escape(item["text"])}
                </div>

                <div style="color:#64748b;font-size:0.72rem;margin-top:6px;">
                    Voice: {html.escape(item["voice"])}
                    &nbsp;•&nbsp;
                    Model: {html.escape(item["model"])}
                    &nbsp;•&nbsp;
                    Style: {html.escape(item["style"])}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# ABOUT PAGE
# ============================================================

def render_about():
    st.markdown(
        '<div class="app-header">'
        '<div class="app-title">About AI Voice Studio</div>'
        '<div class="app-subtitle">'
        "A Streamlit-based AI text-to-speech workspace."
        "</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="studio-card">

        <div class="card-title">What is this?</div>

        <div class="card-description">

        AI Voice Studio converts written text into speech using
        Google's Gemini TTS API.

        The application is intentionally designed without ElevenLabs
        APIs, proprietary code, voice cloning or proprietary assets.

        </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="studio-card">

        <div class="card-title">Technology</div>

        <div class="card-description">

        • Python<br>
        • Streamlit<br>
        • Google GenAI Python SDK<br>
        • Gemini TTS<br>
        • Browser SpeechSynthesis fallback<br>
        • Session-based history<br>
        • WAV audio processing

        </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="studio-card">

        <div class="card-title">Privacy and security</div>

        <div class="card-description">

        The Gemini API key is loaded from Streamlit Secrets.
        It is never displayed in the interface and is not stored
        in session history.

        Do not commit your API key to GitHub.

        </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# MAIN VOICE STUDIO
# ============================================================

def render_voice_studio():

    st.markdown(
        """
        <div class="app-header">
            <div class="app-title">AI Voice Studio</div>
            <div class="app-subtitle">
                Turn your text into natural-sounding speech.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # Three-column desktop layout
    # --------------------------------------------------------

    left_col, main_col, right_col = st.columns(
        [1.15, 3.2, 1.55],
        gap="large",
    )

    # --------------------------------------------------------
    # LEFT
    # --------------------------------------------------------

    with left_col:

        st.markdown(
            """
            <div class="studio-card">
                <div class="card-title">Workspace</div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("🎙️ **Voice Studio**")
        st.caption("Create AI speech from text.")

        st.markdown("")

        st.markdown("🕘 **History**")
        st.caption("View this session's generations.")

        st.markdown("")

        st.markdown("⚙️ **Settings**")
        st.caption("API and application settings.")

        st.markdown("")

        st.markdown("ℹ️ **About**")
        st.caption("Learn about this application.")

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(
            """
            <div class="studio-card">
                <div class="card-title">Quick tips</div>
                <div class="card-description">
                    Use short paragraphs for quick testing.
                    Choose a style and voice that match the content.
                    For a free browser-only option, use Browser TTS.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # --------------------------------------------------------
    # MAIN TEXT AREA
    # --------------------------------------------------------

    with main_col:

        st.markdown(
            """
            <div class="studio-card">
                <div class="card-title">Your Script</div>
            """,
            unsafe_allow_html=True,
        )

        text = st.text_area(
            "Text",
            value=st.session_state.text_input,
            key="text_input",
            height=360,
            placeholder="Type or paste your text here...",
            label_visibility="collapsed",
            max_chars=MAX_CHARACTERS,
        )

        character_count = len(text)
        word_count = count_words(text)

        st.markdown(
            f"""
            <div class="counter-row">
                <div class="counter">
                    Characters: <strong>{character_count:,}</strong>
                </div>

                <div class="counter">
                    Words: <strong>{word_count:,}</strong>
                </div>

                <div class="counter">
                    Limit: <strong>{MAX_CHARACTERS:,}</strong>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        clear_col, generate_col = st.columns(
            [1, 2.8],
            gap="small",
        )

        with clear_col:
            st.button(
                "Clear",
                on_click=clear_text,
                use_container_width=True,
            )

        # ----------------------------------------------------
        # SETTINGS ARE COLLECTED FROM RIGHT COLUMN BELOW
        # ----------------------------------------------------

        st.markdown("</div>", unsafe_allow_html=True)

    # --------------------------------------------------------
    # RIGHT SETTINGS
    # --------------------------------------------------------

    with right_col:

        st.markdown(
            """
            <div class="studio-card">
            """,
            unsafe_allow_html=True,
        )

        settings = render_settings()

        st.markdown("</div>", unsafe_allow_html=True)

    # --------------------------------------------------------
    # GENERATION BUTTON
    # --------------------------------------------------------

    with main_col:

        st.markdown(
            '<div class="generate-button">',
            unsafe_allow_html=True,
        )

        generate_clicked = st.button(
            "✨ Generate Speech",
            use_container_width=True,
            type="primary",
        )

        st.markdown("</div>", unsafe_allow_html=True)

        if generate_clicked:

            clean_text = text.strip()

            if not clean_text:
                st.error(
                    "Please enter some text before generating speech."
                )
                return

            if len(clean_text) > MAX_CHARACTERS:
                st.error(
                    f"Your text is too long. Please keep it under "
                    f"{MAX_CHARACTERS:,} characters."
                )
                return

            provider = settings["provider"]

            if provider == "Browser TTS — Free fallback":

                st.info(
                    "Browser TTS runs directly in your browser and "
                    "does not use the Gemini API."
                )

                render_browser_tts(clean_text)
                return

            if not get_api_key():
                st.error(
                    "GEMINI_API_KEY is missing. Add it to Streamlit "
                    "Community Cloud → App Settings → Secrets."
                )

                st.info(
                    "You can still use Browser TTS — Free fallback "
                    "without an API key."
                )

                render_browser_tts(clean_text)
                return

            # ------------------------------------------------
            # GENERATE
            # ------------------------------------------------

            try:

                with st.status(
                    "Generating speech...",
                    expanded=True,
                ) as status:

                    st.write("Preparing the speaking instructions...")

                    st.write(
                        f"Voice: {settings['voice_name']}"
                    )

                    st.write(
                        f"Model: {settings['model']}"
                    )

                    st.write("Calling Gemini TTS...")

                    wav_bytes = generate_speech(
                        text=clean_text,
                        model=settings["model"],
                        voice_name=settings["voice_name"],
                        speaking_style=settings["speaking_style"],
                        custom_style=settings["custom_style"],
                        speed=settings["speed"],
                        consistency=settings["consistency"],
                        character=settings["character"],
                        style_intensity=settings["style_intensity"],
                    )

                    st.write("Processing audio...")

                    filename = (
                        "ai_voice_"
                        + datetime.now().strftime("%Y%m%d_%H%M%S")
                        + ".wav"
                    )

                    st.session_state.generated_audio = wav_bytes
                    st.session_state.generated_filename = filename

                    st.session_state.generation_info = {
                        "voice": settings["voice_name"],
                        "model": settings["model"],
                        "style": settings["speaking_style"],
                    }

                    add_history(
                        text=clean_text,
                        voice=settings["voice_name"],
                        model=settings["model"],
                        style=settings["speaking_style"],
                    )

                    status.update(
                        label="Speech generated successfully.",
                        state="complete",
                    )

            except Exception as exc:

                error_text = str(exc).lower()

                if (
                    "api key" in error_text
                    or "authentication" in error_text
                    or "unauthorized" in error_text
                    or "permission" in error_text
                ):
                    st.error(
                        "Gemini authentication failed. Check your "
                        "GEMINI_API_KEY in Streamlit Secrets."
                    )

                elif (
                    "quota" in error_text
                    or "rate" in error_text
                    or "resource exhausted" in error_text
                ):
                    st.error(
                        "The Gemini API quota or rate limit was reached. "
                        "Please wait and try again later."
                    )

                elif (
                    "not found" in error_text
                    or "model" in error_text
                ):
                    st.error(
                        "The selected Gemini TTS model may be unavailable "
                        "or may have changed. Try the other model."
                    )

                elif (
                    "network" in error_text
                    or "connection" in error_text
                    or "timeout" in error_text
                ):
                    st.error(
                        "The Gemini service could not be reached. "
                        "Please check the connection and try again."
                    )

                else:
                    st.error(
                        "Speech generation failed. "
                        "Please verify your Gemini API key, selected "
                        "model and text, then try again."
                    )

                st.info(
                    "Browser TTS is available as a free fallback below."
                )

                render_browser_tts(clean_text)

        # ----------------------------------------------------
        # AUDIO OUTPUT
        # ----------------------------------------------------

        if st.session_state.generated_audio:

            st.markdown(
                """
                <div class="studio-card">
                    <div class="card-title">🎧 Audio Output</div>
                """,
                unsafe_allow_html=True,
            )

            if st.session_state.generation_info:

                info = st.session_state.generation_info

                st.markdown(
                    f"""
                    <div class="success-box">
                        Speech generated successfully.<br>
                        Voice: {html.escape(info["voice"])}<br>
                        Model: {html.escape(info["model"])}<br>
                        Style: {html.escape(info["style"])}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                st.markdown("")

            st.audio(
                st.session_state.generated_audio,
                format="audio/wav",
            )

            st.download_button(
                label="⬇️ Download WAV",
                data=st.session_state.generated_audio,
                file_name=st.session_state.generated_filename,
                mime="audio/wav",
                use_container_width=True,
            )

            st.markdown(
                """
                <div class="card-description" style="margin-top:10px;">
                    WAV is provided because it requires no FFmpeg
                    dependency and is directly generated from the
                    Gemini PCM response.
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# SETTINGS PAGE
# ============================================================

def render_settings_page():

    st.markdown(
        """
        <div class="app-header">
            <div class="app-title">Application Settings</div>
            <div class="app-subtitle">
                Configuration and security information.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    api_key_exists = bool(get_api_key())

    if api_key_exists:
        st.success(
            "GEMINI_API_KEY is configured."
        )
    else:
        st.warning(
            "GEMINI_API_KEY is not configured."
        )

    st.markdown(
        """
        ### API configuration

        The application reads:

        `GEMINI_API_KEY`

        from Streamlit Secrets.

        The API key is intentionally not shown in this interface.

        ### Security

        Never put your Gemini API key inside:

        - `app.py`
        - `README.md`
        - GitHub commits
        - screenshots
        - session history

        ### Recommended Streamlit Secret

        ```toml
        GEMINI_API_KEY = "YOUR_API_KEY"
        ```
        """
    )


# ============================================================
# APPLICATION ENTRY POINT
# ============================================================

page = render_sidebar()

if page == "🎙️ Voice Studio":
    render_voice_studio()

elif page == "🕘 History":
    render_history()

elif page == "⚙️ Settings":
    render_settings_page()

elif page == "ℹ️ About":
    render_about()


st.markdown(
    """
    <div class="footer">
        AI Voice Studio • Streamlit • Google Gemini TTS
    </div>
    """,
    unsafe_allow_html=True,
)
