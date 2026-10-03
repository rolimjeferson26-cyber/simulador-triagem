"""O dados.js (usado pelas páginas) tem de estar sincronizado com os ficheiros
JSON (usados pelo motor em Python). O dados.js é gerado por
ferramentas/gerar_dados_js.py: se um JSON mudar e o dados.js não for gerado de
novo, os dois motores deixam de bater."""
import json
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "ferramentas"))

import gerar_dados_js  # noqa: E402

PAGINAS_SIMULADOR = ("index.html", "abcde.html")


def test_dados_js_esta_atualizado():
    with open(os.path.join(RAIZ, "dados.js"), encoding="utf-8") as f:
        atual = f.read()
    assert atual == gerar_dados_js.conteudo_dados_js(), (
        "o dados.js está desatualizado em relação aos ficheiros JSON: "
        "corra  python3 ferramentas/gerar_dados_js.py  e faça commit do dados.js"
    )


def test_dados_js_tem_todos_os_ficheiros_json():
    with open(os.path.join(RAIZ, "dados.js"), encoding="utf-8") as f:
        texto = f.read()
    for chave, ficheiro in gerar_dados_js.FONTES.items():
        linha = re.search(r'^  "%s": (.*?),?$' % re.escape(chave), texto, re.M)
        assert linha, f"chave {chave} em falta no dados.js"
        with open(os.path.join(RAIZ, ficheiro), encoding="utf-8") as f:
            assert json.loads(linha.group(1)) == json.load(f), chave


def test_docs_sinonimos_md_esta_atualizado():
    with open(os.path.join(RAIZ, "docs", "sinonimos.md"), encoding="utf-8") as f:
        assert f.read() == gerar_dados_js.conteudo_sinonimos_md(), (
            "o docs/sinonimos.md está desatualizado: corra  python3 ferramentas/gerar_dados_js.py"
        )


def test_paginas_usam_ficheiros_partilhados_sem_copias_embutidas():
    for pagina in PAGINAS_SIMULADOR:
        with open(os.path.join(RAIZ, pagina), encoding="utf-8") as f:
            html = f.read()
        assert '<script type="application/json"' not in html, f"{pagina} ainda tem dados embutidos"
        posicoes = [html.find('<script src="%s"></script>' % s) for s in ("dados.js", "motor.js", "ui.js")]
        assert all(p >= 0 for p in posicoes), f"{pagina} não carrega dados.js, motor.js e ui.js"
        assert posicoes == sorted(posicoes), f"{pagina}: a ordem tem de ser dados.js, motor.js, ui.js"


def test_grupos_inem_cobrem_0_a_215_meses_sem_falhas():
    with open(os.path.join(RAIZ, "parametros_vitais.json"), encoding="utf-8") as f:
        grupos = json.load(f)["limites_alerta_inem"]["grupos"]
    esperado = 0
    for g in grupos:
        assert g["idade_min_meses"] == esperado, g["grupo"]
        assert g["idade_max_meses"] >= g["idade_min_meses"], g["grupo"]
        esperado = g["idade_max_meses"] + 1
    assert esperado == 216
