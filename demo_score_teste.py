import json

taxonomia = json.load(open("taxonomia_teste.json", encoding="utf-8"))
fichas = json.load(open("criterios_teste.json", encoding="utf-8"))

BONUS_BANDEIRA = 2  # multiplicador extra quando um achado bandeira_vermelha bate
LIMIAR_DIFERENCIACAO_PONTOS = 12  # diferença mínima de F1 (em pontos %) pra considerar o 1º colocado destacado

def tags_dos_vitais(vitais):
    ativas = set()
    for regra in taxonomia["sinais_vitais"]:
        v = vitais.get(regra["parametro"])
        if v is None:
            continue
        if regra["min"] is not None and v < regra["min"]:
            continue
        if regra["max"] is not None and v > regra["max"]:
            continue
        ativas.add(regra["tag"])
    return ativas

def pontuar_lista(criterios, tags_presentes):
    """
    Duas métricas, combinadas por F1 (média harmônica), em vez de um único
    percentual:

    - precisao: dos critérios DESTA ficha, quantos (em peso) bateram.
      Responde "o que a vítima apresenta é compatível com esta ficha?"
    - cobertura (recall): das tags que o usuário informou (input inteiro),
      quantas esta ficha consegue explicar. Responde "esta ficha dá conta
      de tudo que foi observado, ou só uma fatia pequena?"

    Uma ficha pequena que bate 100% dos seus 2 critérios mas ignora outras
    5 tags presentes no input tem precisão alta e cobertura baixa -> F1
    baixo. Isso corrige o viés de fichas com poucos critérios "vencerem"
    por sorte (caso da crise_ligeira de Asma na 1ª rodada de teste).
    """
    total_peso = sum(c["peso"] * (BONUS_BANDEIRA if c.get("bandeira_vermelha") else 1) for c in criterios)
    obtido_peso = 0
    bateram = []
    for c in criterios:
        peso_efetivo = c["peso"] * (BONUS_BANDEIRA if c.get("bandeira_vermelha") else 1)
        if c["tag"] in tags_presentes:
            obtido_peso += peso_efetivo
            bateram.append(c)

    precisao = obtido_peso / total_peso if total_peso else 0
    cobertura = len(bateram) / len(tags_presentes) if tags_presentes else 0
    f1 = (2 * precisao * cobertura / (precisao + cobertura)) if (precisao + cobertura) else 0
    return precisao, cobertura, f1, bateram

def rankear(tags_presentes, top_n=3, limiar=0.25, minimo_criterios=2):
    candidatos = []
    for ficha_id, ficha in fichas.items():
        if ficha["formato"] == "plano":
            listas = [(None, ficha["criterios"])]
        else:
            listas = list(ficha["niveis_gravidade"].items())
        for nivel, criterios in listas:
            precisao, cobertura, f1, bateram = pontuar_lista(criterios, tags_presentes)
            if len(bateram) < minimo_criterios:
                continue
            candidatos.append((ficha["nome"], nivel, precisao, cobertura, f1, bateram))
    candidatos.sort(key=lambda x: x[4], reverse=True)
    return [c for c in candidatos if c[4] >= limiar][:top_n]

def imprimir_resultado(titulo, candidatos):
    """
    Mostra o ranking. Se a diferença de F1 entre o 1º colocado e algum dos
    seguintes for menor que LIMIAR_DIFERENCIACAO_PONTOS, todos os que caem
    dentro dessa margem do líder são tratados como um GRUPO EMPATADO: nenhum
    é destacado como resposta certa, e um aviso explícito é mostrado.

    Isso evita que a interface pareça mais confiante do que os achados
    realmente permitem — importante em cenário pré-hospitalar, onde um
    "1º colocado" sem essa ressalva pode ser lido como diagnóstico.
    """
    print()
    print("=" * 70)
    print(titulo)
    print("=" * 70)

    if not candidatos:
        print("Nenhuma correspondência com confiança suficiente para sugerir uma patologia.")
        return

    lider_f1 = candidatos[0][4]
    empatados = [c for c in candidatos if (lider_f1 - c[4]) * 100 < LIMIAR_DIFERENCIACAO_PONTOS]

    if len(empatados) > 1:
        nomes = ", ".join(f"{c[0]}" + (f" ({c[1]})" if c[1] else "") for c in empatados)
        margem = (lider_f1 - empatados[-1][4]) * 100
        print(f"⚠️  ACHADOS INSUFICIENTES PARA DIFERENCIAR — {len(empatados)} candidatos dentro de {margem:.0f} pontos um do outro (limiar: {LIMIAR_DIFERENCIACAO_PONTOS} pts)")
        print(f"    Candidatos empatados: {nomes}")
        print(f"    Sugestão: investigar achados adicionais que distingam entre eles antes de decidir conduta.")

    for i, (nome, nivel, precisao, cobertura, f1, bateram) in enumerate(candidatos, start=1):
        label = f"{nome} ({nivel})" if nivel else nome
        em_grupo = " [grupo empatado]" if len(empatados) > 1 and (lider_f1 - f1) * 100 < LIMIAR_DIFERENCIACAO_PONTOS else ""
        destaque = " <- destaque" if (i == 1 and len(empatados) == 1) else ""
        print(f"\n{i}. {label}: F1={f1:.0%}  (precisao={precisao:.0%}, cobertura={cobertura:.0%}){em_grupo}{destaque}")
        for c in bateram:
            flag = "  [BANDEIRA VERMELHA]" if c.get("bandeira_vermelha") else ""
            print(f"   - {c['tag']}{flag}")

# ---------------------------------------------------------------------------
# Caso de teste 1: vítima com crise de asma moderada/grave
# ---------------------------------------------------------------------------
vitais1 = {"FR": 26, "FC": 118, "SpO2": 90}
tags1 = {"dispneia", "pieira", "tiragem_musculos_acessorios", "ansiedade"} | tags_dos_vitais(vitais1)
imprimir_resultado(
    "CASO 1: dispneia, pieira, tiragem, FR 26, FC 118, SpO2 90%, ansiedade",
    rankear(tags1),
)

# ---------------------------------------------------------------------------
# Caso de teste 2: vítima com suspeita de AVC
# ---------------------------------------------------------------------------
tags2 = {"assimetria_facial", "disartria_afasia", "hemiparesia_hemiplegia", "cefaleia_intensa"}
imprimir_resultado(
    "CASO 2: assimetria facial, disartria, hemiparesia, cefaleia intensa",
    rankear(tags2),
)

# ---------------------------------------------------------------------------
# Caso de teste 3: dor torácica típica + choque associado (caso ambíguo,
# pra ver como o motor se comporta quando duas fichas competem)
# ---------------------------------------------------------------------------
vitais3 = {"PAS": 82, "FC": 112}
tags3 = {"dor_toracica_opressiva", "dor_irradiada_msuperior_mandibula", "sudorese", "palidez"} | tags_dos_vitais(vitais3)
imprimir_resultado(
    "CASO 3: dor retroesternal irradiada p/ MS esq, sudorese, palidez, PAS 82, FC 112",
    rankear(tags3),
)

# ---------------------------------------------------------------------------
# Caso de teste 4: sintomas ambíguos entre patologias DIFERENTES (não graus
# da mesma ficha). Cenário: dispneia súbita, ansiedade, taquicardia,
# taquipneia, sudorese, palidez, cansaço súbito — SEM dor torácica típica
# e SEM pieira/sibilos. De propósito sem nenhum achado bandeira_vermelha,
# pra simular exatamente o caso difícil: podia ser crise de asma, podia
# ser IAM atípico (a própria ficha cardíaca avisa que idosos/diabéticos
# podem não ter dor torácica) e até esbarra em choque.
# ---------------------------------------------------------------------------
tags4 = {"dispneia", "ansiedade", "taquicardia", "taquipneia", "sudorese", "palidez", "fadiga_inicio_subito"}
imprimir_resultado(
    "CASO 4 (ambíguo entre patologias diferentes): dispneia, ansiedade, taquicardia, taquipneia, sudorese, palidez, cansaço súbito",
    rankear(tags4),
)
