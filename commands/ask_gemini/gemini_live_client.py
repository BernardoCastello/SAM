"""
Cliente para a API Gemini Live (audio-to-audio em tempo real via WebSocket).
Referência: https://ai.google.dev/api/multimodal-live
"""

import asyncio
import base64
import json
import os
import websockets
from dotenv import load_dotenv

load_dotenv()  # Carrega variáveis do arquivo .env na raiz do projeto

# Configurações do modelo
GEMINI_MODEL   = "gemini-2.0-flash-live-preview"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
WS_URL = (
    f"wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1beta"
    f".GenerativeService.BidiGenerateContent?key={GEMINI_API_KEY}"
)

# Formato de áudio que ENVIAMOS ao Gemini
INPUT_SAMPLE_RATE  = 16000   # Hz — padrão para voz
INPUT_CHANNELS     = 1
INPUT_FORMAT       = "audio/pcm"   # PCM 16-bit little-endian

# Formato de áudio que RECEBEMOS do Gemini
OUTPUT_SAMPLE_RATE = 24000   # Hz — o modelo responde em 24 kHz


async def ask_gemini_live(audio_pcm_bytes: bytes, system_prompt: str = "") -> bytes:
    """
    Envia áudio PCM ao Gemini Live e retorna o áudio PCM de resposta (concatenado).

    Parâmetros
    ----------
    audio_pcm_bytes : bytes
        Áudio gravado em PCM 16-bit, mono, 16 kHz.
    system_prompt : str
        Instrução de sistema opcional (ex: "Responda sempre em português.").

    Retorna
    -------
    bytes
        Áudio PCM 16-bit da resposta do Gemini (24 kHz).
    """
    setup_message = {
        "setup": {
            "model": f"models/{GEMINI_MODEL}",
            "generation_config": {
                "response_modalities": ["AUDIO"],
                "speech_config": {
                    "voice_config": {
                        "prebuilt_voice_config": {"voice_name": "Aoede"}
                    }
                },
            },
        }
    }

    if system_prompt:
        setup_message["setup"]["system_instruction"] = {
            "parts": [{"text": system_prompt}]
        }

    audio_b64 = base64.b64encode(audio_pcm_bytes).decode("utf-8")
    audio_message = {
        "realtime_input": {
            "media_chunks": [
                {
                    "mime_type": f"{INPUT_FORMAT};rate={INPUT_SAMPLE_RATE}",
                    "data": audio_b64,
                }
            ]
        }
    }

    if not GEMINI_API_KEY:
        raise EnvironmentError(
            "[Gemini] GEMINI_API_KEY não encontrada. "
            "Defina-a no arquivo .env na raiz do projeto."
        )

    response_audio_chunks = []

    async with websockets.connect(WS_URL) as ws:
        # 1. Envia configuração inicial
        await ws.send(json.dumps(setup_message))

        # 2. Aguarda confirmação do setup
        setup_resp = json.loads(await ws.recv())
        if "setupComplete" not in setup_resp:
            raise RuntimeError(f"[Gemini] Setup falhou: {setup_resp}")

        # 3. Envia o áudio da pergunta
        await ws.send(json.dumps(audio_message))

        # 4. Sinaliza fim do turno do usuário
        end_of_turn = {"client_content": {"turn_complete": True}}
        await ws.send(json.dumps(end_of_turn))

        # 5. Coleta chunks de áudio até o modelo terminar
        while True:
            raw = await ws.recv()
            msg = json.loads(raw)

            # Chunk de áudio na resposta
            for part in (
                msg.get("serverContent", {})
                   .get("modelTurn", {})
                   .get("parts", [])
            ):
                if "inlineData" in part:
                    chunk = base64.b64decode(part["inlineData"]["data"])
                    response_audio_chunks.append(chunk)

            # Verifica se o turno do modelo terminou
            if msg.get("serverContent", {}).get("turnComplete"):
                break

    return b"".join(response_audio_chunks)