"""
Automated Test Suite for Genuine Voice Intelligence:
- Real Voice Activity Detection (VAD) with frame energy and boundary detection
- Real Neural Speech Synthesis (TTS) via edge-tts generating valid WAV audio
- Speech normalization, empty audio, and silence handling
"""

import io
import wave
import pytest
from packages.shared_schemas.mboa_schemas import (
    LanguageCode,
    VADState,
    SynthesisRequest
)
from services.speech_to_text.engine import VoiceActivityDetector, SpeechToTextEngine
from services.text_to_speech.engine import TextToSpeechEngine


def test_vad_silence_vs_speech_detection():
    """Verify VAD correctly distinguishes silence from high-energy speech frames."""
    vad = VoiceActivityDetector(sample_rate=16000)

    # 1. Pure silence (zeros)
    silent_chunk = b"\x00\x00" * 480  # 30ms of silence
    state_silence = vad.process_chunk(silent_chunk)
    assert state_silence == VADState.SILENCE
    assert vad.calculate_frame_energy(silent_chunk) == 0.0

    # 2. Simulated high-energy speech chunk (PCM sine wave with amplitude 8000)
    import numpy as np
    t = np.linspace(0, 0.03, 480, endpoint=False)
    sine_samples = (np.sin(2 * np.pi * 300 * t) * 8000).astype(np.int16)
    speech_chunk = sine_samples.tobytes()

    energy = vad.calculate_frame_energy(speech_chunk)
    assert energy > 4000.0  # Strong audible energy

    # First speech chunk starts transition
    state1 = vad.process_chunk(speech_chunk)
    # Second speech chunk triggers SPEECH_START
    state2 = vad.process_chunk(speech_chunk)
    assert state2 in (VADState.SPEECH_START, VADState.SPEECH_ACTIVE)


def test_stt_handles_empty_and_silent_audio():
    """Verify STT engine handles silent or empty audio gracefully without guessing phrases."""
    stt = SpeechToTextEngine()

    # Empty bytes
    res_empty = stt.transcribe_audio_bytes(b"", session_id="test_empty")
    assert res_empty.text == ""
    assert res_empty.confidence == 0.0

    # 1 second of silent WAV
    silent_wav = io.BytesIO()
    with wave.open(silent_wav, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        wf.writeframes(b"\x00\x00" * 16000)

    res_silent = stt.transcribe_audio_bytes(silent_wav.getvalue(), session_id="test_silent")
    assert res_silent.text == ""
    assert res_silent.confidence == 0.0
    # Must NOT return hardcoded default "Montre-moi mon solde"
    assert "Montre-moi mon solde" not in res_silent.text


def test_real_tts_speech_synthesis_french():
    """Verify Text-to-Speech synthesizes genuine WAV speech in French."""
    tts = TextToSpeechEngine()
    req = SynthesisRequest(
        text="Votre solde disponible est de 150 000 FCFA.",
        language=LanguageCode.FRENCH,
        voice_speed=1.0
    )
    resp = tts.synthesize(req)

    assert resp.audio_base64 is not None
    assert len(resp.audio_base64) > 5000  # Substantial genuine audio payload
    assert resp.mime_type == "audio/wav"
    assert resp.duration_seconds > 0.5


def test_real_tts_speech_synthesis_english():
    """Verify Text-to-Speech synthesizes genuine WAV speech in English."""
    tts = TextToSpeechEngine()
    req = SynthesisRequest(
        text="Your transfer of 25 000 FCFA has been confirmed.",
        language=LanguageCode.ENGLISH,
        voice_speed=1.0
    )
    resp = tts.synthesize(req)

    assert resp.audio_base64 is not None
    assert len(resp.audio_base64) > 5000
    assert resp.duration_seconds > 0.5


def test_real_tts_speech_synthesis_pidgin():
    """Verify Text-to-Speech synthesizes speech for Cameroonian Pidgin English."""
    tts = TextToSpeechEngine()
    req = SynthesisRequest(
        text="Ya balance wey you fit use na 150 000 FCFA.",
        language=LanguageCode.PIDGIN,
        voice_speed=1.0
    )
    resp = tts.synthesize(req)

    assert resp.audio_base64 is not None
    assert resp.language == LanguageCode.PIDGIN
    assert resp.duration_seconds > 0.5

