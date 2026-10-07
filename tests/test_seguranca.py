"""Segurança do simulador.

1. Importação de casos (ui.js: validarCasosImportados e esc): um ficheiro de
   casos partilhado entre formadores é "não confiável". Estes testes garantem
   que HTML malicioso nunca chega à página e que os casos verdadeiros continuam
   a ser aceites sem alterações.
2. Content-Security-Policy: cada página tem a CSP e os hashes dos scripts
   embutidos estão atualizados (se editar um <script>, corra
   `python3 ferramentas/atualizar_csp.py`).

Corre as funções reais do ui.js no Node.js, como test_pesquisa.py."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "ferramentas"))

import atualizar_csp  # noqa: E402

JS = r"""
var fs = require('fs'), vm = require('vm');
var ctx = {}; ctx.window = ctx; vm.createContext(ctx);
['dados.js', 'motor.js', 'ui.js'].forEach(function(f){ vm.runInContext(fs.readFileSync(%s + '/' + f, 'utf8'), ctx, { filename: f }); });
var p = JSON.parse(fs.readFileSync(0, 'utf8'));
var U = ctx.UI;
process.stdout.write(JSON.stringify({
  embutidos: ctx.DADOS.casos,
  validacaoEmbutidos: U.validarCasosImportados(ctx.DADOS.casos),
  validacaoMaliciosos: U.validarCasosImportados(p.maliciosos),
  esc: U.esc(p.textoEsc),
  gabaritoHtml: U.renderGabaritoConteudo(p.gabarito, p.titulo)
}));
"""

XSS = '<img src=x onerror="alert(1)">'


def correr_js(pedido):
    node = shutil.which("node")
    if not node:
        raise unittest.SkipTest("Node.js não encontrado: instale-o para correr os testes de segurança")
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as f:
        f.write(JS % json.dumps(RAIZ))
        caminho = f.name
    try:
        saida = subprocess.run([node, caminho], input=json.dumps(pedido), capture_output=True,
                               text=True, check=True).stdout
    finally:
        os.unlink(caminho)
    return json.loads(saida)


def _resultado():
    ficha_valida = "asma"
    return correr_js({
        "textoEsc": XSS,
        "titulo": XSS,
        "gabarito": {"tipo": "definido", "ficha_id": ficha_valida, "nota_instrutor": XSS},
        "maliciosos": [
            # 1: título com HTML: aceite, mas o texto fica guardado tal e qual (é escapado ao desenhar)
            {"titulo": XSS, "vinheta": "texto", "gabarito": {"tipo": "definido", "ficha_id": ficha_valida},
             "campo_estranho": "<script>"},
            # 2: ficha inexistente -> rejeitado
            {"titulo": "ok", "vinheta": "ok", "gabarito": {"tipo": "definido", "ficha_id": XSS}},
            # 3: título não é texto -> rejeitado
            {"titulo": {"x": 1}, "vinheta": "ok", "gabarito": {"tipo": "definido", "ficha_id": ficha_valida}},
            # 4: sem gabarito -> rejeitado
            {"titulo": "ok", "vinheta": "ok"},
            # 5: não é um objeto -> rejeitado
            "isto não é um caso",
        ],
    })


def test_esc_neutraliza_html():
    r = _resultado()
    assert "<" not in r["esc"] and ">" not in r["esc"] and '"' not in r["esc"]


def test_gabarito_nao_injeta_html():
    html = _resultado()["gabaritoHtml"]
    assert "<img" not in html
    assert "&lt;img" in html


def test_casos_embutidos_passam_a_validacao_sem_alteracoes():
    r = _resultado()
    v = r["validacaoEmbutidos"]
    assert v["rejeitados"] == 0
    assert len(v["validos"]) == len(r["embutidos"])
    for original, validado in zip(r["embutidos"], v["validos"]):
        for campo in ("id", "titulo", "vinheta", "nivel_dificuldade", "categoria_alvo"):
            assert validado.get(campo) == original.get(campo), (original["id"], campo)
        g, gv = original["gabarito"], validado["gabarito"]
        assert gv["tipo"] == g["tipo"]
        assert gv.get("ficha_id") == g.get("ficha_id")
        assert gv.get("nota_instrutor") == g.get("nota_instrutor")
        assert gv["tags_esperadas"] == g.get("tags_esperadas", [])
        assert gv["vitais_esperados"] == g.get("vitais_esperados", {})


def test_importacao_rejeita_casos_invalidos_e_descarta_campos_desconhecidos():
    v = _resultado()["validacaoMaliciosos"]
    assert v["rejeitados"] == 4
    assert len(v["validos"]) == 1
    assert "campo_estranho" not in v["validos"][0]


def test_csp_presente_e_atualizada():
    problemas = atualizar_csp.verificar(RAIZ)
    assert not problemas, "\n".join(problemas) + "\nCorra: python3 ferramentas/atualizar_csp.py"


def test_codigo_instrutor_guardado_so_como_hash():
    """O código de instrutor nunca está no site: só sal + hash PBKDF2 com muitas iterações.
    O antigo "código do dia" (DDMM), fácil de adivinhar, já não pode existir."""
    import re
    with open(os.path.join(RAIZ, "codigo_instrutor.js"), encoding="utf-8") as f:
        cfg = f.read()
    m = re.search(r'sal: "([A-Za-z0-9+/=]{20,})", iteracoes: (\d+), hash: "([A-Za-z0-9+/=]{40,})"', cfg)
    assert m, "codigo_instrutor.js com formato inesperado: corra ferramentas/definir_codigo_instrutor.py"
    assert int(m.group(2)) >= 100_000
    with open(os.path.join(RAIZ, "index.html"), encoding="utf-8") as f:
        html = f.read()
    assert "codigoDoDia" not in html
    assert '<script src="codigo_instrutor.js"></script>' in html
