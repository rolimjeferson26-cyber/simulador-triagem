"""Gera e verifica a Content-Security-Policy (CSP) de cada página .html.

O que é a CSP: uma regra que diz ao browser de onde a página pode carregar
scripts, estilos, imagens, etc. Se alguém conseguir injetar um <script> na
página, o browser recusa-se a corrê-lo porque não está na lista autorizada.

O GitHub Pages não deixa configurar cabeçalhos HTTP, por isso a CSP vai numa
etiqueta <meta http-equiv="Content-Security-Policy"> no <head> de cada página.

Os scripts escritos dentro do HTML (<script>...</script>) são autorizados
pelo seu "hash" SHA-256: uma impressão digital do conteúdo. Se mudar uma
única letra dentro de um <script>, o hash muda e o browser bloqueia-o.
Por isso, sempre que editar um <script> dentro de um .html, corra:

    python3 ferramentas/atualizar_csp.py

e o teste tests/test_seguranca.py confirma que ficou tudo certo.

Uso:
    python3 ferramentas/atualizar_csp.py            # atualiza as páginas
    python3 ferramentas/atualizar_csp.py --verificar  # só verifica (sai com 1 se houver erros)
"""
import base64
import glob
import hashlib
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Política base. {scripts} é substituído pelos hashes dos scripts embutidos.
#  - default-src 'self'         só o próprio site, por defeito
#  - script-src                 ficheiros .js do próprio site + scripts embutidos autorizados
#  - style-src 'unsafe-inline'  necessário para estilos escritos no HTML (risco baixo)
#  - img-src data:              imagens embutidas nos estilos
#  - *.goatcounter.com          envio das estatísticas de visitas (count.js), sem cookies
#  - object-src 'none'          sem plugins (Flash, etc.)
#  - base-uri / form-action     impedem redirecionar links e formulários para fora
POLITICA = ("default-src 'self'; script-src 'self'{scripts}; style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https://*.goatcounter.com; connect-src 'self' https://*.goatcounter.com; font-src 'self'; object-src 'none'; "
            "base-uri 'self'; form-action 'self'")

RE_SCRIPT = re.compile(r"<script>(.*?)</script>", re.S)
RE_META_CSP = re.compile(r'[ \t]*<meta http-equiv="Content-Security-Policy" content="[^"]*">\n?')
RE_META_VIEWPORT = re.compile(r'(<meta name="viewport"[^>]*>\n)')


def politica_para(html):
    hashes = []
    for corpo in RE_SCRIPT.findall(html):
        h = base64.b64encode(hashlib.sha256(corpo.encode("utf-8")).digest()).decode()
        hashes.append(f" 'sha256-{h}'")
    return POLITICA.format(scripts="".join(hashes))


def meta_para(html):
    return f'<meta http-equiv="Content-Security-Policy" content="{politica_para(html)}">\n'


def paginas(raiz):
    return sorted(glob.glob(os.path.join(raiz, "*.html")))


def atualizar(raiz=RAIZ):
    for caminho in paginas(raiz):
        with open(caminho, encoding="utf-8") as f:
            html = f.read()
        sem = RE_META_CSP.sub("", html)
        if not RE_META_VIEWPORT.search(sem):
            raise SystemExit(f"{os.path.basename(caminho)}: não encontrei <meta name=\"viewport\"> para colocar a CSP")
        novo = RE_META_VIEWPORT.sub(lambda m: m.group(1) + meta_para(sem), sem, count=1)
        if novo != html:
            with open(caminho, "w", encoding="utf-8") as f:
                f.write(novo)
            print(f"atualizada: {os.path.basename(caminho)}")


def verificar(raiz=RAIZ):
    problemas = []
    for caminho in paginas(raiz):
        nome = os.path.basename(caminho)
        with open(caminho, encoding="utf-8") as f:
            html = f.read()
        metas = RE_META_CSP.findall(html)
        if len(metas) != 1:
            problemas.append(f"{nome}: deve ter exatamente 1 <meta> de CSP (tem {len(metas)})")
            continue
        if metas[0].strip() != meta_para(RE_META_CSP.sub("", html)).strip():
            problemas.append(f"{nome}: a CSP está desatualizada (algum <script> foi alterado)")
        if re.search(r"\son[a-z]+\s*=", re.sub(r"<script>.*?</script>", "", html, flags=re.S)):
            problemas.append(f"{nome}: tem atributos on...= (ex.: onclick) — a CSP bloqueia-os; use addEventListener")
    return problemas


if __name__ == "__main__":
    if "--verificar" in sys.argv:
        p = verificar()
        print("\n".join(p) or "CSP OK em todas as páginas")
        sys.exit(1 if p else 0)
    atualizar()
