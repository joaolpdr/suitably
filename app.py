"""Interface do Suitably (Streamlit)."""

import streamlit as st

from suitability import PERGUNTAS, calcular_perfil, carregar_produtos, classificar_produtos

def mostrar_produtos(titulo: str, produtos: list[dict], mensagem_vazia: str) -> None:
    """Exibe uma lista de produtos ou uma mensagem quando a lista está vazia."""
    st.subheader(titulo)
    if not produtos:
        st.caption(mensagem_vazia)
        return
    for p in produtos:
        st.write(f"**{p['nome']}** · risco {p['risco']}/5")

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