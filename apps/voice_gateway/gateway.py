"""
Voice Gateway for Mboa Finance AI.
Handles live bidirectional WebSocket audio streaming, VAD turn-taking,
interruption detection, and audio response streaming.
"""

import json
import base64
import asyncio
import logging
from typing import Dict
from fastapi import WebSocket, WebSocketDisconnect
from packages.shared_schemas.mboa_schemas import (
    LanguageCode,
    VADState,
    AgentMessageRequest,
    AgentMessageResponse
)
from services.speech_to_text.engine import VoiceActivityDetector, SpeechToTextEngine
from services.agent_orchestrator.orchestrator import AgentOrchestrator

logger = logging.getLogger("mboa.voice.gateway")


class VoiceStreamingGateway:
    """
    Manages active voice sessions and WebSocket streams.
    """

    def __init__(self, orchestrator: AgentOrchestrator):
        self.orchestrator = orchestrator
        self.active_connections: Dict[str, WebSocket] = {}

    async def handle_voice_websocket(self, websocket: WebSocket, session_id: str):
        """
        Main WebSocket loop for live streaming audio.
        """
        await websocket.accept()
        self.active_connections[session_id] = websocket
        vad = VoiceActivityDetector()
        audio_buffer = bytearray()
        target_lang = LanguageCode.FRENCH

        logger.info(f"Voice session connected: {session_id}")
        await websocket.send_json({
            "event": "CONNECTED",
            "session_id": session_id,
            "message": "Passerelle vocale Mboa connectée."
        })

        try:
            while True:
                message = await websocket.receive_text()
                payload = json.loads(message)
                event_type = payload.get("event")

                if event_type == "CONFIG":
                    lang_str = payload.get("language", "fra")
                    try:
                        target_lang = LanguageCode(lang_str)
                    except ValueError:
                        target_lang = LanguageCode.FRENCH
                    await websocket.send_json({
                        "event": "CONFIG_ACK",
                        "language": target_lang.value
                    })

                elif event_type == "AUDIO_CHUNK":
                    chunk_b64 = payload.get("data")
                    if chunk_b64:
                        chunk_bytes = base64.b64decode(chunk_b64)
                        audio_buffer.extend(chunk_bytes)

                        # Run VAD detection
                        vad_state = vad.process_chunk(chunk_bytes)

                        if vad_state == VADState.SPEECH_START:
                            await websocket.send_json({"event": "VAD_SPEECH_START"})

                        elif vad_state == VADState.SPEECH_END or payload.get("is_final"):
                            await websocket.send_json({"event": "VAD_SPEECH_END"})

                            # Process complete audio buffer through agent
                            response: AgentMessageResponse = await self.orchestrator.process_user_request(
                                AgentMessageRequest(
                                    session_id=session_id,
                                    audio_base64=base64.b64encode(audio_buffer).decode("utf-8"),
                                    language=target_lang
                                )
                            )

                            # Stream response back to client
                            await websocket.send_json({
                                "event": "AGENT_RESPONSE",
                                "transcription": response.transcribed_text,
                                "detected_language": response.detected_language.value,
                                "explanation": response.explanation,
                                "intent": response.intent.value,
                                "audio_base64": response.audio_base64,
                                "requires_confirmation": response.requires_user_confirmation,
                                "prepared_transaction": (
                                    response.prepared_transaction.model_dump()
                                    if response.prepared_transaction else None
                                )
                            })

                            # Reset audio buffer and VAD for next turn
                            audio_buffer.clear()
                            vad.reset()

                elif event_type == "INTERRUPT":
                    # User interrupted ongoing speech
                    audio_buffer.clear()
                    vad.reset()
                    await websocket.send_json({"event": "INTERRUPT_ACK"})

        except WebSocketDisconnect:
            logger.info(f"Voice session disconnected: {session_id}")
            self.active_connections.pop(session_id, None)
        except Exception as e:
            logger.error(f"Error in voice websocket: {e}")
            self.active_connections.pop(session_id, None)

