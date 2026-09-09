import io
import os
import wave
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
# CONFIGURATION
# ============================================================

DEFAULT_MODEL = "gemini-2.5-flash-preview-tts"

MAX_CHARACTERS = 12000

VOICE_OPTIONS = {
    "Kore — Clear & professional": "Kore",
    "Puck — Friendly & energetic": "Puck",
    "Charon — Deep & authoritative": "Charon",
    "Fenrir — Strong & expressive": "Fenrir",
    "Aoede — Warm & conversational": "Aoede",
    "Leda — Smooth & balanced": "Leda",
    "Orus — Strong & clear": "Orus",
    "Zephyr — Natural & versatile": "Zephyr",
}

STYLE_OPTIONS = [
    "Natural",
    "Professional",
    "Friendly",
    "Energetic",
    "Calm",
    "Narration",
    "News",
    "Storytelling",
    "Podcast",
    "Deep & Dramatic",
]


# ============================================================
# CUSTOM CSS
# IMPORTANT:
# We use CSS only.
# NO custom HTML UI blocks.
# ============================================================

st.markdown(
    """
<style>

/* =========================================================
   GLOBAL
   ========================================================= */

.stApp {
    background: #07111f;
    color: #e5edf7;
}

[data-testid="stHeader"] {
    background: transparent;
}

[data-testid="stToolbar"] {
    background: transparent;
}

.main .block-container {
    max-width: 1450px;
    padding-top: 2.2rem;
    padding-bottom: 4rem;
}


/* =========================================================
   SIDEBAR
   ========================================================= */

section[data-testid="stSidebar"] {
    background: #091524;
    border-right: 1px solid #1b2a3d;
}

section[data-testid="stSidebar"] > div {
    background: #091524;
}

section[data-testid="stSidebar"] .block-container {
    padding-top: 1.5rem;
}


/* Sidebar text */

section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] label {
    color: #cbd5e1;
}


/* Sidebar buttons */

section[data-testid="stSidebar"] .stButton > button {
    width: 100%;
    min-height: 45px;
    background: transparent;
    border: 1px solid transparent;
    border-radius: 10px;
    color: #cbd5e1;
    text-align: left;
    font-size: 0.92rem;
    font-weight: 600;
}

section[data-testid="stSidebar"] .stButton > button:hover {
    background: #102238;
    border-color: #1d3856;
    color: #ffffff;
}


/* =========================================================
   TITLES
   ========================================================= */

h1,
h2,
h3 {
    color: #f8fafc !important;
}

.page-title {
    font-size: 2.5rem;
    font-weight: 800;
    color: #f8fafc;
    letter-spacing: -1px;
}

.page-subtitle {
    color: #94a3b8;
    font-size: 1rem;
    margin-bottom: 1.8rem;
}


/* =========================================================
   CARDS
   ========================================================= */

[data-testid="stVerticalBlockBorderWrapper"] {
    background: #0d1a2b;
    border: 1px solid #20324a;
    border-radius: 16px;
}


/* =========================================================
   TEXT AREA
   ========================================================= */

textarea {
    background-color: #0a1626 !important;
    color: #f1f5f9 !important;
    border: 1px solid #2b405b !important;
    border-radius: 12px !important;
    font-size: 1rem !important;
    line-height: 1.7 !important;
}

textarea::placeholder {
    color: #64748b !important;
    opacity: 1 !important;
}

textarea:focus {
    border-color: #3b82f6 !important;
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2) !important;
}


/* =========================================================
   SELECTBOX
   ========================================================= */

div[data-baseweb="select"] > div {
    background: #0b1829 !important;
    border: 1px solid #2b405b !important;
    border-radius: 10px !important;
    color: #f8fafc !important;
}

div[data-baseweb="select"] span {
    color: #e5edf7 !important;
}

div[data-baseweb="select"] svg {
    fill: #94a3b8 !important;
}


/* =========================================================
   LABELS
   ========================================================= */

label {
    color: #cbd5e1 !important;
    font-weight: 600 !important;
}


/* =========================================================
   SLIDERS
   ========================================================= */

div[data-testid="stSlider"] label {
    color: #cbd5e1 !important;
}

div[data-testid="stSlider"] [role="slider"] {
    background: #3b82f6 !important;
}


/* =========================================================
   BUTTONS
   ========================================================= */

.stButton > button {
    border-radius: 10px;
    min-height: 44px;
    background: #14243a;
    color: #e2e8f0;
    border: 1px solid #2a405b;
    font-weight: 650;
}

.stButton > button:hover {
    background: #1a304d;
    border-color: #3b82f6;
    color: #ffffff;
}


/* Generate button */

.generate-button .stButton > button {
    background: #2563eb !important;
    color: white !important;
    border: none !important;
    min-height: 52px;
    font-size: 1rem;
    font-weight: 750;
    border-radius: 11px;
    box-shadow: 0 8px 25px rgba(37, 99, 235, 0.25);
}

.generate-button .stButton > button:hover {
    background: #1d4ed8 !important;
}


/* =========================================================
   METRICS
   ========================================================= */

[data-testid="stMetric"] {
    background: #0a1727;
    border: 1px solid #20344d;
    border-radius: 10px;
    padding: 0.7rem;
}

[data-testid="stMetricLabel"] {
    color: #94a3b8 !important;
}

[data-testid="stMetricValue"] {
    color: #f8fafc !important;
}


/* =========================================================
   INFO / SUCCESS / WARNING
   ========================================================= */

div[data-testid="stAlert"] {
    border-radius: 10px;
}


/* =========================================================
   AUDIO
   ========================================================= */

audio {
    width: 100%;
}


/* =========================================================
   DIVIDERS
   ========================================================= */

hr {
    border-color: #1c2c40 !important;
}


/* =========================================================
   SIDEBAR BRAND
   ========================================================= */

.sidebar-brand {
    text-align: center;
    padding: 0.5rem 0 1.5rem 0;
}

.sidebar-mic {
    font-size: 3rem;
    line-height: 1;
}

.sidebar-brand-title {
    color: #f8fafc;
    font-size: 1.25rem;
    font-weight: 800;
    margin-top: 0.7rem;
}

.sidebar-brand-subtitle {
    color: #718198;
    font-size: 0.75rem;
    margin-top: 0.3rem;
}


/* =========================================================
   SECTION TITLES
   ========================================================= */

.section-title {
    color: #f8fafc;
    font-size: 1.05rem;
    font-weight: 750;
    margin-bottom: 0.4rem;
}

.section-caption {
    color: #64748b;
    font-size: 0.78rem;
    margin-bottom: 1rem;
}

.small-heading {
    color: #64748b;
    font-size: 0.7rem;
    font-weight: 800;
    letter-spacing: 1px;
    text-transform: uppercase;
}


/* =========================================================
   FOOTER
   ========================================================= */

.footer {
    text-align: center;
    color: #52657c;
    font-size: 0.72rem;
    padding-top: 2rem;
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

if "script" not in st.session_state:
    st.session_state.script = ""

if "audio_data" not in st.session_state:
    st.session_state.audio_data = None

if "history" not in st.session_state:
    st.session_state.history = []

if "provider" not in st.session_state:
    st.session_state.provider = "Google Gemini TTS"


# ============================================================
# FUNCTIONS
# ============================================================

def get_api_key():
    """
    Read Gemini API key only from Streamlit secrets
    or environment variables.

    The key is never stored in session_state.
    """

    try:
        key = st.secrets.get("GEMINI_API_KEY")

        if key:
            return key

    except Exception:
        pass

    key = os.environ.get("GEMINI_API_KEY")

    if key:
        return key

    return None


def pcm_to_wav(
    pcm_bytes,
    sample_rate=24000,
    channels=1,
    sample_width=2,
):
    """
    Convert raw PCM audio into a valid WAV file.
    """

    output = io.BytesIO()

    with wave.open(output, "wb") as wav_file:
        wav_file.setnchannels(channels)
        wav_file.setsampwidth(sample_width)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(pcm_bytes)

    return output.getvalue()


def build_tts_prompt(
    text,
    style,
    speed,
    consistency,
    character,
    intensity,
):
    """
    Build a natural-language Gemini TTS instruction.

    Gemini does not expose ElevenLabs-style
    stability/similarity controls, so those controls
    are translated into prompt instructions.
    """

    speed_instruction = "normal speaking pace"

    if speed < 0.9:
        speed_instruction = "slightly slow and deliberate speaking pace"

    elif speed > 1.1:
        speed_instruction = "slightly fast and energetic speaking pace"

    if consistency < 0.35:
        consistency_instruction = (
            "Use expressive vocal variation and natural changes "
            "in delivery."
        )

    elif consistency > 0.7:
        consistency_instruction = (
            "Keep the vocal delivery consistent, controlled, "
            "and steady."
        )

    else:
        consistency_instruction = (
            "Use balanced and natural vocal variation."
        )

    if character < 0.35:
        character_instruction = (
            "Keep the vocal character neutral and natural."
        )

    elif character > 0.7:
        character_instruction = (
            "Give the delivery a distinctive and expressive "
            "vocal character."
        )

    else:
        character_instruction = (
            "Use a moderately expressive vocal character."
        )

    if intensity < 0.35:
        intensity_instruction = (
            "Keep stylistic expression subtle."
        )

    elif intensity > 0.7:
        intensity_instruction = (
            "Use strong expressive delivery."
        )

    else:
        intensity_instruction = (
            "Use noticeable but controlled emotional expression."
        )

    prompt = f"""
Speak the following text naturally.

Speaking style:
{style}

Pacing:
{speed_instruction}

Voice consistency:
{consistency_instruction}

Voice character:
{character_instruction}

Style intensity:
{intensity_instruction}

Additional instructions:
- Use clear pronunciation.
- Sound natural and human-like.
- Use appropriate pauses.
- Follow punctuation naturally.
- Do not add words.
- Do not explain the text.
- Only speak the supplied script.

SCRIPT:

{text}
"""

    return prompt


def generate_speech(
    text,
    model,
    voice,
    style,
    speed,
    consistency,
    character,
    intensity,
):
    """
    Generate speech through Google's official
    Gemini Python SDK.
    """

    api_key = get_api_key()

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured. "
            "Add it under Streamlit Cloud → Settings → Secrets."
        )

    client = genai.Client(api_key=api_key)

    prompt = build_tts_prompt(
        text=text,
        style=style,
        speed=speed,
        consistency=consistency,
        character=character,
        intensity=intensity,
    )

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
            "Gemini returned an empty response."
        )

    for candidate in response.candidates:

        if not candidate.content:
            continue

        if not candidate.content.parts:
            continue

        for part in candidate.content.parts:

            inline_data = getattr(
                part,
                "inline_data",
                None,
            )

            if inline_data is None:
                continue

            audio_bytes = inline_data.data

            if isinstance(audio_bytes, str):
                import base64

                audio_bytes = base64.b64decode(
                    audio_bytes
                )

            return pcm_to_wav(
                audio_bytes
            )

    raise RuntimeError(
        "Gemini did not return audio data."
    )


def count_words(text):
    if not text.strip():
        return 0

    return len(text.split())


def render_sidebar():

    with st.sidebar:

        st.markdown(
            """
            <div class="sidebar-brand">
                <div class="sidebar-mic">🎙️</div>
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

        st.divider()

        st.caption("WORKSPACE")

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

        st.divider()

        with st.container(border=True):

            st.markdown(
                "**✨ Gemini TTS**"
            )

            st.caption(
                "Generate natural-sounding speech "
                "from your scripts using Google's "
                "Gemini text-to-speech models."
            )

        st.markdown("")

        st.caption(
            "No database • Session-based history"
        )

        st.caption(
            "Built with Streamlit + Gemini"
        )


def render_settings():

    st.subheader("Voice Settings")

    st.caption(
        "Configure the AI voice and delivery."
    )

    provider = st.selectbox(
        "Provider",
        [
            "Google Gemini TTS",
            "Browser TTS",
        ],
        index=0,
        key="provider_select",
    )

    st.session_state.provider = provider

    st.markdown(
        '<div class="small-heading">AI ENGINE</div>',
        unsafe_allow_html=True,
    )

    model = st.selectbox(
        "AI Model",
        [
            "Gemini 2.5 Flash TTS"
        ],
        key="model_select",
    )

    model_id = DEFAULT_MODEL

    st.markdown(
        '<div class="small-heading">VOICE</div>',
        unsafe_allow_html=True,
    )

    voice_label = st.selectbox(
        "Voice",
        list(VOICE_OPTIONS.keys()),
        key="voice_select",
    )

    voice_id = VOICE_OPTIONS[voice_label]

    st.caption(
        voice_label.split(" — ", 1)[-1]
    )

    st.markdown(
        '<div class="small-heading">SPEAKING STYLE</div>',
        unsafe_allow_html=True,
    )

    style = st.selectbox(
        "Speaking Style",
        STYLE_OPTIONS,
        key="style_select",
    )

    custom_style = st.text_area(
        "Custom Style",
        placeholder=(
            "Example: Speak naturally, confidently "
            "and professionally. Use moderate pacing "
            "and clear pronunciation."
        ),
        height=90,
        key="custom_style",
    )

    if custom_style.strip():
        final_style = custom_style.strip()
    else:
        final_style = style

    st.markdown(
        '<div class="small-heading">VOICE CONTROL</div>',
        unsafe_allow_html=True,
    )

    speed = st.slider(
        "Speed",
        min_value=0.7,
        max_value=1.3,
        value=1.0,
        step=0.05,
        key="speed",
    )

    consistency = st.slider(
        "Voice Consistency",
        min_value=0.0,
        max_value=1.0,
        value=0.6,
        step=0.05,
        help=(
            "Application-level prompt control. "
            "It is not an ElevenLabs stability parameter."
        ),
        key="consistency",
    )

    character = st.slider(
        "Voice Character",
        min_value=0.0,
        max_value=1.0,
        value=0.5,
        step=0.05,
        help=(
            "Controls prompt instructions for vocal character. "
            "It does not clone or match a person's voice."
        ),
        key="character",
    )

    intensity = st.slider(
        "Style Intensity",
        min_value=0.0,
        max_value=1.0,
        value=0.5,
        step=0.05,
        key="intensity",
    )

    return {
        "provider": provider,
        "model": model_id,
        "voice": voice_id,
        "style": final_style,
        "speed": speed,
        "consistency": consistency,
        "character": character,
        "intensity": intensity,
    }


def render_voice_studio():

    # --------------------------------------------------------
    # PAGE HEADER
    # --------------------------------------------------------

    st.markdown(
        '<div class="page-title">AI Voice Studio</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="page-subtitle">'
        "Turn your text into natural-sounding speech."
        "</div>",
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # MAIN COLUMNS
    # --------------------------------------------------------

    main_column, settings_column = st.columns(
        [2.1, 1],
        gap="large",
    )

    # ========================================================
    # MAIN COLUMN
    # ========================================================

    with main_column:

        with st.container(border=True):

            st.markdown(
                '<div class="section-title">Your Script</div>',
                unsafe_allow_html=True,
            )

            st.caption(
                "Write or paste your narration below."
            )

            script = st.text_area(
                "Script",
                value=st.session_state.script,
                placeholder=(
                    "Type or paste your text here..."
                ),
                height=360,
                label_visibility="collapsed",
                max_chars=MAX_CHARACTERS,
                key="script_editor",
            )

            st.session_state.script = script

            characters = len(script)
            words = count_words(script)

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "Characters",
                    f"{characters:,}",
                )

            with col2:
                st.metric(
                    "Words",
                    f"{words:,}",
                )

            with col3:

                minutes = (
                    words / 150
                    if words
                    else 0
                )

                st.metric(
                    "Estimated",
                    f"{minutes:.1f} min",
                )

            st.caption(
                f"{characters:,} / "
                f"{MAX_CHARACTERS:,} characters"
            )

        st.write("")

        # ----------------------------------------------------
        # BUTTONS
        # ----------------------------------------------------

        button1, button2 = st.columns(
            [3, 1]
        )

        with button1:

            st.markdown(
                '<div class="generate-button">',
                unsafe_allow_html=True,
            )

            generate = st.button(
                "✨  Generate Speech",
                use_container_width=True,
            )

            st.markdown(
                "</div>",
                unsafe_allow_html=True,
            )

        with button2:

            clear = st.button(
                "🗑️ Clear",
                use_container_width=True,
            )

        if clear:

            st.session_state.script = ""
            st.session_state.audio_data = None

            st.rerun()

        # ----------------------------------------------------
        # GENERATION
        # ----------------------------------------------------

        if generate:

            if not script.strip():

                st.warning(
                    "Please enter some text first."
                )

            elif len(script) > MAX_CHARACTERS:

                st.error(
                    f"Your text is too long. "
                    f"Maximum allowed is "
                    f"{MAX_CHARACTERS:,} characters."
                )

            elif st.session_state.provider == "Browser TTS":

                st.info(
                    "Browser TTS fallback is selected. "
                    "Use the browser's built-in speech option "
                    "on a supported browser."
                )

                # Browser fallback using Streamlit
                # JavaScript component.
                st.components.v1.html(
                    f"""
                    <div style="
                        background:#0d1a2b;
                        padding:18px;
                        border-radius:12px;
                        border:1px solid #20324a;
                        color:#e5edf7;
                        font-family:Arial,sans-serif;
                    ">

                    <button
                        onclick="speakText()"
                        style="
                            background:#2563eb;
                            color:white;
                            border:none;
                            padding:12px 18px;
                            border-radius:8px;
                            cursor:pointer;
                            font-weight:bold;
                        "
                    >
                    🔊 Speak in Browser
                    </button>

                    <script>

                    function speakText() {{

                        const text = {repr(script)};

                        if (!window.speechSynthesis) {{
                            alert(
                                "Browser speech synthesis is not supported."
                            );
                            return;
                        }}

                        window.speechSynthesis.cancel();

                        const utterance =
                            new SpeechSynthesisUtterance(text);

                        utterance.rate = {speed};

                        window.speechSynthesis.speak(
                            utterance
                        );
                    }}

                    </script>

                    </div>
                    """,
                    height=80,
                )

            else:

                api_key = get_api_key()

                if not api_key:

                    st.error(
                        "GEMINI_API_KEY is missing. "
                        "Open Streamlit Cloud → Settings → Secrets "
                        "and add your Gemini API key."
                    )

                else:

                    settings = {
                        "model": st.session_state.get(
                            "model_select",
                            DEFAULT_MODEL,
                        ),
                        "voice": VOICE_OPTIONS.get(
                            st.session_state.get(
                                "voice_select",
                                list(VOICE_OPTIONS.keys())[0],
                            ),
                            "Kore",
                        ),
                        "style": st.session_state.get(
                            "custom_style"
                        )
                        or st.session_state.get(
                            "style_select",
                            "Natural",
                        ),
                        "speed": st.session_state.get(
                            "speed",
                            1.0,
                        ),
                        "consistency": st.session_state.get(
                            "consistency",
                            0.6,
                        ),
                        "character": st.session_state.get(
                            "character",
                            0.5,
                        ),
                        "intensity": st.session_state.get(
                            "intensity",
                            0.5,
                        ),
                    }

                    try:

                        with st.status(
                            "Generating speech...",
                            expanded=True,
                        ) as status:

                            st.write(
                                "Connecting to Gemini TTS..."
                            )

                            audio = generate_speech(
                                text=script,
                                model=settings["model"],
                                voice=settings["voice"],
                                style=settings["style"],
                                speed=settings["speed"],
                                consistency=settings[
                                    "consistency"
                                ],
                                character=settings[
                                    "character"
                                ],
                                intensity=settings[
                                    "intensity"
                                ],
                            )

                            st.write(
                                "Processing audio..."
                            )

                            st.session_state.audio_data = (
                                audio
                            )

                            # Session history
                            st.session_state.history.insert(
                                0,
                                {
                                    "date": datetime.now().strftime(
                                        "%Y-%m-%d %H:%M"
                                    ),
                                    "voice": settings[
                                        "voice"
                                    ],
                                    "model": settings[
                                        "model"
                                    ],
                                    "text": script[:180],
                                    "style": settings[
                                        "style"
                                    ],
                                },
                            )

                            status.update(
                                label=(
                                    "Speech generated successfully."
                                ),
                                state="complete",
                            )

                    except Exception as error:

                        error_text = str(error)

                        if (
                            "API key" in error_text
                            or "401" in error_text
                            or "403" in error_text
                        ):

                            st.error(
                                "Gemini authentication failed. "
                                "Please check your GEMINI_API_KEY."
                            )

                        elif (
                            "404" in error_text
                            or "not found" in error_text.lower()
                        ):

                            st.error(
                                "The selected Gemini TTS model "
                                "may no longer be available. "
                                "Try updating DEFAULT_MODEL in app.py."
                            )

                        elif (
                            "quota" in error_text.lower()
                            or "429" in error_text
                        ):

                            st.error(
                                "Gemini API quota or rate limit "
                                "was reached. Please try again later."
                            )

                        else:

                            st.error(
                                "Speech generation failed. "
                                "Please check your Gemini API configuration "
                                "and try again."
                            )

        # ----------------------------------------------------
        # AUDIO OUTPUT
        # ----------------------------------------------------

        if st.session_state.audio_data:

            st.write("")

            with st.container(border=True):

                st.markdown(
                    '<div class="section-title">'
                    "🎧 Audio Output"
                    "</div>",
                    unsafe_allow_html=True,
                )

                st.caption(
                    "Your generated speech is ready."
                )

                st.audio(
                    st.session_state.audio_data,
                    format="audio/wav",
                )

                st.download_button(
                    "⬇️ Download WAV",
                    data=st.session_state.audio_data,
                    file_name="ai_voice_studio.wav",
                    mime="audio/wav",
                    use_container_width=True,
                )

    # ========================================================
    # SETTINGS COLUMN
    # ========================================================

    with settings_column:

        with st.container(border=True):

            settings = render_settings()


def render_history():

    st.markdown(
        '<div class="page-title">History</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="page-subtitle">'
        "Your recent voice generations."
        "</div>",
        unsafe_allow_html=True,
    )

    if not st.session_state.history:

        with st.container(border=True):

            st.info(
                "No generations yet. "
                "Generate your first voice from Voice Studio."
            )

        return

    if st.button(
        "🗑️ Clear History",
        use_container_width=False,
    ):

        st.session_state.history = []

        st.rerun()

    st.write("")

    for index, item in enumerate(
        st.session_state.history
    ):

        with st.container(border=True):

            st.markdown(
                f"**{item['date']}**"
            )

            st.write(
                item["text"]
            )

            st.caption(
                f"Voice: {item['voice']}  •  "
                f"Model: {item['model']}  •  "
                f"Style: {item['style']}"
            )


def render_settings_page():

    st.markdown(
        '<div class="page-title">Settings</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="page-subtitle">'
        "Application configuration."
        "</div>",
        unsafe_allow_html=True,
    )

    with st.container(border=True):

        st.subheader(
            "Gemini API Configuration"
        )

        if get_api_key():

            st.success(
                "Gemini API key detected."
            )

        else:

            st.warning(
                "GEMINI_API_KEY is not configured."
            )

        st.info(
            "For Streamlit Community Cloud, add "
            "GEMINI_API_KEY under your app's Secrets."
        )


def render_about():

    st.markdown(
        '<div class="page-title">About</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="page-subtitle">'
        "AI-powered text-to-speech studio."
        "</div>",
        unsafe_allow_html=True,
    )

    with st.container(border=True):

        st.subheader(
            "🎙️ AI Voice Studio"
        )

        st.write(
            "AI Voice Studio converts written scripts "
            "into natural-sounding speech using Google "
            "Gemini TTS."
        )

        st.write(
            "The application is designed for "
            "Streamlit Community Cloud and uses "
            "session-based history without a database."
        )

        st.caption(
            "Gemini TTS • Streamlit • Python"
        )


# ============================================================
# RENDER SIDEBAR
# ============================================================

render_sidebar()


# ============================================================
# PAGE ROUTING
# ============================================================

if st.session_state.page == "Voice Studio":

    render_voice_studio()

elif st.session_state.page == "History":

    render_history()

elif st.session_state.page == "Settings":

    render_settings_page()

elif st.session_state.page == "About":

    render_about()


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "AI Voice Studio • Built with Streamlit + Gemini"
)
