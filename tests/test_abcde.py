"""Coerência do abcde.json (Avaliação ABCDE) com a taxonomia e o motor."""
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

import motor_pontuacao as m  # noqa: E402

with open(os.path.join(RAIZ, "abcde.json"), encoding="utf-8") as _f:
    ABCDE = json.load(_f)

TAGS_SINTOMAS = {t["tag"] for t in m.taxonomia["sinais_sintomas"]}
REGRAS_VITAIS = {t["tag"]: t["parametro"] for t in m.taxonomia["sinais_vitais"]}


def _tags_da_etapa(etapa):
    tags = [t for a in etapa["achados"] for t in a["tags"]]
    if "avds" in etapa:
        tags += [t for o in etapa["avds"]["opcoes"] for t in o["tags"]]
    return tags


def letra_da_tag():
    letra = {}
    for etapa in ABCDE["etapas"]:
        for t in _tags_da_etapa(etapa):
            letra.setdefault(t, etapa["letra"])
    for l, tags in ABCDE["sinais_vitais_por_letra"].items():
        for t in tags:
            letra[t] = l
    return letra


def test_letras_por_ordem():
    assert [e["letra"] for e in ABCDE["etapas"]] == ["A", "B", "C", "D", "E"]
    for e in ABCDE["etapas"]:
        assert e["titulo"] and e["objetivo"] and e["acoes"], e["letra"]


def test_todos_os_achados_apontam_para_tags_que_existem():
    for etapa in ABCDE["etapas"]:
        for t in _tags_da_etapa(etapa):
            assert t in TAGS_SINTOMAS, f"{etapa['letra']}: a tag {t} não existe em taxonomia.json (sinais_sintomas)"


def test_ids_dos_achados_unicos():
    ids = [a["id"] for e in ABCDE["etapas"] for a in e["achados"]]
    assert len(ids) == len(set(ids))


def test_cada_tag_pertence_a_uma_so_letra():
    vistas = {}
    for etapa in ABCDE["etapas"]:
        for t in set(_tags_da_etapa(etapa)):
            assert t not in vistas, f"a tag {t} aparece nas letras {vistas[t]} e {etapa['letra']}"
            vistas[t] = etapa["letra"]


def test_sinais_vitais_cobertos_e_coerentes():
    parametros = [p for e in ABCDE["etapas"] for p in e["sinais_vitais"]]
    assert sorted(parametros) == sorted(set(REGRAS_VITAIS.values())), "cada parâmetro vital tem de estar numa só letra"
    por_letra = ABCDE["sinais_vitais_por_letra"]
    todas = [t for tags in por_letra.values() for t in tags]
    assert sorted(todas) == sorted(REGRAS_VITAIS), "as 14 tags de sinais vitais têm de ter letra, uma só vez"
    params_da_letra = {e["letra"]: set(e["sinais_vitais"]) for e in ABCDE["etapas"]}
    for letra, tags in por_letra.items():
        for t in tags:
            assert REGRAS_VITAIS[t] in params_da_letra[letra], f"{t} ({REGRAS_VITAIS[t]}) não é medido na letra {letra}"


def test_avds_so_alerta_nao_ativa_tags():
    d = next(e for e in ABCDE["etapas"] if e["letra"] == "D")
    opcoes = {o["valor"]: o["tags"] for o in d["avds"]["opcoes"]}
    assert opcoes == {"A": [], "V": ["alteracao_consciencia"], "D": ["alteracao_consciencia"], "S": ["alteracao_consciencia"]}


def test_casos_simulados_abcde_mais_historia_dao_o_mesmo_ranking_do_caso_treino():
    # Na Avaliação ABCDE, cada tag esperada é marcada na sua letra ou, se não
    # pertencer a nenhuma, na etapa "História e sintomas" (seletor completo).
    letra = letra_da_tag()
    with open(os.path.join(RAIZ, "casos_ficticios.json"), encoding="utf-8") as f:
        casos = json.load(f)
    for caso in casos:
        g = caso["gabarito"]
        tv = m.tags_dos_vitais(g.get("vitais_esperados") or {}, caso.get("idade_meses"))
        esperadas = set(g.get("tags_esperadas", []))
        for t in esperadas:
            assert t in TAGS_SINTOMAS or t in REGRAS_VITAIS, (caso["id"], t)
        por_passo = {}
        for t in esperadas | tv:
            por_passo.setdefault(letra.get(t, "H"), set()).add(t)
        abcde = set().union(*por_passo.values())
        trauma = caso.get("categoria_alvo") == "Trauma"
        assert m.rankear(abcde, contexto_trauma=trauma) == m.rankear(esperadas | tv, contexto_trauma=trauma), caso["id"]
