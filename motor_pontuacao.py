import json
import os

_PASTA = os.path.dirname(os.path.abspath(__file__))

def _carregar(nome):
    with open(os.path.join(_PASTA, nome), encoding="utf-8") as f:
        return json.load(f)

taxonomia = _carregar("taxonomia.json")
fichas = _carregar("criterios.json")
limites_inem = _carregar("parametros_vitais.json")["limites_alerta_inem"]

BONUS_BANDEIRA = 2  # multiplicador extra quando um achado bandeira_vermelha bate
LIMIAR_DIFERENCIACAO_PONTOS = 12  # diferença mínima de F1 (em pontos %) pra considerar o 1º colocado destacado
IDADE_ADULTO_MESES = 216  # 18 anos: a partir daqui usam-se as regras gerais da taxonomia

# Em vítimas pediátricas, estas tags deixam de usar os limites de adulto da
# taxonomia e passam a usar os limites do grupo etário do INEM...
TAGS_LIMITES_PEDIATRICOS = {"taquicardia", "bradicardia", "taquipneia", "hipotensao", "glicemia_baixa"}
# ...e estas não se aplicam abaixo dos 18 anos (não ativam).
TAGS_SO_ADULTO = {"hipertensao", "hipotensao_diastolica", "hipertensao_diastolica"}

def grupo_pediatrico(idade_meses):
    """Grupo etário do INEM para a idade, ou None se não houver idade ou for >= 18 anos."""
    if idade_meses is None or idade_meses >= IDADE_ADULTO_MESES:
        return None
    for grupo in limites_inem["grupos"]:
        if grupo["idade_min_meses"] <= idade_meses <= grupo["idade_max_meses"]:
            return grupo
    raise ValueError(f"idade sem grupo pediátrico: {idade_meses} meses")

def pas_minima(grupo, idade_meses):
    """PAS mínima aceitável: base + por_ano × anos completos (ex.: 4a 11m -> 70 + 2×4 = 78)."""
    return grupo["pas_min_base"] + grupo["pas_min_por_ano"] * (idade_meses // 12)

def pas_normal(grupo, idade_meses):
    """PAS normal: base + por_ano × anos completos (ex.: 4 anos -> 90 + 2×4 = 98)."""
    return grupo["pas_normal_base"] + grupo["pas_normal_por_ano"] * (idade_meses // 12)

def peso_estimado(idade_meses):
    """Peso estimado em kg (Quadro 1), ou None se não se aplicar (recém-nascido e adultos)."""
    for regra in limites_inem["peso_estimado"]["regras"]:
        if regra["idade_min_meses"] <= idade_meses <= regra["idade_max_meses"]:
            idade = idade_meses if regra["unidade"] == "meses" else idade_meses // 12
            return regra["multiplicador"] * idade + regra["soma"]
    return None

def tags_dos_vitais(vitais, idade_meses=None):
    grupo = grupo_pediatrico(idade_meses)
    ativas = set()
    for regra in taxonomia["sinais_vitais"]:
        if grupo is not None and regra["tag"] in TAGS_LIMITES_PEDIATRICOS | TAGS_SO_ADULTO:
            continue
        v = vitais.get(regra["parametro"])
        if v is None:
            continue
        if regra["min"] is not None and v < regra["min"]:
            continue
        if regra["max"] is not None and v > regra["max"]:
            continue
        ativas.add(regra["tag"])
    if grupo is not None:
        fc, fr, pas, glicemia = vitais.get("FC"), vitais.get("FR"), vitais.get("PAS"), vitais.get("Glicemia")
        if fc is not None and fc > grupo["fc_max"]:
            ativas.add("taquicardia")
        if fc is not None and fc < grupo["fc_min"]:
            ativas.add("bradicardia")
        if fr is not None and fr > grupo["fr_max"]:
            ativas.add("taquipneia")
        if pas is not None and pas < pas_minima(grupo, idade_meses):
            ativas.add("hipotensao")
        if glicemia is not None and glicemia < grupo["glicemia_min"]:
            ativas.add("glicemia_baixa")
    return ativas

def _regra(tag):
    return next(r for r in taxonomia["sinais_vitais"] if r["tag"] == tag)

def referencia_vitais(idade_meses):
    """Valores de referência e limites de alerta para uma idade, exatamente os
    que tags_dos_vitais usa. É o que a página de Parâmetros Vitais mostra.
    idade_meses = None ou >= 216: regras de adulto da taxonomia."""
    grupo = grupo_pediatrico(idade_meses)
    comum = {
        "spo2_max_alerta": _regra("spo2_baixo")["max"],
        "glicemia_alta_min": _regra("glicemia_alta")["min"],
        "febre_min": _regra("febre")["min"],
        "hipotermia_max": _regra("hipotermia_vital")["max"],
    }
    if grupo is None:
        return dict(comum, adulto=True, grupo=None,
                    fc_alerta_abaixo_de=_regra("bradicardia")["max"] + 1,
                    fc_alerta_acima_de=_regra("taquicardia")["min"] - 1,
                    fr_alerta_acima_de=_regra("taquipneia")["min"] - 1,
                    pas_hipotensao_max=_regra("hipotensao")["max"],
                    pas_hipertensao_min=_regra("hipertensao")["min"],
                    pad_baixa_max=_regra("hipotensao_diastolica")["max"],
                    pad_alta_min=_regra("hipertensao_diastolica")["min"],
                    glicemia_baixa_max=_regra("glicemia_baixa")["max"])
    return dict(comum, adulto=False, grupo=grupo["grupo"],
                fc_min=grupo["fc_min"], fc_max=grupo["fc_max"],
                fr_min=grupo["fr_min"], fr_max=grupo["fr_max"],
                pas_normal=pas_normal(grupo, idade_meses),
                pas_normal_maior_que=bool(grupo.get("pas_normal_maior_que")),
                pas_min=pas_minima(grupo, idade_meses),
                glicemia_min=grupo["glicemia_min"],
                peso_estimado=peso_estimado(idade_meses))

def pontuar_lista(criterios, tags_presentes):
    """
    Duas métricas, combinadas por F1 (média harmônica), em vez de um único
    percentual:

    - precisao: dos critérios DESTA ficha/variante, quantos (em peso) bateram.
      Responde "o que a vítima apresenta é compatível com esta ficha?"
    - cobertura (recall): das tags que o usuário informou (input inteiro),
      quantas esta ficha consegue explicar. Responde "esta ficha dá conta
      de tudo que foi observado, ou só uma fatia pequena?"

    Uma ficha pequena que bate 100% dos seus critérios mas ignora outras tags
    presentes no input tem precisão alta e cobertura baixa -> F1 baixo. Isso
    corrige o viés de fichas com poucos critérios "vencerem" por sorte.
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

def variantes_da_ficha(ficha):
    """
    Uma ficha pode ter 3 formatos:
    - "plano": um único conjunto de critérios
    - "por_gravidade": vários níveis de gravidade (ex: asma leve/moderada/grave)
    - "por_subtipo": vários subtipos/síndromes distintos dentro da mesma ficha
      (ex: trauma_toracico tem 8 lesões diferentes; intoxicacao_pediatrica tem
      7 síndromes tóxicas)
    Em ambos os casos com variantes, cada uma é pontuada separadamente e
    disputa o ranking como se fosse uma ficha à parte.
    """
    if ficha["formato"] == "plano":
        return [(None, ficha["criterios"])]
    if ficha["formato"] == "por_gravidade":
        return list(ficha["niveis_gravidade"].items())
    if ficha["formato"] == "por_subtipo":
        return list(ficha["subtipos"].items())
    raise ValueError(f"formato desconhecido: {ficha['formato']}")

def rankear(tags_presentes, top_n=4, limiar=0.25, minimo_criterios=2, contexto_trauma=False, contexto_pediatrico=False):
    """
    Portões de contexto clínico:
    - contexto_trauma: fichas da categoria "Trauma" só entram na disputa se
      houver mecanismo de trauma confirmado. Sem isso, sinais genéricos de
      choque (taquicardia, palidez, dispneia) fazem fichas como hemotórax
      competirem com quadros puramente clínicos sem nenhuma evidência de
      lesão física — foi o que aconteceu no Caso 4 quando expandimos de 4
      para 47 fichas.
    - contexto_pediatrico: fichas da categoria "Pediatria" só entram na
      disputa se a vítima for pediátrica. Sem isso, sinais autonómicos
      genéricos (taquicardia, palidez, sudorese) fazem fichas pediátricas
      pequenas "roubarem" o ranking de vítimas adultas, já que o motor não
      tem noção de idade por si só.
    """
    candidatos = []
    for ficha_id, ficha in fichas.items():
        if ficha.get("categoria") == "Trauma" and not contexto_trauma:
            continue
        if ficha.get("categoria") == "Pediatria" and not contexto_pediatrico:
            continue
        for variante, criterios in variantes_da_ficha(ficha):
            precisao, cobertura, f1, bateram = pontuar_lista(criterios, tags_presentes)
            if len(bateram) < minimo_criterios:
                continue
            candidatos.append((ficha["nome"], variante, precisao, cobertura, f1, bateram))
    candidatos.sort(key=lambda x: x[4], reverse=True)
    return [c for c in candidatos if c[4] >= limiar][:top_n]

def imprimir_resultado(titulo, candidatos):
    """
    Mostra o ranking. Se a diferença de F1 entre o 1º colocado e algum dos
    seguintes for menor que LIMIAR_DIFERENCIACAO_PONTOS, todos os que caem
    dentro dessa margem do líder são tratados como um GRUPO EMPATADO: nenhum
    é destacado como resposta certa, e um aviso explícito é mostrado.
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

if __name__ == "__main__":
    # -----------------------------------------------------------------------
    # Caso A: Trauma torácico — pneumotórax hipertensivo
    # -----------------------------------------------------------------------
    vitaisA = {"FC": 128, "PAS": 78}
    tagsA = {"dispneia", "taquipneia", "assimetria_toracica", "ingurgitamento_jugular",
             "desvio_traqueia", "cianose"} | tags_dos_vitais(vitaisA)
    imprimir_resultado(
        "CASO A (trauma): dispneia, taquipneia, assimetria torácica, ingurgitamento jugular, desvio da traqueia, cianose, FC 128, PAS 78",
        rankear(tagsA, contexto_trauma=True),
    )

    # -----------------------------------------------------------------------
    # Caso B: Intoxicação pediátrica — síndrome colinérgica vs narcótica
    # (ambas cursam com bradicardia + miose, teste de ambiguidade entre
    # subtipos DENTRO da mesma ficha)
    # -----------------------------------------------------------------------
    vitaisB = {"FC": 52}
    tagsB = {"miose", "sialorreia", "diarreia"} | tags_dos_vitais(vitaisB)
    imprimir_resultado(
        "CASO B (intoxicação pediátrica): bradicardia, miose, sialorreia, diarreia",
        rankear(tagsB, contexto_pediatrico=True),
    )

    # -----------------------------------------------------------------------
    # Caso C: Hipertensão na gravidez com sinais de gravidade
    # -----------------------------------------------------------------------
    vitaisC = {"PAS": 162}
    tagsC = {"cefaleia_intensa", "alteracao_visual", "dor_abdominal"} | tags_dos_vitais(vitaisC)
    imprimir_resultado(
        "CASO C (obstetrícia): PAS 162, cefaleia intensa, alteração visual, dor abdominal",
        rankear(tagsC),
    )

    # -----------------------------------------------------------------------
    # Caso D: Criança com febre + convulsão — ambíguo entre 3 fichas
    # pediátricas diferentes (febre_pediatrica, convulsao_pediatrica,
    # sepsis_meningococica) — teste de ambiguidade entre patologias
    # DIFERENTES, análogo ao Caso 4 já validado com o utilizador.
    # -----------------------------------------------------------------------
    vitaisD = {"Temp": 39.2}
    tagsD = {"convulsao_presente", "dispneia"} | tags_dos_vitais(vitaisD)
    imprimir_resultado(
        "CASO D (pediatria): Temp 39.2ºC (febre), convulsão presenciada, dificuldade respiratória",
        rankear(tagsD, contexto_pediatrico=True),
    )
