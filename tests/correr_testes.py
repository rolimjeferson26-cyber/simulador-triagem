"""Executa todos os testes da pasta tests/ só com a biblioteca padrão.

Uso:  python3 tests/correr_testes.py

Corre todas as funções test_* dos ficheiros tests/test_*.py e termina com
código 1 se algum teste falhar (útil para integração contínua)."""
import glob
import importlib.util
import os
import sys
import traceback
import unittest

PASTA = os.path.dirname(os.path.abspath(__file__))


def main():
    passaram, falharam, ignorados = 0, [], 0
    for caminho in sorted(glob.glob(os.path.join(PASTA, "test_*.py"))):
        nome = os.path.splitext(os.path.basename(caminho))[0]
        spec = importlib.util.spec_from_file_location(nome, caminho)
        modulo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modulo)
        print(f"\n{nome}")
        for teste in sorted(n for n in dir(modulo) if n.startswith("test_")):
            try:
                getattr(modulo, teste)()
            except unittest.SkipTest as e:
                ignorados += 1
                print(f"  IGNORADO  {teste}: {e}")
            except Exception:
                falharam.append(f"{nome}.{teste}")
                print(f"  FALHOU    {teste}")
                print("            " + traceback.format_exc().strip().replace("\n", "\n            "))
            else:
                passaram += 1
                print(f"  ok        {teste}")
    print(f"\n{passaram} passaram, {len(falharam)} falharam, {ignorados} ignorados")
    return 1 if falharam else 0


if __name__ == "__main__":
    sys.exit(main())
