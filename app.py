import os
import io
import base64
import wave
from datetime import datetime

import streamlit as st

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

MODELS = {
    "Gemini 2.5 Flash TTS": "gemini-2.5-flash-preview-tts",
    "Gemini 3.1 Flash TTS": "gemini-3.1-flash-tts-preview",
}

VOICES = {
    "Kore": "Clear & professional",
    "Puck": "Friendly & energetic",
    "Charon": "Deep & authoritative",
    "Fenrir": "Strong & expressive",
    "Aoede": "Warm & conversational",
    "Leda": "Smooth & balanced",
    "Orus": "Strong & clear",
    "Zephyr": "Natural & versatile",
}

STYLES = [
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
# SESSION STATE
# ============================================================

if "history" not in st.session_state:
    st.session_state.history = []

if "generated_audio" not in st.session_state:
    st.session_state.generated_audio = None

if "generated_text" not in st.session_state:
    st.session_state.generated_text = ""

if "generation_count" not in st.session_state:
    st.session_state.generation_count = 0


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
<style>

    /* Main background */
    .stApp {
        background: #0b1220;
    }

    /* Main content */
    .main .block-container {
        max-width: 1250px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: #101827;
        border-right: 1px solid #243044;
    }

    section[data-testid="stSidebar"] * {
        color: #e7edf7;
    }

    /* Headings */
    h1, h2, h3 {
        color: #f5f7fb !important;
    }

    p, label, .stMarkdown {
        color: #c8d2e3;
    }

    /* Text area */
    textarea {
        background-color: #111b2d !important;
        color: #f4f7fb !important;
        border: 1px solid #33425c !important;
        border-radius: 12px !important;
        font-size: 16px !important;
        line-height: 1.6 !important;
    }

    textarea:focus {
        border-color: #5c8cff !important;
        box-shadow: 0 0 0 1px #5c8cff !important;
    }

    /* Select boxes */
    div[data-baseweb="select"] > div {
        background-color: #111b2d !important;
        border-color: #33425c !important;
        color: #f4f7fb !important;
        border-radius: 10px !important;
    }

    /* Buttons */
    .stButton > button {
        width: 100%;
        border-radius: 10px;
        border: 1px solid #33425c;
        background: #18243a;
        color: #f4f7fb;
        font-weight: 600;
        padding: 0.65rem 1rem;
    }

    .stButton > button:hover {
        border-color: #6b91ff;
        background: #202f4c;
        color: white;
    }

    /* Primary button */
    button[kind="primary"] {
        background: #315edb !important;
        border-color: #315edb !important;
        color: white !important;
    }

    button[kind="primary"]:hover {
        background: #3f6df0 !important;
    }

    /* Cards */
    .voice-card {
        background: #111b2d;
        border: 1px solid #293852;
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 18px;
    }

    .hero {
        background: linear-gradient(
            135deg,
            #111c30 0%,
            #14233c 100%
        );
        border: 1px solid #2c3d59;
        border-radius: 18px;
        padding: 28px;
        margin-bottom: 25px;
    }

    .hero-title {
        font-size: 34px;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 8px;
    }

    .hero-subtitle {
        font-size: 16px;
        color: #aebbd0;
        line-height: 1.6;
    }

    .section-title {
        font-size: 20px;
        font-weight: 700;
        color: #ffffff;
        margin-top: 10px;
        margin-bottom: 10px;
    }

    .small-text {
        color: #8f9db4;
        font-size: 13px;
    }

    .stat-card {
        background: #111b2d;
        border: 1px solid #293852;
        border-radius: 12px;
        padding: 18px;
        text-align: center;
    }

    .stat-number {
        font-size: 26px;
        font-weight: 800;
        color: white;
    }

    .stat-label {
        font-size: 13px;
        color: #8f9db4;
    }

    /* Success box */
    .success-card {
        background: #10261f;
        border: 1px solid #22553f;
        border-radius: 12px;
        padding: 16px;
        color: #b8f3d3;
    }

    /* Info box */
    .info-card {
        background: #101f34;
        border: 1px solid #274b70;
        border-radius: 12px;
        padding: 16px;
        color: #bdd9f5;
    }

    /* Warning */
    .warning-card {
        background: #2a2110;
        border: 1px solid #604b1e;
        border-radius: 12px;
        padding: 16px;
        color: #f2d58c;
    }

    /* Divider */
    hr {
        border-color: #26354d !important;
    }

</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# API KEY
# ============================================================

def get_api_key():
    """
    Get Gemini API key from Streamlit Secrets first,
    then environment variable.
    """

    try:
        key = st.secrets.get("GEMINI_API_KEY", "")
        if key:
            return key
    except Exception:
        pass

    return os.environ.get("GEMINI_API_KEY", "")


# ============================================================
# PCM -> WAV
# ============================================================

def pcm_to_wav(
    pcm_data,
    sample_rate=24000,
    channels=1,
    sample_width=2,
):
    """
    Convert raw PCM audio bytes into WAV bytes.
    Gemini TTS returns PCM audio.
    """

    if isinstance(pcm_data, str):
        try:
            pcm_data = base64.b64decode(pcm_data)
        except Exception:
            raise RuntimeError("Audio data could not be decoded.")

    if not isinstance(pcm_data, bytes):
        pcm_data = bytes(pcm_data)

    output = io.BytesIO()

    with wave.open(output, "wb") as wav_file:
        wav_file.setnchannels(channels)
        wav_file.setsampwidth(sample_width)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(pcm_data)

    return output.getvalue()


# ============================================================
# WORD COUNT
# ============================================================

def count_words(text):
    if not text:
        return 0

    return len(text.split())


# ============================================================
# BUILD TTS PROMPT
# ============================================================

def build_tts_prompt(
    text,
    style,
    speed,
    consistency,
    character,
    intensity,
):
    """
    Create a natural language instruction for Gemini TTS.
    """

    speed_instruction = {
        "Very Slow": "Speak very slowly and clearly.",
        "Slow": "Speak slowly with comfortable pauses.",
        "Normal": "Use a natural conversational speaking speed.",
        "Fast": "Speak slightly faster while remaining clear.",
        "Very Fast": "Speak quickly but keep the words understandable.",
    }

    consistency_instruction = {
        "Low": "Allow natural variation in pitch and expression.",
        "Medium": "Maintain a balanced and consistent speaking style.",
        "High": "Keep the voice highly consistent and controlled.",
    }

    character_instruction = {
        "Neutral": "Use a neutral personality.",
        "Warm": "Sound warm, welcoming and approachable.",
        "Confident": "Sound confident and assured.",
        "Friendly": "Sound friendly and pleasant.",
        "Authoritative": "Sound authoritative and professional.",
        "Dramatic": "Use expressive dramatic delivery.",
    }

    intensity_instruction = {
        "Low": "Keep emotional intensity subtle.",
        "Medium": "Use moderate emotional expression.",
        "High": "Use strong expressive emotion.",
    }

    prompt = f"""
Read the following text aloud.

Voice style:
{style}

Delivery:
{speed_instruction.get(speed, "Use a natural speaking speed.")}

Voice consistency:
{consistency_instruction.get(consistency, "Maintain consistent delivery.")}

Character:
{character_instruction.get(character, "Use a neutral personality.")}

Expression:
{intensity_instruction.get(intensity, "Use moderate expression.")}

Important:
- Speak naturally.
- Do not announce these instructions.
- Do not add explanations.
- Do not add extra words.
- Pronounce the text clearly.
- Use appropriate pauses and emphasis.
- Preserve the original wording.

Text to speak:

{text}
"""

    return prompt.strip()


# ============================================================
# GENERATE SPEECH
# ============================================================

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
    Generate speech using Google Gemini TTS.
    """

    api_key = get_api_key()

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. "
            "Add GEMINI_API_KEY to Streamlit Secrets."
        )

    if not text or not text.strip():
        raise RuntimeError(
            "Please enter some text before generating speech."
        )

    try:

        # Current Google GenAI SDK
        from google import genai
        from google.genai import types

        client = genai.Client(
            api_key=api_key
        )

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

        # ----------------------------------------------------
        # Check response
        # ----------------------------------------------------

        if not response:
            raise RuntimeError(
                "Gemini returned an empty response."
            )

        if not response.candidates:
            raise RuntimeError(
                "Gemini returned no candidates."
            )

        # ----------------------------------------------------
        # Find audio data
        # ----------------------------------------------------

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

                audio_data = getattr(
                    inline_data,
                    "data",
                    None,
                )

                if not audio_data:
                    continue

                # Convert PCM to WAV
                wav_audio = pcm_to_wav(
                    audio_data,
                    sample_rate=24000,
                    channels=1,
                    sample_width=2,
                )

                return wav_audio

        # ----------------------------------------------------
        # No audio found
        # ----------------------------------------------------

        raise RuntimeError(
            "Gemini responded successfully, but no audio "
            "data was found in the response."
        )

    except Exception as error:

        # Keep the REAL Gemini error.
        # This is important for debugging 401/403/404/429 errors.

        error_type = type(error).__name__

        raise RuntimeError(
            f"{error_type}: {error}"
        ) from error


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div style="font-size:26px;font-weight:800;color:white;">
        🎙️ AI Voice Studio
        </div>
        <div style="color:#8f9db4;margin-top:5px;margin-bottom:20px;">
        AI-powered text-to-speech
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

    st.divider()

    api_key = get_api_key()

    if api_key:

        st.success(
            "Gemini API configured",
            icon="✅",
        )

    else:

        st.error(
            "Gemini API key missing",
            icon="❌",
        )

    st.caption(
        "API key is read from Streamlit Secrets."
    )


# ============================================================
# VOICE STUDIO
# ============================================================

if page == "🎙️ Voice Studio":

    # --------------------------------------------------------
    # HERO
    # --------------------------------------------------------

    st.markdown(
        """
        <div class="hero">
            <div class="hero-title">
                🎙️ AI Voice Studio
            </div>
            <div class="hero-subtitle">
                Turn your text into natural-sounding speech
                using Google Gemini Text-to-Speech.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # STATS
    # --------------------------------------------------------

    stat1, stat2, stat3 = st.columns(3)

    with stat1:
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-number">
                    {st.session_state.generation_count}
                </div>
                <div class="stat-label">
                    Generations
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with stat2:
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-number">
                    {count_words(st.session_state.generated_text)}
                </div>
                <div class="stat-label">
                    Last words
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with stat3:
        st.markdown(
            """
            <div class="stat-card">
                <div class="stat-number">
                    Gemini
                </div>
                <div class="stat-label">
                    AI Engine
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")

    # --------------------------------------------------------
    # TEXT INPUT
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">📝 Your Script</div>',
        unsafe_allow_html=True,
    )

    text = st.text_area(
        "Write or paste your narration",
        height=260,
        placeholder=(
            "Enter the text you want to convert into speech...\n\n"
            "Example:\n"
            "Welcome to our channel. Today we are going "
            "to explore the fascinating world of artificial intelligence."
        ),
        label_visibility="collapsed",
    )

    word_count = count_words(text)

    st.caption(
        f"{word_count} words"
    )

    st.divider()

    # --------------------------------------------------------
    # SETTINGS
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">🎛️ Voice Settings</div>',
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    with col1:

        model_name = st.selectbox(
            "AI Engine",
            list(MODELS.keys()),
            index=0,
        )

        model = MODELS[model_name]

        voice = st.selectbox(
            "Voice",
            list(VOICES.keys()),
            index=0,
        )

        st.caption(
            f"Voice character: {VOICES[voice]}"
        )

        style = st.selectbox(
            "Speaking Style",
            STYLES,
            index=0,
        )

    with col2:

        speed = st.select_slider(
            "Speaking Speed",
            options=[
                "Very Slow",
                "Slow",
                "Normal",
                "Fast",
                "Very Fast",
            ],
            value="Normal",
        )

        consistency = st.select_slider(
            "Voice Consistency",
            options=[
                "Low",
                "Medium",
                "High",
            ],
            value="Medium",
        )

        character = st.selectbox(
            "Character",
            [
                "Neutral",
                "Warm",
                "Confident",
                "Friendly",
                "Authoritative",
                "Dramatic",
            ],
            index=0,
        )

        intensity = st.select_slider(
            "Expression Intensity",
            options=[
                "Low",
                "Medium",
                "High",
            ],
            value="Medium",
        )

    st.write("")

    # --------------------------------------------------------
    # BUTTONS
    # --------------------------------------------------------

    button1, button2, button3 = st.columns(
        [2, 1, 1]
    )

    with button1:

        generate = st.button(
            "🎙️ Generate Speech",
            type="primary",
            use_container_width=True,
        )

    with button2:

        test_voice = st.button(
            "🔊 Test Voice",
            use_container_width=True,
        )

    with button3:

        clear = st.button(
            "🗑️ Clear",
            use_container_width=True,
        )

    # --------------------------------------------------------
    # CLEAR
    # --------------------------------------------------------

    if clear:

        st.session_state.generated_audio = None
        st.session_state.generated_text = ""

        st.rerun()

    # --------------------------------------------------------
    # TEST VOICE
    # --------------------------------------------------------

    if test_voice:

        if not api_key:

            st.error(
                "GEMINI_API_KEY is not configured."
            )

            st.info(
                "Go to your Streamlit Cloud app → "
                "Settings → Secrets and add GEMINI_API_KEY."
            )

        else:

            test_text = (
                "Hello! This is a test of the AI Voice Studio. "
                "Your Gemini voice is working correctly."
            )

            with st.spinner(
                "Testing Gemini voice..."
            ):

                try:

                    audio = generate_speech(
                        text=test_text,
                        model=model,
                        voice=voice,
                        style=style,
                        speed=speed,
                        consistency=consistency,
                        character=character,
                        intensity=intensity,
                    )

                    st.success(
                        "Voice test generated successfully!"
                    )

                    st.audio(
                        audio,
                        format="audio/wav",
                    )

                except Exception as error:

                    error_text = str(error)

                    st.error(
                        "Voice test failed."
                    )

                    with st.expander(
                        "🔍 Show technical error",
                        expanded=True,
                    ):

                        st.code(
                            error_text,
                            language="text",
                        )

                    if "401" in error_text:

                        st.warning(
                            "The Gemini API key appears to be "
                            "invalid or is not being accepted."
                        )

                    elif "403" in error_text:

                        st.warning(
                            "Gemini rejected access to this "
                            "model/API. Your project may not "
                            "have access to the selected TTS model."
                        )

                    elif "404" in error_text:

                        st.warning(
                            "The selected TTS model was not found. "
                            "Try the other model from the AI Engine menu."
                        )

                    elif "429" in error_text:

                        st.warning(
                            "Gemini API quota or rate limit was reached. "
                            "Please wait and try again."
                        )

    # --------------------------------------------------------
    # GENERATE
    # --------------------------------------------------------

    if generate:

        if not text.strip():

            st.warning(
                "Please enter some text first."
            )

        elif not api_key:

            st.error(
                "GEMINI_API_KEY is not configured."
            )

            st.info(
                "Add your Gemini API key in Streamlit Secrets."
            )

        else:

            with st.spinner(
                "🎙️ Generating natural speech..."
            ):

                try:

                    audio = generate_speech(
                        text=text,
                        model=model,
                        voice=voice,
                        style=style,
                        speed=speed,
                        consistency=consistency,
                        character=character,
                        intensity=intensity,
                    )

                    # Save current result
                    st.session_state.generated_audio = audio
                    st.session_state.generated_text = text
                    st.session_state.generation_count += 1

                    # Save history
                    st.session_state.history.insert(
                        0,
                        {
                            "date": datetime.now().strftime(
                                "%Y-%m-%d %H:%M"
                            ),
                            "voice": voice,
                            "style": style,
                            "words": count_words(text),
                            "text": text,
                            "audio": audio,
                        },
                    )

                    # Keep last 20
                    st.session_state.history = (
                        st.session_state.history[:20]
                    )

                    st.success(
                        "Speech generated successfully! 🎉"
                    )

                except Exception as error:

                    error_text = str(error)

                    st.error(
                        "Speech generation failed."
                    )

                    # IMPORTANT:
                    # Show the real error instead of hiding it.

                    with st.expander(
                        "🔍 Show technical error",
                        expanded=True,
                    ):

                        st.code(
                            error_text,
                            language="text",
                        )

                    # Helpful diagnosis

                    if "401" in error_text:

                        st.warning(
                            "🔐 Authentication error (401): "
                            "Your Gemini API key is invalid, "
                            "expired, or not being accepted."
                        )

                    elif "403" in error_text:

                        st.warning(
                            "🚫 Permission error (403): "
                            "Your API key/project may not have "
                            "access to the selected Gemini TTS model."
                        )

                        st.info(
                            "Try selecting another TTS model "
                            "from the AI Engine menu."
                        )

                    elif "404" in error_text:

                        st.warning(
                            "❌ Model not found (404): "
                            "The selected model is unavailable "
                            "for your API/project."
                        )

                    elif "429" in error_text:

                        st.warning(
                            "⏳ Rate limit/quota error (429): "
                            "Gemini has temporarily limited your requests."
                        )

                    elif "GEMINI_API_KEY" in error_text:

                        st.warning(
                            "🔑 GEMINI_API_KEY is missing "
                            "from Streamlit Secrets."
                        )

                    else:

                        st.info(
                            "Open the technical error above. "
                            "The exact Gemini error is shown there "
                            "so it can be diagnosed."
                        )

    # --------------------------------------------------------
    # AUDIO PLAYER
    # --------------------------------------------------------

    if st.session_state.generated_audio:

        st.divider()

        st.markdown(
            '<div class="section-title">🎧 Generated Audio</div>',
            unsafe_allow_html=True,
        )

        st.audio(
            st.session_state.generated_audio,
            format="audio/wav",
        )

        st.download_button(
            label="⬇️ Download WAV Audio",
            data=st.session_state.generated_audio,
            file_name="ai_voice_studio.wav",
            mime="audio/wav",
            use_container_width=True,
        )

        st.markdown(
            """
            <div class="success-card">
                <strong>Audio ready</strong><br>
                Your speech has been converted to WAV format.
                You can listen to it above or download it.
            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# HISTORY
# ============================================================

elif page == "🕘 History":

    st.markdown(
        """
        <div class="hero">
            <div class="hero-title">
                🕘 Generation History
            </div>
            <div class="hero-subtitle">
                Review your recent voice generations.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not st.session_state.history:

        st.info(
            "No generations yet. Create your first voice "
            "from Voice Studio."
        )

    else:

        if st.button(
            "🗑️ Clear History",
            use_container_width=True,
        ):

            st.session_state.history = []

            st.rerun()

        st.write("")

        for index, item in enumerate(
            st.session_state.history
        ):

            with st.expander(
                f"🎙️ {item['voice']} • "
                f"{item['style']} • "
                f"{item['date']}"
            ):

                st.write(
                    f"**Words:** {item['words']}"
                )

                st.write(
                    f"**Voice:** {item['voice']}"
                )

                st.write(
                    f"**Style:** {item['style']}"
                )

                st.write(
                    "**Text:**"
                )

                st.write(
                    item["text"]
                )

                st.audio(
                    item["audio"],
                    format="audio/wav",
                )

                st.download_button(
                    label="⬇️ Download",
                    data=item["audio"],
                    file_name=(
                        f"voice_generation_{index + 1}.wav"
                    ),
                    mime="audio/wav",
                    key=f"download_{index}",
                )


# ============================================================
# SETTINGS
# ============================================================

elif page == "⚙️ Settings":

    st.markdown(
        """
        <div class="hero">
            <div class="hero-title">
                ⚙️ Settings
            </div>
            <div class="hero-subtitle">
                Configure your AI Voice Studio environment.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        "### 🔐 Gemini API Configuration"
    )

    if api_key:

        st.success(
            "GEMINI_API_KEY is configured.",
            icon="✅",
        )

        st.caption(
            "Your API key is stored in Streamlit Secrets "
            "and is not displayed here."
        )

    else:

        st.error(
            "GEMINI_API_KEY is not configured.",
            icon="❌",
        )

        st.markdown(
            """
            Add the following to Streamlit Cloud Secrets:

            ```toml
            GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
            ```
            """
        )

    st.divider()

    st.markdown(
        "### 🤖 Available Models"
    )

    for name, model_id in MODELS.items():

        st.write(
            f"**{name}**"
        )

        st.code(
            model_id,
            language="text",
        )

    st.divider()

    st.markdown(
        "### 🎙️ Available Voices"
    )

    for voice_name, description in VOICES.items():

        st.write(
            f"**{voice_name}** — {description}"
        )


# ============================================================
# ABOUT
# ============================================================

elif page == "ℹ️ About":

    st.markdown(
        """
        <div class="hero">
            <div class="hero-title">
                ℹ️ About AI Voice Studio
            </div>
            <div class="hero-subtitle">
                A simple AI-powered text-to-speech studio
                built with Streamlit and Google Gemini.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        ### 🎙️ What can you do?

        - Convert text into natural speech
        - Select different Gemini voices
        - Change speaking style
        - Control speaking speed
        - Control voice consistency
        - Adjust character
        - Adjust expression intensity
        - Listen to generated audio
        - Download WAV files
        - Review recent generations

        ### 🧠 Technology

        **Frontend / App**
        - Streamlit

        **AI**
        - Google Gemini Text-to-Speech

        **Audio**
        - PCM → WAV conversion

        ### 🔐 Security

        Your Gemini API key should be stored in:

        `Streamlit Cloud → Settings → Secrets`

        Never put your API key directly inside `app.py`.
        """
    )

    st.divider()

    st.caption(
        "AI Voice Studio • Built with Streamlit + Gemini"
    )
