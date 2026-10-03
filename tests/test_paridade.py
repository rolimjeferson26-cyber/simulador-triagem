"""Paridade entre o motor em Python e o motor em JavaScript do index.html.

Extrai do index.html o código entre os marcadores // <motor> e // </motor>,
corre-o no Node.js com os dados embutidos na própria página, e compara tags e
ranking com o motor_pontuacao.py nos mesmos cenários."""
import json
import os
import random
import re
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
    with open(os.path.join(RAIZ, "index.html"), encoding="utf-8") as f:
        html = f.read()
    motor = re.search(r"// <motor>(.*?)// </motor>", html, re.S)
    assert motor, "marcadores // <motor> e // </motor> não encontrados no index.html"

    def bloco(bloco_id):
        return re.search(r'<script type="application/json" id="%s"[^>]*>(.*?)</script>' % bloco_id, html, re.S).group(1)

    return (
        "var taxonomia = %s;\nvar fichas = %s;\nvar limitesInem = (%s).limites_alerta_inem;\n%s\n"
        "var cenarios = JSON.parse(require('fs').readFileSync(0, 'utf8'));\n"
        "process.stdout.write(JSON.stringify(cenarios.map(function(c){\n"
        "  contextoTrauma = c.contexto_trauma; contextoPediatrico = c.contexto_pediatrico;\n"
        "  var tv = tagsDosVitais(c.vitais, c.idade_meses);\n"
        "  var todas = new Set(c.tags); tv.forEach(function(t){ todas.add(t); });\n"
        "  return { tags_vitais: Array.from(tv).sort(), ranking: rankear(todas).map(function(r){\n"
        "    return [r.nome, r.variante, r.precisao, r.cobertura, r.f1]; }) };\n"
        "})));\n"
    ) % (bloco("taxonomia-source"), bloco("criterios-source"), bloco("parametros-source"), motor.group(1))


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
