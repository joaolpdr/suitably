"""Recursos de voz: transcrição (e, na próxima etapa, síntese)."""

from google.genai import types

from agent import MODELO, get_client

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