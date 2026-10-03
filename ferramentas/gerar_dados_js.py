"""Gera o dados.js (e o docs/sinonimos.md) a partir dos ficheiros JSON do projeto.

As páginas (Caso Treino e Avaliação ABCDE) carregam os dados com
<script src="dados.js">, o que funciona também ao abrir os ficheiros por
file://. Os ficheiros JSON continuam a ser a fonte: depois de editar um deles,
corra

    python3 ferramentas/gerar_dados_js.py

e faça commit do dados.js gerado. O teste tests/test_dados.py falha se o
dados.js estiver desatualizado.
"""
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# chave em window.DADOS -> ficheiro JSON
FONTES = {
    "taxonomia": "taxonomia.json",
    "criterios": "criterios.json",
    "atuacoes": "atuacoes.json",
    "casos": "casos_ficticios.json",
    "parametros_vitais": "parametros_vitais.json",
    "abcde": "abcde.json",
}

CABECALHO = (
    "// GERADO AUTOMATICAMENTE por ferramentas/gerar_dados_js.py a partir dos ficheiros JSON.\n"
    "// Não edite este ficheiro à mão: edite o JSON correspondente e corra\n"
    "//   python3 ferramentas/gerar_dados_js.py\n"
)


def conteudo_dados_js():
    linhas = []
    for chave, ficheiro in FONTES.items():
        with open(os.path.join(RAIZ, ficheiro), encoding="utf-8") as f:
            dados = json.load(f)
        linhas.append("  %s: %s" % (json.dumps(chave), json.dumps(dados, ensure_ascii=False, separators=(",", ":"))))
    return CABECALHO + "window.DADOS = {\n" + ",\n".join(linhas) + "\n};\n"


def conteudo_sinonimos_md():
    with open(os.path.join(RAIZ, "taxonomia.json"), encoding="utf-8") as f:
        taxonomia = json.load(f)
    linhas = [
        "# Sinónimos das tags",
        "",
        "Expressões que a pesquisa de sinais e sintomas reconhece, além do rótulo de cada tag",
        "(Caso Treino e etapa «História e sintomas» da Avaliação ABCDE). A pesquisa ignora",
        "acentos e maiúsculas. Os sinónimos não mudam o motor de pontuação.",
        "",
        "Este ficheiro é **gerado** a partir do campo `sinonimos` de `taxonomia.json` por",
        "`python3 ferramentas/gerar_dados_js.py`. Para acrescentar expressões, edite esse campo",
        "e corra o gerador (ou anote-as aqui e peça a atualização: este ficheiro é reescrito).",
        "",
        "| Tag | Rótulo | Sinónimos |",
        "|---|---|---|",
    ]
    for t in taxonomia["sinais_sintomas"]:
        if t.get("sinonimos"):
            linhas.append(f"| `{t['tag']}` | {t['label']} | {', '.join(t['sinonimos'])} |")
    return "\n".join(linhas) + "\n"


def main():
    caminho = os.path.join(RAIZ, "dados.js")
    with open(caminho, "w", encoding="utf-8", newline="\n") as f:
        f.write(conteudo_dados_js())
    print(f"dados.js gerado ({os.path.getsize(caminho) // 1024} KB)")
    os.makedirs(os.path.join(RAIZ, "docs"), exist_ok=True)
    with open(os.path.join(RAIZ, "docs", "sinonimos.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write(conteudo_sinonimos_md())
    print("docs/sinonimos.md gerado")
    return 0


if __name__ == "__main__":
    sys.exit(main())
