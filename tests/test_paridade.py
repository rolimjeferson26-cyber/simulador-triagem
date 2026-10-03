"""Paridade entre o motor em Python (motor_pontuacao.py) e o motor em
JavaScript (motor.js, partilhado pelo Caso Treino e pela Avaliação ABCDE).

Carrega no Node.js o dados.js e o motor.js tal como as páginas os usam, e
compara tags e ranking com o motor Python nos mesmos cenários."""
import json
import os
import random
import shutil
import subprocess
import sys
import tempfile
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

import motor_pontuacao as m  # noqa: E402

PARAMETROS_GERADOS = {
    "FC": (30, 230), "FR": (0, 70), "PAS": (40, 220), "PAD": (30, 130),
    "SpO2": (70, 100), "Temp": (33, 41), "Glicemia": (30, 400), "Glasgow": (3, 15),
}


def _motor_js():
    caminho = lambda nome: json.dumps(os.path.join(RAIZ, nome))
    return (
        "var fs = require('fs'), vm = require('vm');\n"
        "var contexto = { window: {} }; vm.createContext(contexto);\n"
        "vm.runInContext(fs.readFileSync(%s, 'utf8'), contexto);\n"
        "var M = require(%s)(contexto.window.DADOS);\n"
        "var cenarios = process.argv[2] === 'referencia' ? [] : JSON.parse(fs.readFileSync(0, 'utf8'));\n"
        "if (process.argv[2] === 'referencia') {\n"
        "  var idades = JSON.parse(fs.readFileSync(0, 'utf8'));\n"
        "  process.stdout.write(JSON.stringify(idades.map(function(i){ return M.referenciaVitais(i); })));\n"
        "  process.exit(0);\n"
        "}\n"
        "process.stdout.write(JSON.stringify(cenarios.map(function(c){\n"
        "  var tv = M.tagsDosVitais(c.vitais, c.idade_meses);\n"
        "  var todas = new Set(c.tags); tv.forEach(function(t){ todas.add(t); });\n"
        "  var r = M.rankear(todas, { contextoTrauma: c.contexto_trauma, contextoPediatrico: c.contexto_pediatrico });\n"
        "  return { tags_vitais: Array.from(tv).sort(), ranking: r.map(function(x){\n"
        "    return [x.nome, x.variante, x.precisao, x.cobertura, x.f1]; }) };\n"
        "})));\n"
    ) % (caminho("dados.js"), caminho("motor.js"))


def _cenarios():
    rng = random.Random(2026)
    sintomas = [t["tag"] for t in m.taxonomia["sinais_sintomas"]]
    cenarios = []
    # 1) cada mês dos 0 aos 18 anos, com valores à volta dos limites do grupo
    for idade in range(0, 217):
        g = m.grupo_pediatrico(idade)
        if g:
            pas = m.pas_minima(g, idade)
            valores = [
                {"FC": g["fc_max"], "FR": g["fr_max"], "PAS": pas},
                {"FC": g["fc_max"] + 1, "FR": g["fr_max"] + 1, "PAS": pas - 1},
                {"FC": g["fc_min"] - 1, "PAD": 50, "SpO2": 93},
                {"Glicemia": g["glicemia_min"] - 1}, {"Glicemia": g["glicemia_min"]},
            ]
        else:
            valores = [{"FC": 101, "FR": 21, "PAS": 89}, {"FC": 59, "PAS": 140, "PAD": 90}]
        for v in valores:
            cenarios.append({"vitais": v, "tags": [], "idade_meses": idade,
                             "contexto_trauma": False, "contexto_pediatrico": True})
    # 2) os 5 casos incluídos, em todos os contextos, sem idade e com idades pediátricas
    with open(os.path.join(RAIZ, "casos_ficticios.json"), encoding="utf-8") as f:
        casos = json.load(f)
    for caso in casos:
        g = caso["gabarito"]
        for idade in (None, 6, 30, 100, 200, 216):
            for trauma in (False, True):
                for ped in (False, True):
                    cenarios.append({"vitais": g.get("vitais_esperados", {}), "tags": g.get("tags_esperadas", []),
                                     "idade_meses": idade, "contexto_trauma": trauma, "contexto_pediatrico": ped})
    # 3) cenários aleatórios, com e sem idade
    for _ in range(1500):
        vitais = {p: rng.randint(lo, hi) for p, (lo, hi) in PARAMETROS_GERADOS.items() if rng.random() < 0.5}
        idade = rng.choice([None, None, rng.randint(0, 240)])
        cenarios.append({"vitais": vitais, "tags": rng.sample(sintomas, rng.randint(0, 8)), "idade_meses": idade,
                         "contexto_trauma": rng.random() < 0.5, "contexto_pediatrico": rng.random() < 0.5})
    return cenarios


def _python(c):
    tv = m.tags_dos_vitais(c["vitais"], c["idade_meses"])
    r = m.rankear(set(c["tags"]) | tv, contexto_trauma=c["contexto_trauma"], contexto_pediatrico=c["contexto_pediatrico"])
    return {"tags_vitais": sorted(tv), "ranking": [[n, v, p, cob, f1] for n, v, p, cob, f1, b in r]}


def test_motor_js_igual_ao_python():
    node = shutil.which("node")
    if not node:
        raise unittest.SkipTest("Node.js não encontrado: instale-o para correr o teste de paridade")
    cenarios = _cenarios()
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as f:
        f.write(_motor_js())
        caminho = f.name
    try:
        saida = subprocess.run([node, caminho], input=json.dumps(cenarios), capture_output=True,
                               text=True, check=True).stdout
    finally:
        os.unlink(caminho)
    resultados_js = json.loads(saida)
    assert len(resultados_js) == len(cenarios)
    for c, js in zip(cenarios, resultados_js):
        assert js == _python(c), c


def test_referencia_da_consulta_js_igual_ao_python():
    # A página de Parâmetros Vitais mostra Motor.referenciaVitais(idade).
    node = shutil.which("node")
    if not node:
        raise unittest.SkipTest("Node.js não encontrado: instale-o para correr o teste de paridade")
    idades = [None] + list(range(0, 241))
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as f:
        f.write(_motor_js())
        caminho = f.name
    try:
        saida = subprocess.run([node, caminho, "referencia"], input=json.dumps(idades), capture_output=True,
                               text=True, check=True).stdout
    finally:
        os.unlink(caminho)
    for idade, js in zip(idades, json.loads(saida)):
        assert js == m.referencia_vitais(idade), idade
