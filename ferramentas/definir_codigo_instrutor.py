"""Define (ou muda) o código de acesso ao modo Instrutor.

Porquê: antes, o código era a data do dia (DDMM) — qualquer formando o
adivinhava. Agora o código é escolhido por si e o site guarda só um "hash"
dele, nunca o código em texto. Quem ler o código-fonte do site vê o hash, mas
não consegue voltar ao código original (só tentando códigos um a um, e cada
tentativa é lenta de propósito).

Como funciona:
  - PBKDF2-SHA256 com um "sal" aleatório e muitas iterações. O sal impede
    tabelas pré-calculadas; as iterações tornam cada tentativa lenta.
  - O browser faz o mesmo cálculo (Web Crypto API) ao carregar em Confirmar e
    compara com o hash guardado em codigo_instrutor.js.

Uso:
    python3 ferramentas/definir_codigo_instrutor.py           # pede o código (não aparece no ecrã)
    python3 ferramentas/definir_codigo_instrutor.py --gerar   # gera um código aleatório e mostra-o

Depois, faça commit do codigo_instrutor.js. O código em si NUNCA vai para o
repositório: entregue-o só aos formadores (por exemplo, às escolas com licença).

Limite honesto: isto impede que um formando adivinhe o código, mas os dados
dos casos (incluindo o gabarito) continuam no dados.js, visíveis para quem
souber ler o código-fonte. Proteção completa só com um servidor (fase 2).
"""
import base64
import getpass
import hashlib
import os
import secrets
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DESTINO = os.path.join(RAIZ, "codigo_instrutor.js")
ITERACOES = 310_000          # recomendação OWASP para PBKDF2-SHA256
ALFABETO = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"   # sem 0/O, 1/I/L, para não haver confusões
TAMANHO_MINIMO = 8


def normalizar(codigo):
    """Igual ao browser: sem espaços e em maiúsculas."""
    return codigo.strip().upper()


def gerar_codigo(tamanho=10):
    return "".join(secrets.choice(ALFABETO) for _ in range(tamanho))


def escrever(codigo):
    codigo = normalizar(codigo)
    if len(codigo) < TAMANHO_MINIMO:
        raise SystemExit(f"O código tem de ter pelo menos {TAMANHO_MINIMO} caracteres.")
    sal = secrets.token_bytes(16)
    h = hashlib.pbkdf2_hmac("sha256", codigo.encode("utf-8"), sal, ITERACOES)
    b64 = lambda b: base64.b64encode(b).decode()
    with open(DESTINO, "w", encoding="utf-8") as f:
        f.write(
            "// Gerado por ferramentas/definir_codigo_instrutor.py — não editar à mão.\n"
            "// Contém só o hash do código de instrutor (PBKDF2-SHA256), nunca o código.\n"
            f'window.CODIGO_INSTRUTOR = {{ sal: "{b64(sal)}", iteracoes: {ITERACOES}, hash: "{b64(h)}" }};\n'
        )
    print(f"Atualizado: {os.path.relpath(DESTINO, RAIZ)}")


if __name__ == "__main__":
    if "--gerar" in sys.argv:
        novo = gerar_codigo()
        escrever(novo)
        print(f"\nNovo código de instrutor: {novo}\nGuarde-o num sítio seguro. Não o coloque no repositório.")
    else:
        c1 = getpass.getpass("Novo código de instrutor (mín. 8 caracteres): ")
        c2 = getpass.getpass("Repita o código: ")
        if normalizar(c1) != normalizar(c2):
            raise SystemExit("Os códigos não coincidem.")
        escrever(c1)
