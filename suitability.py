import json
from pathlib import Path

CAMINHO_PRODUTOS = Path(__file__).parent / "data" / "produtos.json"

"""Regras de suitability: questionário, pontuação e adequação de produtos."""

PERGUNTAS = {
    "objetivo": {
        "pergunta": "Qual é o seu principal objetivo ao investir?",
        "opcoes": {
            "Preservar o dinheiro": 1,
            "Crescer com segurança": 2,
            "Maximizar ganhos": 3,
        },
    },
    "prazo": {
        "pergunta": "Por quanto tempo você pode deixar o dinheiro aplicado?",
        "opcoes": {
            "Menos de 1 ano": 1,
            "De 1 a 5 anos": 2,
            "Mais de 5 anos": 3,
        },
    },
    "reacao": {
        "pergunta": "Se seu investimento caísse 15% em um mês, você:",
        "opcoes": {
            "Resgataria tudo": 1,
            "Esperaria recuperar": 2,
            "Aplicaria mais": 3,
        },
    },
    "reserva": {
        "pergunta": "Você tem reserva de emergência?",
        "opcoes": {
            "Não": 1,
            "Parcial": 2,
            "Sim, completa": 3,
        },
    },
}

FAIXAS_PERFIL = [
    (6, "Conservador", 2),
    (9, "Moderado", 3),
    (12, "Arrojado", 5),
]
# (pergunta, resposta) → perfil máximo permitido, independente da pontuação
TRAVAS = {
    ("reserva", "Não"): "Conservador",
    ("prazo", "Menos de 1 ano"): "Conservador",
}


def calcular_perfil(respostas: dict[str, str]) -> tuple[str, int]:
    """Recebe {chave_da_pergunta: opção escolhida} e retorna (perfil, risco máximo)."""
    faltando = set(PERGUNTAS) - set(respostas)
    if faltando:
        raise ValueError(f"Perguntas sem resposta: {sorted(faltando)}")

    pontos = 0
    for chave, dados in PERGUNTAS.items():
        opcao = respostas[chave]
        if opcao not in dados["opcoes"]:
            raise ValueError(f"Opção inválida para '{chave}': {opcao}")
        pontos += dados["opcoes"][opcao]

    # 1. Perfil pela pontuação
    indice = next(
        (i for i, (limite, _, _) in enumerate(FAIXAS_PERFIL) if pontos <= limite),
        None,
    )
    if indice is None:
        raise ValueError(f"Pontuação fora das faixas: {pontos}")

    # 2. Travas: o perfil nunca passa do máximo permitido
    ordem_perfis = [perfil for _, perfil, _ in FAIXAS_PERFIL]
    for (chave, opcao), perfil_max in TRAVAS.items():
        if respostas[chave] == opcao:
            indice = min(indice, ordem_perfis.index(perfil_max))

    _, perfil, risco_max = FAIXAS_PERFIL[indice]
    return perfil, risco_max


def carregar_produtos(caminho: Path = CAMINHO_PRODUTOS) -> list[dict]:
    """Lê o catálogo de produtos do JSON."""
    with open(caminho, encoding="utf-8") as arquivo:
        return json.load(arquivo)


def classificar_produtos(risco_max: int, produtos: list[dict]) -> tuple[list[dict], list[dict]]:
    """Separa os produtos em adequados e não adequados ao risco máximo do perfil."""
    adequados = [p for p in produtos if p["risco"] <= risco_max]
    nao_adequados = [p for p in produtos if p["risco"] > risco_max]
    return adequados, nao_adequados