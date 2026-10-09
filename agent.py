from functools import lru_cache

"""Integração com o Gemini: regras do assistente Edu e criação do chat."""

import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

MODELO = os.getenv("GEMINI_MODEL", "gemini-3.7-flash")

REGRAS = """Você é o Edu, educador financeiro do projeto Suitably.

Seu papel:
- Explicar produtos e conceitos financeiros de forma simples, com exemplos do dia a dia.
- Responder em português, em no máximo 3 parágrafos curtos.

Regras obrigatórias:
1. Você EDUCA, não recomenda. Nunca diga "invista em X" nem indique quanto aplicar.
2. Use apenas as informações de produtos fornecidas abaixo. Se algo não estiver lá, diga que não tem essa informação.
3. O perfil do usuário e a classificação dos produtos já foram calculados. Nunca altere essa classificação.
4. Se perguntarem sobre um produto NÃO ADEQUADO, explique-o e deixe claro por que ele não é compatível com o perfil.
5. Se o usuário não tiver reserva de emergência completa, destaque a importância dela quando o assunto for investir.
6. Ao falar de produtos, termine lembrando que isto é conteúdo educativo, não recomendação de investimento.
7. Recuse com educação assuntos fora de finanças pessoais e investimentos."""


def _listar_produtos(produtos: list[dict]) -> str:
    if not produtos:
        return "- Nenhum"
    return "\n".join(
        f"- {p['nome']} (risco {p['risco']}/5, liquidez: {p['liquidez']}, "
        f"garantia: {p['garantia']}): {p['descricao']}"
        for p in produtos
    )


def montar_contexto(
    perfil: str,
    risco_max: int,
    respostas: dict[str, str],
    adequados: list[dict],
    nao_adequados: list[dict],
) -> str:
    """Transforma o resultado do suitability em texto para o modelo."""
    respostas_txt = "\n".join(f"- {chave}: {opcao}" for chave, opcao in respostas.items())
    return (
        f"PERFIL DO USUÁRIO: {perfil} (aceita risco até {risco_max}/5)\n\n"
        f"RESPOSTAS DO QUESTIONÁRIO:\n{respostas_txt}\n\n"
        f"PRODUTOS ADEQUADOS:\n{_listar_produtos(adequados)}\n\n"
        f"PRODUTOS NÃO ADEQUADOS:\n{_listar_produtos(nao_adequados)}"
    )


@lru_cache(maxsize=1)
def get_client() -> genai.Client:
    """Cria o client do Gemini uma única vez e reaproveita nas próximas chamadas."""
    return genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def criar_chat(contexto: str):
    """Cria uma conversa com o Gemini usando as regras e o contexto do usuário."""
    return get_client().chats.create(
        model=MODELO,
        config=types.GenerateContentConfig(
            system_instruction=f"{REGRAS}\n\n{contexto}",
            temperature=0.3,
        ),
    )