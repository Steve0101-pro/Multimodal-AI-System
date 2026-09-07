import base64
import asyncio
import io
import logging
import wave
from google import genai
from google.genai import types
from google.genai.errors import APIError
from langsmith import traceable

from app.config import settings

logger = logging.getLogger(__name__)

# Initialize the client
client = genai.Client(api_key=settings.GEMINI_API_KEY.get_secret_value())
TTS_REQUEST_TIMEOUT_SECONDS = 45

@traceable(
    name="gemini_text_to_speech",
    run_type="llm",
    tags=["text-to-speech", "tts", "gemini"],
)
async def text_to_speech(text: str) -> bytes:
    """Asynchronously converts text into native audio file data using Gemini."""
    prompt = f"Speak naturally and warmly. Do not add extra words.\n\n{text}"

    try:
        for attempt in range(3):
            try:
                # Use client.aio to keep the network requests non-blocking
                response = await asyncio.wait_for(
                    client.aio.models.generate_content(
                        model=settings.GEMINI_TTS_MODEL,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            response_modalities=["AUDIO"],
                            speech_config=types.SpeechConfig(
                                voice_config=types.VoiceConfig(
                                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                        voice_name="Kore"
                                    )
                                )
                            ),
                        ),
                    ),
                    timeout=TTS_REQUEST_TIMEOUT_SECONDS,
                )
                break
            except APIError as exc:
                is_capacity_error = getattr(exc, "code", None) == 503
                if not is_capacity_error or attempt == 2:
                    raise
                await asyncio.sleep(2 ** attempt)

        # Access response elements safely
        part = response.candidates[0].content.parts[0]
        
        if not part.inline_data or not part.inline_data.data:
            raise ValueError("No inline audio data found in response parts.")

        # Decode base64 payload into raw binary file bytes
        raw_audio_data = part.inline_data.data
        if isinstance(raw_audio_data, str):
            audio_bytes = base64.b64decode(raw_audio_data)
        else:
            audio_bytes = raw_audio_data

        # Gemini returns signed 16-bit PCM samples without a WAV container.
        # Wrap the samples so clients can identify and play the audio.
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(24000)
            wav_file.writeframes(audio_bytes)

        return wav_buffer.getvalue()

    except (APIError, AttributeError, IndexError, TypeError, ValueError) as e:
        logger.error(f"Gemini TTS processing failed: {e}")
        raise RuntimeError("Gemini TTS engine did not return valid audio data.") from e
