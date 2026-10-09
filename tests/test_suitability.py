import pytest

from suitability import PERGUNTAS, calcular_perfil, carregar_produtos, classificar_produtos


def respostas_com_pontos(pontos: int) -> dict[str, str]:
    """Monta respostas escolhendo, em cada pergunta, a opção que vale `pontos`."""
    return {
        chave: next(opcao for opcao, valor in dados["opcoes"].items() if valor == pontos)
        for chave, dados in PERGUNTAS.items()
    }


# --- Perfil ---

@pytest.mark.parametrize(
    "pontos, perfil_esperado, risco_esperado",
    [
        (1, "Conservador", 2),
        (2, "Moderado", 3),
        (3, "Arrojado", 5),
    ],
)
def test_calcular_perfil(pontos, perfil_esperado, risco_esperado):
    assert calcular_perfil(respostas_com_pontos(pontos)) == (perfil_esperado, risco_esperado)


def test_limite_entre_conservador_e_moderado():
    respostas = respostas_com_pontos(1)          # 4 pontos
    respostas["prazo"] = "Mais de 5 anos"        # +2 → 6 pontos
    assert calcular_perfil(respostas)[0] == "Conservador"

    respostas["reacao"] = "Esperaria recuperar"  # +1 → 7 pontos
    assert calcular_perfil(respostas)[0] == "Moderado"


# --- Validação ---

def test_resposta_faltando_gera_erro():
    with pytest.raises(ValueError, match="sem resposta"):
        calcular_perfil({"objetivo": "Preservar o dinheiro"})


def test_opcao_invalida_gera_erro():
    respostas = respostas_com_pontos(1)
    respostas["prazo"] = "Para sempre"
    with pytest.raises(ValueError, match="Opção inválida"):
        calcular_perfil(respostas)


# --- Produtos ---

def test_classificar_produtos_separa_por_risco():
    produtos = [
        {"nome": "A", "risco": 1},
        {"nome": "B", "risco": 3},
        {"nome": "C", "risco": 5},
    ]
    adequados, nao_adequados = classificar_produtos(3, produtos)
    assert [p["nome"] for p in adequados] == ["A", "B"]
    assert [p["nome"] for p in nao_adequados] == ["C"]


CAMPOS_OBRIGATORIOS = {"nome", "categoria", "risco", "liquidez", "garantia", "descricao"}


def test_catalogo_tem_campos_e_risco_validos():
    for produto in carregar_produtos():
        assert CAMPOS_OBRIGATORIOS.issubset(produto), produto.get("nome")
        assert 1 <= produto["risco"] <= 5, produto["nome"]