from unittest.mock import AsyncMock

import pytest

from app.services import multimodal


@pytest.mark.asyncio
async def test_multimodal_pipeline_calls_all_llm_services(monkeypatch):
    """Verify the pipeline connects STT, Gemini response, and TTS in order."""
    transcribe = AsyncMock(return_value="what is on this invoice")
    generate = AsyncMock(return_value="The invoice total is 125 dollars.")
    text_to_speech = AsyncMock(return_value=b"audio-bytes")
    track = AsyncMock()

    monkeypatch.setattr(multimodal, "transcribe_audio", transcribe)
    monkeypatch.setattr(multimodal, "generate_response", generate)
    monkeypatch.setattr(multimodal, "text_to_speech", text_to_speech)
    monkeypatch.setattr(multimodal.portkeys_client, "track_llm_call", track)

    result = await multimodal.process_multimodal_request(
        audio_bytes=b"audio-input",
        audio_filename="question.wav",
        audio_content_type="audio/wav",
        image_bytes=b"image-input",
        image_content_type="image/jpeg",
        conversation_context=[{"role": "user", "content": "Previous question"}],
        user_prompt="Read the total",
    )

    transcribe.assert_awaited_once_with(b"audio-input", "question.wav", "audio/wav")
    generate.assert_awaited_once_with(
        transcript="what is on this invoice",
        image_bytes=b"image-input",
        image_content_type="image/jpeg",
        conversation_context=[{"role": "user", "content": "Previous question"}],
        user_prompt="Read the total",
    )
    text_to_speech.assert_awaited_once_with("The invoice total is 125 dollars.")

    assert result == {
        "transcript": "what is on this invoice",
        "response_text": "The invoice total is 125 dollars.",
        "audio": b"audio-bytes",
    }

    # STT, response generation, and TTS each emit one monitoring event.
    assert track.await_count == 3


@pytest.mark.asyncio
async def test_multimodal_pipeline_propagates_provider_failure(monkeypatch):
    """Verify provider errors reach the API layer for consistent error handling."""
    transcribe = AsyncMock(side_effect=RuntimeError("STT unavailable"))
    generate = AsyncMock()
    text_to_speech = AsyncMock()
    track = AsyncMock()

    monkeypatch.setattr(multimodal, "transcribe_audio", transcribe)
    monkeypatch.setattr(multimodal, "generate_response", generate)
    monkeypatch.setattr(multimodal, "text_to_speech", text_to_speech)
    monkeypatch.setattr(multimodal.portkeys_client, "track_llm_call", track)

    with pytest.raises(RuntimeError, match="STT unavailable"):
        await multimodal.process_multimodal_request(
            audio_bytes=b"audio-input",
            audio_filename="question.wav",
            audio_content_type="audio/wav",
            image_bytes=None,
            image_content_type=None,
            conversation_context=[],
        )

    generate.assert_not_awaited()
    text_to_speech.assert_not_awaited()
    track.assert_not_awaited()
