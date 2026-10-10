"""Interface do Suitably (Streamlit)."""

import hashlib

import streamlit as st
from google.genai import errors
from agent import criar_chat, get_client, montar_contexto

from agent import criar_chat, montar_contexto
from suitability import PERGUNTAS, calcular_perfil, carregar_produtos, classificar_produtos
from voz import sintetizar, transcrever
import os

LIMITE_PERGUNTAS = int(os.getenv("LIMITE_PERGUNTAS", "10"))
LIMITE_VOZ = int(os.getenv("LIMITE_VOZ", "3"))


# --- Funções ---

def mostrar_produtos(titulo: str, produtos: list[dict], mensagem_vazia: str) -> None:
    """Exibe uma lista de produtos ou uma mensagem quando a lista está vazia."""
    st.subheader(titulo)
    if not produtos:
        st.caption(mensagem_vazia)
        return
    for p in produtos:
        st.write(f"**{p['nome']}** · risco {p['risco']}/5")


def perguntar_ao_edu(pergunta: str) -> str | None:
    """Envia a pergunta ao Edu. Retorna a resposta ou None se a API falhar."""
    try:
        return st.session_state.chat.send_message(pergunta).text
    except errors.ServerError:
        st.error("O Edu está sobrecarregado no momento. Tente novamente em instantes.")
    except errors.ClientError:
        st.error("Não foi possível falar com o Edu. Verifique a chave e o modelo no arquivo .env.")
    return None


def transcrever_audio(audio: bytes, mime_type: str) -> str | None:
    """Transcreve o áudio. Retorna o texto ou None se falhar ou estiver inaudível."""
    try:
        texto = transcrever(audio, mime_type)
    except errors.ServerError:
        st.error("O serviço de voz está sobrecarregado. Tente novamente em instantes.")
        return None
    except errors.ClientError:
        st.error("Não foi possível processar o áudio. Verifique a chave e o modelo no .env.")
        return None
    if not texto or "[inaudível]" in texto:
        st.warning("Não consegui entender o áudio. Tente falar mais perto do microfone.")
        return None
    return texto


def sintetizar_audio(texto: str) -> bytes | None:
    """Gera a voz do Edu. Se falhar, avisa e devolve None (a resposta em texto continua)."""
    try:
        return sintetizar(texto)
    except (errors.APIError, AttributeError, IndexError) as erro:
        print(f"[voz] Falha ao sintetizar: {erro!r}")
        st.info("Não consegui gerar o áudio desta vez. A resposta está em texto acima.")
        return None


def responder(pergunta: str, via_voz: bool = False) -> None:
    """Mostra a pergunta, consulta o Edu e guarda a conversa no histórico."""
    st.chat_message("user").write(pergunta)
    with st.chat_message("assistant", avatar="📚"):
        with st.spinner("O Edu está pensando..."):
            resposta = perguntar_ao_edu(pergunta)
        if not resposta:
            return
        st.write(resposta)
        st.session_state.perguntas_feitas = st.session_state.get("perguntas_feitas", 0) + 1

        audio_resposta = None
        if via_voz:
            with st.spinner("Gerando áudio..."):
                audio_resposta = sintetizar_audio(resposta)
            if audio_resposta:
                st.audio(audio_resposta, format="audio/wav", autoplay=True)
            st.session_state.voz_usada = st.session_state.get("voz_usada", 0) + 1
    st.session_state.mensagens += [
        {"role": "user", "content": pergunta},
        {"role": "assistant", "content": resposta, "audio": audio_resposta},
    ]


# --- Página ---

st.set_page_config(page_title="Suitably", page_icon="📚")
st.title("📚 Suitably")
st.caption("Educação financeira de acordo com o seu perfil. Conteúdo educativo, não é recomendação de investimento.")

# --- Questionário ---
with st.sidebar:
    st.header("Seu perfil")
    with st.form("questionario"):
        respostas = {
            chave: st.radio(dados["pergunta"], list(dados["opcoes"]), index=None, key=chave)
            for chave, dados in PERGUNTAS.items()
        }
        enviado = st.form_submit_button("Calcular perfil")

if enviado:
    if None in respostas.values():
        st.sidebar.error("Responda todas as perguntas.")
    else:
        perfil, risco_max = calcular_perfil(respostas)
        adequados, nao_adequados = classificar_produtos(risco_max, carregar_produtos())
        st.session_state.update(
            perfil=perfil,
            risco_max=risco_max,
            respostas=respostas,
            adequados=adequados,
            nao_adequados=nao_adequados,
        )
        st.session_state.client = get_client()  # mantém a conexão viva enquanto o chat existir
        st.session_state.chat = criar_chat(
            montar_contexto(perfil, risco_max, respostas, adequados, nao_adequados)
        )
        st.session_state.mensagens = []

if "perfil" not in st.session_state:
    st.info("👈 Responda o questionário na barra lateral para começar.")
    st.stop()

# --- Resultado ---
st.success(f"Seu perfil: **{st.session_state.perfil}** (aceita risco até {st.session_state.risco_max}/5)")

col_ok, col_nao = st.columns(2)
with col_ok:
    mostrar_produtos("✅ Adequados", st.session_state.adequados, "Nenhum produto adequado.")
with col_nao:
    mostrar_produtos(
        "⛔ Não adequados",
        st.session_state.nao_adequados,
        "Todos os produtos do catálogo são compatíveis com o seu perfil.",
    )

# --- Chat ---
st.divider()
st.subheader("💬 Converse com o Edu")

for msg in st.session_state.mensagens:
    with st.chat_message(msg["role"], avatar="📚" if msg["role"] == "assistant" else None):
        st.write(msg["content"])
        if msg.get("audio"):
            st.audio(msg["audio"], format="audio/wav")

feitas = st.session_state.get("perguntas_feitas", 0)
voz_usada = st.session_state.get("voz_usada", 0)

if feitas >= LIMITE_PERGUNTAS:
    st.info("Você chegou ao limite de perguntas desta demonstração. Obrigado por testar o Suitably! 📚")
    st.stop()

st.caption(f"Perguntas restantes nesta demonstração: {LIMITE_PERGUNTAS - feitas}")

if voz_usada < LIMITE_VOZ:
    audio = st.audio_input("🎤 Ou pergunte por voz")
    st.caption("O áudio é enviado ao Google (Gemini) para transcrição e para gerar a resposta falada.")
else:
    audio = None
    st.caption("Limite de perguntas por voz atingido. Você pode continuar por texto.")

if audio:
    audio_bytes = audio.getvalue()
    audio_id = hashlib.sha256(audio_bytes).hexdigest()
    if audio_id != st.session_state.get("ultimo_audio"):
        st.session_state.ultimo_audio = audio_id
        with st.spinner("Ouvindo..."):
            pergunta_voz = transcrever_audio(audio_bytes, audio.type)
        if pergunta_voz:
            responder(pergunta_voz, via_voz=True)

if pergunta := st.chat_input("Ex.: O que é LCI? Faz sentido para o meu perfil?"):
    responder(pergunta)