import logging
from groq import AsyncGroq
from langsmith import traceable
from app.config import settings

logger = logging.getLogger(__name__)

# Initialize the official Async client
client = AsyncGroq(api_key=settings.GROQ_API_KEY.get_secret_value())

@traceable(
    name="groq_audio_transcription",
    run_type="llm",
    tags=["speech-to-text", "whisper", "groq"],
)
async def transcribe_audio(file_bytes: bytes, filename: str, content_type: str) -> str:
    """Asynchronously transcribes audio bytes using Groq's Whisper API."""
    try:
        result = await client.audio.transcriptions.create(
            file=(filename, file_bytes),
            model=settings.GROQ_MODEL,
            response_format="json",
            language="en",
            temperature=0.0,
        )
        return result.text
    except Exception as e:
        logger.error(f"Groq transcription failed: {e}")
        raise RuntimeError("Failed to transcribe audio data.") from e
