"""
Comando: ask_gemini
Grava a pergunta do usuário em áudio bruto e envia ao Gemini Live,
que responde também em áudio (sem passar por transcrição).
"""

import asyncio
import struct
import sys
import threading

import pyaudio

from .gemini_live_client import (
    OUTPUT_SAMPLE_RATE,
    INPUT_CHANNELS,
    INPUT_SAMPLE_RATE,
    ask_gemini_live,
)

# ── Parâmetros de gravação ──────────────────────────────────────────────────
RECORD_SECONDS   = 8      # Tempo máximo de gravação da pergunta
CHUNK            = 1024   # Frames por buffer de leitura/escrita
PYAUDIO_FORMAT   = pyaudio.paInt16   # PCM 16-bit (igual ao que o Gemini espera)

# ── Prompt do sistema ───────────────────────────────────────────────────────
SYSTEM_PROMPT = (
    "Você é Sam, um assistente de voz pessoal. "
    "Responda sempre em português do Brasil, de forma clara e concisa."
)


def _gravar_pergunta() -> bytes:
    """Grava áudio do microfone por RECORD_SECONDS e retorna bytes PCM."""
    pa = pyaudio.PyAudio()
    stream = pa.open(
        format=PYAUDIO_FORMAT,
        channels=INPUT_CHANNELS,
        rate=INPUT_SAMPLE_RATE,
        input=True,
        frames_per_buffer=CHUNK,
    )

    print("    🎙️  Pode falar sua pergunta...")
    frames = []
    total_chunks = int(INPUT_SAMPLE_RATE / CHUNK * RECORD_SECONDS)

    for _ in range(total_chunks):
        frames.append(stream.read(CHUNK, exception_on_overflow=False))

    stream.stop_stream()
    stream.close()
    pa.terminate()
    print("    ✅ Pergunta capturada. Consultando Gemini...")

    return b"".join(frames)


def _reproduzir_audio(audio_pcm: bytes):
    """Reproduz bytes PCM (24 kHz, mono, 16-bit) no alto-falante padrão."""
    pa = pyaudio.PyAudio()
    stream = pa.open(
        format=PYAUDIO_FORMAT,
        channels=1,
        rate=OUTPUT_SAMPLE_RATE,
        output=True,
        frames_per_buffer=CHUNK,
    )

    # Envia o áudio em chunks para o stream de saída
    offset = 0
    while offset < len(audio_pcm):
        end = offset + CHUNK * 2          # *2 porque cada frame = 2 bytes (int16)
        stream.write(audio_pcm[offset:end])
        offset = end

    stream.stop_stream()
    stream.close()
    pa.terminate()


def ask_gemini():
    """
    Ponto de entrada registrado no WakeOnSpeech.

    Fluxo:
      1. Grava áudio da pergunta (até RECORD_SECONDS segundos)
      2. Envia ao Gemini Live via WebSocket
      3. Reproduz a resposta em áudio
    """
    try:
        audio_pergunta = _gravar_pergunta()
        audio_resposta = asyncio.run(ask_gemini_live(audio_pergunta, SYSTEM_PROMPT))

        if audio_resposta:
            print("    🔊 Reproduzindo resposta do Gemini...")
            _reproduzir_audio(audio_resposta)
        else:
            print("    [!] Gemini não retornou áudio.")

    except Exception as e:
        print(f"    [Erro] Falha ao consultar Gemini: {e}")