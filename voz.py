"""Recursos de voz: transcrição (áudio → texto) e síntese (texto → áudio)."""

import io
import os
import re
import wave

from google.genai import types

from agent import MODELO, get_client

MODELO_TTS = os.getenv("GEMINI_TTS_MODEL", "gemini-3.8-flash-tts")
VOZ = os.getenv("GEMINI_TTS_VOICE", "Kore")

PROMPT_TRANSCRICAO = (
    "Transcreva este áudio em português exatamente como foi falado. "
    "Responda apenas com a transcrição, sem comentários. "
    "Se não houver fala compreensível, responda apenas: [inaudível]"
)


def transcrever(audio: bytes, mime_type: str = "audio/wav") -> str:
    """Converte um áudio em texto usando o Gemini."""
    resposta = get_client().models.generate_content(
        model=MODELO,
        contents=[PROMPT_TRANSCRICAO, types.Part.from_bytes(data=audio, mime_type=mime_type)],
    )
    return resposta.text.strip()


def _limpar_markdown(texto: str) -> str:
    """Remove símbolos de formatação para o TTS não tentar lê-los."""
    return re.sub(r"[*_#`>]", "", texto)


def _pcm_para_wav(pcm: bytes, taxa: int = 24000) -> bytes:
    """O TTS devolve áudio 'cru' (PCM). Adiciona o cabeçalho WAV para o navegador tocar."""
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as arquivo:
        arquivo.setnchannels(1)      # mono
        arquivo.setsampwidth(2)      # 16 bits
        arquivo.setframerate(taxa)   # 24 kHz
        arquivo.writeframes(pcm)
    return buffer.getvalue()


def sintetizar(texto: str) -> bytes:
    """Converte texto em áudio WAV usando o modelo de voz do Gemini."""
    resposta = get_client().models.generate_content(
        model=MODELO_TTS,
        contents=_limpar_markdown(texto),
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=VOZ)
                )
            ),
        ),
    )
    pcm = resposta.candidates[0].content.parts[0].inline_data.data
    return _pcm_para_wav(pcm)