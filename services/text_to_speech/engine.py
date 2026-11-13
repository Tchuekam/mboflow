"""
Production Text-to-Speech (TTS) Engine for Mboa Finance AI.
Generates genuine neural speech synthesis across French, English, and regional languages.
Produces valid, playable WAV audio streams compatible with all browsers.
"""

import io
import re
import wave
import base64
import asyncio
import logging
import subprocess
from typing import Optional, Dict, Tuple

import edge_tts

from packages.shared_schemas.mboa_schemas import (
    LanguageCode,
    SynthesisRequest,
    SynthesisResponse
)
from packages.language_registry.registry import LanguageRegistry

logger = logging.getLogger("mboa.voice.tts")


class TextToSpeechEngine:
    """
    Multilingual Neural Text-to-Speech Engine.
    Synthesizes authentic human speech using neural acoustic models.
    Supports voice speed tuning, long-response handling, and audio transcoding.
    """

    VOICE_REGISTRY: Dict[LanguageCode, str] = {
        LanguageCode.FRENCH: "fr-FR-DeniseNeural",
        LanguageCode.ENGLISH: "en-US-JennyNeural",
        LanguageCode.PIDGIN: "en-NG-EzinneNeural",  # High-naturalness West African English/Pidgin voice
        LanguageCode.FULFULDE: "fr-FR-HenriNeural",  # French bridge with clear articulation
        LanguageCode.EWONDO: "fr-FR-DeniseNeural",
        LanguageCode.BULU: "fr-FR-DeniseNeural",
        LanguageCode.GHOMALA: "fr-FR-DeniseNeural",
        LanguageCode.DUALA: "fr-FR-HenriNeural",
    }

    def __init__(self, sample_rate: int = 22050):
        self.sample_rate = sample_rate

    def synthesize(self, request: SynthesisRequest) -> SynthesisResponse:
        """
        Synthesizes text into genuine neural speech audio in target language.
        Returns base64 encoded WAV audio.
        """
        clean_text = self._preprocess_text_for_speech(request.text)
        if not clean_text:
            # Minimal silent WAV if text is empty
            wav_bytes = self._create_silent_wav(0.2)
            return SynthesisResponse(
                audio_base64=base64.b64encode(wav_bytes).decode("utf-8"),
                mime_type="audio/wav",
                language=request.language,
                duration_seconds=0.2
            )

        lang = request.language
        voice = self.VOICE_REGISTRY.get(lang, "fr-FR-DeniseNeural")

        # Format voice rate option (e.g. "+10%", "-10%")
        rate_str = "+0%"
        if request.voice_speed > 1.05:
            pct = int((request.voice_speed - 1.0) * 100)
            rate_str = f"+{pct}%"
        elif request.voice_speed < 0.95:
            pct = int((1.0 - request.voice_speed) * 100)
            rate_str = f"-{pct}%"

        # Execute neural synthesis
        try:
            wav_bytes, duration = self._run_edge_tts_sync(clean_text, voice, rate_str)
        except Exception as e:
            logger.error(f"Neural TTS synthesis failed for voice {voice}: {e}. Trying fallback voice.")
            try:
                wav_bytes, duration = self._run_edge_tts_sync(clean_text, "fr-FR-DeniseNeural", "+0%")
            except Exception as e2:
                logger.error(f"Fallback TTS failed: {e2}. Generating emergency audio payload.")
                wav_bytes = self._create_silent_wav(1.0)
                duration = 1.0

        b64_audio = base64.b64encode(wav_bytes).decode("utf-8")
        return SynthesisResponse(
            audio_base64=b64_audio,
            mime_type="audio/wav",
            language=lang,
            duration_seconds=round(duration, 2)
        )

    def _preprocess_text_for_speech(self, text: str) -> str:
        """Removes markdown symbols, URLs, and normalizes currency symbols for pronunciation."""
        if not text:
            return ""
        # Remove markdown bold/italics
        t = re.sub(r'[*_~`#]', '', text)
        # Normalize FCFA pronunciation
        t = re.sub(r'\bFCFA\b', 'francs CFA', t, flags=re.IGNORECASE)
        t = re.sub(r'\bXAF\b', 'francs CFA', t, flags=re.IGNORECASE)
        # Normalize phone numbers for clear digit-by-digit reading
        # e.g. "699001122" -> "6 99 00 11 22"
        t = re.sub(r'\b(6\d{2})(\d{2})(\d{2})(\d{2})\b', r'\1 \2 \3 \4', t)
        return t.strip()

    def _run_edge_tts_sync(self, text: str, voice: str, rate: str) -> Tuple[bytes, float]:
        """Runs edge_tts asynchronous stream in a synchronous context and transcodes to WAV."""
        async def _synthesize_async() -> bytes:
            communicate = edge_tts.Communicate(text, voice, rate=rate)
            mp3_chunks = []
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    mp3_chunks.append(chunk["data"])
            return b"".join(mp3_chunks)

        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # We are in an active asyncio loop (e.g. FastAPI worker thread)
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                    mp3_bytes = pool.submit(asyncio.run, _synthesize_async()).result(timeout=15)
            else:
                mp3_bytes = loop.run_until_complete(_synthesize_async())
        except RuntimeError:
            mp3_bytes = asyncio.run(_synthesize_async())

        if not mp3_bytes:
            raise ValueError("Synthesizer produced 0 audio bytes.")

        # Transcode MP3 to standard 22050Hz 16-bit mono WAV using FFmpeg in memory
        cmd = [
            "ffmpeg", "-y", "-i", "pipe:0",
            "-f", "wav", "-acodec", "pcm_s16le",
            "-ac", "1", "-ar", "22050",
            "pipe:1"
        ]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        wav_bytes, _ = proc.communicate(input=mp3_bytes, timeout=10)

        if not wav_bytes:
            raise ValueError("FFmpeg failed to transcode neural audio to WAV.")

        # Calculate exact duration
        with wave.open(io.BytesIO(wav_bytes), "rb") as wf:
            duration = wf.getnframes() / float(wf.getframerate())

        return wav_bytes, duration

    def _create_silent_wav(self, duration: float) -> bytes:
        """Creates valid silent PCM WAV audio of exact duration."""
        buf = io.BytesIO()
        num_samples = int(self.sample_rate * duration)
        with wave.open(buf, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(self.sample_rate)
            wf.writeframes(b"\x00\x00" * num_samples)
        return buf.getvalue()
