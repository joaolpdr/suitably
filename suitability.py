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

    for limite, perfil, risco_max in FAIXAS_PERFIL:
        if pontos <= limite:
            return perfil, risco_max

    raise ValueError(f"Pontuação fora das faixas: {pontos}")