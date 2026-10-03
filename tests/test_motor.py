"""Testes do motor de pontuação (motor_pontuacao.py): sinais vitais -> tags
com limites pediátricos do INEM, e garantia de que os resultados de adulto
não mudaram face à fotografia guardada em baseline_adulto.json."""
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

import motor_pontuacao as m  # noqa: E402


def meses(anos, meses_extra=0):
    return anos * 12 + meses_extra


def ranking(vitais, tags, idade_meses=None, trauma=False, pediatrico=False):
    tv = m.tags_dos_vitais(vitais, idade_meses)
    r = m.rankear(set(tags) | tv, contexto_trauma=trauma, contexto_pediatrico=pediatrico)
    return sorted(tv), [[nome, variante, f1] for nome, variante, p, c, f1, b in r]


# ---------------------------------------------------------------------------
# O exemplo que motivou a alteração
# ---------------------------------------------------------------------------

def test_bebe_6_meses_dentro_da_faixa_nao_gera_tags():
    # FC 140, FR 30 e PAS 80 estão dentro dos limites do INEM para 1-12 meses;
    # com as regras de adulto davam taquicardia, taquipneia e hipotensão.
    assert m.tags_dos_vitais({"FC": 140, "FR": 30, "PAS": 80}, 6) == set()


def test_mesmos_valores_sem_idade_continuam_a_usar_regras_de_adulto():
    assert m.tags_dos_vitais({"FC": 140, "FR": 30, "PAS": 80}) == {"taquicardia", "taquipneia", "hipotensao"}


# ---------------------------------------------------------------------------
# Valores fora da faixa geram a tag certa
# ---------------------------------------------------------------------------

def test_bebe_6_meses_fora_da_faixa():
    assert m.tags_dos_vitais({"FC": 200}, 6) == {"taquicardia"}
    assert m.tags_dos_vitais({"FC": 70}, 6) == {"bradicardia"}
    assert m.tags_dos_vitais({"FR": 45}, 6) == {"taquipneia"}
    assert m.tags_dos_vitais({"PAS": 69}, 6) == {"hipotensao"}


def test_valor_no_proprio_limite_ainda_e_aceitavel():
    # FC > fc_max, FC < fc_min, FR > fr_max e PAS < pas_min: o limite não ativa.
    assert m.tags_dos_vitais({"FC": 180, "FR": 40, "PAS": 70}, 6) == set()
    assert m.tags_dos_vitais({"FC": 80}, 6) == set()


# ---------------------------------------------------------------------------
# Limites entre grupos etários
# ---------------------------------------------------------------------------

def test_grupo_de_cada_idade():
    esperado = {
        0: "Recém-nascido",
        1: "1-12 meses",
        11: "1-12 meses",
        12: "1-5 anos",
        meses(5, 11): "1-5 anos",
        meses(6): "6-10 anos",
        meses(10, 11): "6-10 anos",
        meses(11): "> 10 anos",
        meses(17, 11): "> 10 anos",
    }
    for idade, grupo in esperado.items():
        assert m.grupo_pediatrico(idade)["grupo"] == grupo, (idade, grupo)
    assert m.grupo_pediatrico(meses(18)) is None
    assert m.grupo_pediatrico(None) is None


def test_fronteira_11_vs_12_meses():
    # FC 175: normal até 180 (1-12 meses), taquicardia acima de 140 (1-5 anos)
    assert m.tags_dos_vitais({"FC": 175}, 11) == set()
    assert m.tags_dos_vitais({"FC": 175}, 12) == {"taquicardia"}


def test_fronteira_5a11m_vs_6_anos():
    # FR 35: normal até 40 (1-5 anos), taquipneia acima de 30 (6-10 anos)
    assert m.tags_dos_vitais({"FR": 35}, meses(5, 11)) == set()
    assert m.tags_dos_vitais({"FR": 35}, meses(6)) == {"taquipneia"}


def test_fronteira_10a11m_vs_11_anos():
    # FC 110: normal até 120 (6-10 anos), taquicardia acima de 100 (> 10 anos)
    assert m.tags_dos_vitais({"FC": 110}, meses(10, 11)) == set()
    assert m.tags_dos_vitais({"FC": 110}, meses(11)) == {"taquicardia"}


def test_fronteira_17a11m_vs_18_anos():
    # FR 19: taquipneia acima de 18 (> 10 anos, INEM), normal até 20 (adulto)
    assert m.tags_dos_vitais({"FR": 19}, meses(17, 11)) == {"taquipneia"}
    assert m.tags_dos_vitais({"FR": 19}, meses(18)) == set()
    # PAS 150: hipertensão sistólica só se aplica a partir dos 18 anos
    assert m.tags_dos_vitais({"PAS": 150}, meses(17, 11)) == set()
    assert m.tags_dos_vitais({"PAS": 150}, meses(18)) == {"hipertensao"}


# ---------------------------------------------------------------------------
# PAS mínima: 70 + 2 × anos completos dos 1 aos 10 anos
# ---------------------------------------------------------------------------

def test_formula_pas_com_anos_completos():
    esperado = {
        0: 60,                # recém-nascido
        11: 70,               # 1-12 meses
        12: 72,               # 1 ano
        meses(4, 11): 78,     # 4 anos e 11 meses -> 4 anos completos
        meses(5, 11): 80,
        meses(6): 82,
        meses(10, 11): 90,
        meses(11): 90,        # > 10 anos: valor fixo
        meses(17, 11): 90,
    }
    for idade, pas in esperado.items():
        assert m.pas_minima(m.grupo_pediatrico(idade), idade) == pas, (idade, pas)


def test_hipotensao_usa_a_pas_minima_da_idade():
    idade = meses(4, 11)  # PAS mínima 78
    assert m.tags_dos_vitais({"PAS": 77}, idade) == {"hipotensao"}
    assert m.tags_dos_vitais({"PAS": 78}, idade) == set()


# ---------------------------------------------------------------------------
# Regras que mudam ou se mantêm abaixo dos 18 anos
# ---------------------------------------------------------------------------

def test_regras_so_de_adulto_nao_ativam_em_criancas():
    idade = meses(10)
    assert m.tags_dos_vitais({"PAD": 50, "PAS": 150}, idade) == set()
    assert m.tags_dos_vitais({"PAD": 95}, idade) == set()


def test_regras_mantidas_em_criancas():
    idade = meses(3)
    assert m.tags_dos_vitais({"SpO2": 93}, idade) == {"spo2_baixo"}
    assert m.tags_dos_vitais({"SpO2": 94}, idade) == set()
    assert m.tags_dos_vitais({"Temp": 38.0}, idade) == {"febre"}
    assert m.tags_dos_vitais({"Temp": 34.9}, idade) == {"hipotermia_vital"}
    assert m.tags_dos_vitais({"Glicemia": 59}, idade) == {"glicemia_baixa"}
    assert m.tags_dos_vitais({"Glicemia": 201}, idade) == {"glicemia_alta"}
    assert m.tags_dos_vitais({"Glasgow": 8}, idade) == {"glasgow_baixo"}
    # FR 0: apneia; fr_min não é usado (ainda não existe a tag bradipneia)
    assert m.tags_dos_vitais({"FR": 0}, idade) == {"apneia"}


# ---------------------------------------------------------------------------
# Adultos: resultados exatamente iguais aos de antes
# ---------------------------------------------------------------------------

def _baseline():
    with open(os.path.join(RAIZ, "tests", "baseline_adulto.json"), encoding="utf-8") as f:
        return json.load(f)["cenarios"]


def test_casos_incluidos_sao_de_adulto():
    with open(os.path.join(RAIZ, "casos_ficticios.json"), encoding="utf-8") as f:
        casos = json.load(f)
    assert len(casos) == 5
    for caso in casos:
        assert caso.get("idade_meses") is None, caso["id"]


def test_os_5_casos_incluidos_dao_o_mesmo_ranking_que_antes():
    cenarios = [c for c in _baseline() if not c["origem"].startswith("aleatorio_")]
    assert len(cenarios) == 20  # 5 casos × 4 contextos (trauma / pediátrico)
    for c in cenarios:
        obtido = ranking(c["vitais"], c["tags"], None, c["contexto_trauma"], c["contexto_pediatrico"])
        assert obtido == (c["esperado"]["tags_vitais"], c["esperado"]["ranking"]), c["origem"]


def test_cenarios_aleatorios_de_adulto_sem_alteracoes():
    for c in _baseline():
        esperado = (c["esperado"]["tags_vitais"], c["esperado"]["ranking"])
        # sem idade e com 18 anos exatos: as duas formas de "adulto"
        for idade in (None, meses(18)):
            obtido = ranking(c["vitais"], c["tags"], idade, c["contexto_trauma"], c["contexto_pediatrico"])
            assert obtido == esperado, (c["origem"], idade)
