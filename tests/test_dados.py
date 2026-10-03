"""Os dados embutidos no index.html têm de ser iguais aos ficheiros JSON.
O Caso Treino usa as cópias embutidas (para funcionar por file://) e o motor
em Python usa os ficheiros: se divergirem, os dois motores deixam de bater."""
import json
import os
import re

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BLOCOS = {
    "taxonomia-source": "taxonomia.json",
    "criterios-source": "criterios.json",
    "atuacoes-source": "atuacoes.json",
    "casos-source": "casos_ficticios.json",
    "parametros-source": "parametros_vitais.json",
}


def bloco_embutido(html, bloco_id):
    padrao = r'<script type="application/json" id="%s"[^>]*>(.*?)</script>' % re.escape(bloco_id)
    encontrados = re.findall(padrao, html, re.S)
    assert len(encontrados) == 1, f"bloco {bloco_id} encontrado {len(encontrados)} vezes no index.html"
    return json.loads(encontrados[0])


def test_blocos_embutidos_iguais_aos_ficheiros_json():
    with open(os.path.join(RAIZ, "index.html"), encoding="utf-8") as f:
        html = f.read()
    for bloco_id, ficheiro in BLOCOS.items():
        with open(os.path.join(RAIZ, ficheiro), encoding="utf-8") as f:
            original = json.load(f)
        assert bloco_embutido(html, bloco_id) == original, (
            f"o bloco {bloco_id} do index.html é diferente de {ficheiro}: "
            f"copie o conteúdo de {ficheiro} para o bloco embutido"
        )


def test_grupos_inem_cobrem_0_a_215_meses_sem_falhas():
    with open(os.path.join(RAIZ, "parametros_vitais.json"), encoding="utf-8") as f:
        grupos = json.load(f)["limites_alerta_inem"]["grupos"]
    esperado = 0
    for g in grupos:
        assert g["idade_min_meses"] == esperado, g["grupo"]
        assert g["idade_max_meses"] >= g["idade_min_meses"], g["grupo"]
        esperado = g["idade_max_meses"] + 1
    assert esperado == 216
