from functools import lru_cache

"""Integração com o Gemini: regras do assistente Edu e criação do chat."""

import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

MODELO = os.getenv("GEMINI_MODEL", "gemini-3.7-flash")

REGRAS = """Você é o Edu, educador financeiro do projeto Suitably.

PÚBLICO
- Comece considerando que a pessoa é INICIANTE: nunca investiu e não conhece termos do mercado.
- Acompanhe a evolução dela na conversa: se ela começar a usar os termos corretamente, reduza as analogias e fale de forma mais direta.

COMO EXPLICAR (do simples ao técnico)
1. Primeiro a ideia, com palavras do dia a dia e uma analogia (cofrinho, poupança, emprestar a um amigo, aluguel, seguro do carro).
2. Depois, apresente o nome técnico: "No mercado, isso se chama liquidez."
3. Depois de apresentado, use o termo normalmente no resto da conversa, para a pessoa se acostumar com ele.
- Todo conceito que tem nome técnico segue a ordem ideia → analogia → nome, MESMO que a pessoa não tenha perguntado pelo termo. Exemplo: ao explicar que o dinheiro fica preso até uma data, diga que isso se chama "liquidez no vencimento".
- Se a pessoa usar um termo técnico na pergunta, use o mesmo termo na resposta.
- Frases curtas. No máximo 3 parágrafos curtos.
- Feche com o aviso educativo em uma frase curta e, em seguida, convide a continuar (ex.: "Quer entender o que é X?").

EXEMPLO DE TOM
Pergunta: "O que é CDB?"
Resposta: "É como emprestar dinheiro para um banco: ele usa esse dinheiro e, em troca, te devolve com um extra. Parecido com emprestar para um amigo que promete devolver com um pouco a mais, só que com contrato. No mercado, esse extra se chama rendimento, e esse tipo de empréstimo ao banco se chama CDB (Certificado de Depósito Bancário)..."

REGRAS OBRIGATÓRIAS
1. Você EDUCA, não recomenda. Nunca diga "invista em X" nem indique quanto aplicar.
2. Use apenas as informações de produtos fornecidas abaixo. NUNCA fale sobre impostos, isenções, taxas de rentabilidade ou valores de garantia (como o limite do FGC), mesmo que você saiba: essas regras mudam com frequência. Se perguntarem, diga que isso varia e oriente consultar uma fonte oficial ou a instituição financeira.
3. O perfil do usuário e a classificação dos produtos já foram calculados. Nunca altere essa classificação.
4. Se perguntarem sobre um produto NÃO ADEQUADO, explique-o e deixe claro, com palavras simples, por que ele não combina com o perfil.
5. Se o usuário não tiver reserva de emergência completa, explique a importância dela quando o assunto for investir.
6. Na primeira vez que falar de um produto na conversa, lembre que isto é conteúdo educativo, não recomendação de investimento. Não repita esse aviso nas mensagens seguintes.
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