"""Pesquisa de sinais e sintomas (ui.js: pesquisarTags), usada na etapa
"História e sintomas" da Avaliação ABCDE e no seletor do Caso Treino.
Corre a função real do ui.js no Node.js, com os dados do dados.js."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

import motor_pontuacao as m  # noqa: E402

# termo -> (tags excluídas, limite)
JS = r"""
var fs = require('fs'), vm = require('vm');
var ctx = {}; ctx.window = ctx; vm.createContext(ctx);
['dados.js', 'motor.js', 'ui.js'].forEach(function(f){ vm.runInContext(fs.readFileSync(%s + '/' + f, 'utf8'), ctx, { filename: f }); });
var pedidos = JSON.parse(fs.readFileSync(0, 'utf8'));
process.stdout.write(JSON.stringify(pedidos.map(function(p){
  return ctx.UI.pesquisarTags(p.termo, { excluir: new Set(p.excluir || []), limite: p.limite || 50 });
})));
"""


def pesquisar(*pedidos):
    node = shutil.which("node")
    if not node:
        raise unittest.SkipTest("Node.js não encontrado: instale-o para testar a pesquisa")
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as f:
        f.write(JS % json.dumps(RAIZ))
        caminho = f.name
    try:
        saida = subprocess.run([node, caminho], input=json.dumps(list(pedidos)), capture_output=True,
                               text=True, check=True).stdout
    finally:
        os.unlink(caminho)
    return json.loads(saida)


def tags(resultado):
    return [r["tag"] for r in resultado]


def test_ignora_acentos_e_maiusculas():
    r = pesquisar({"termo": "convulsao"}, {"termo": "CONVULSÃO"}, {"termo": "Convulsão"})
    for res in r:
        assert "convulsao_presente" in tags(res)
    assert tags(r[0]) == tags(r[1]) == tags(r[2])


def test_sinonimos_comuns():
    esperado = {
        "falta de ar": "dispneia",
        "dor no peito": "dor_toracica_opressiva",
        "desmaio": "sincope_lipotimia",
        "vómito": "nauseas_vomitos",
        "vomito": "nauseas_vomitos",
        "dor de cabeça": "cefaleia_intensa",
        "dor de cabeca": "cefaleia_intensa",
    }
    resultados = pesquisar(*[{"termo": t} for t in esperado])
    for (termo, tag), res in zip(esperado.items(), resultados):
        assert tag in tags(res), (termo, tags(res))


def test_indica_o_sinonimo_que_correspondeu():
    res = pesquisar({"termo": "desmaio"})[0]
    item = next(r for r in res if r["tag"] == "sincope_lipotimia")
    assert item["sinonimo"] == "desmaio"
    res = pesquisar({"termo": "dispneia"})[0]
    assert next(r for r in res if r["tag"] == "dispneia")["sinonimo"] is None   # encontrado pelo rótulo


def test_so_a_partir_de_2_letras():
    r = pesquisar({"termo": ""}, {"termo": "d"}, {"termo": " d "}, {"termo": "do"})
    assert r[0] == r[1] == r[2] == []
    assert len(r[3]) > 0


def test_tags_ja_marcadas_nao_aparecem():
    r = pesquisar({"termo": "dor no peito"}, {"termo": "dor no peito", "excluir": ["dor_toracica_opressiva"]},
                  {"termo": "lábios roxos", "excluir": ["cianose"]})
    assert "dor_toracica_opressiva" in tags(r[0])
    assert "dor_toracica_opressiva" not in tags(r[1])
    assert tags(r[2]) == []


def test_limite_de_sugestoes():
    r = pesquisar({"termo": "dor", "limite": 3})[0]
    assert len(r) == 3


def test_sinonimos_sem_ambiguidade():
    dono = {}
    for t in m.taxonomia["sinais_sintomas"]:
        for s in t.get("sinonimos", []):
            chave = s.strip().lower()
            assert chave, t["tag"]
            assert chave not in dono, f"o sinónimo «{s}» aparece em {dono.get(chave)} e {t['tag']}"
            dono[chave] = t["tag"]
