"""A página de Parâmetros Vitais mostra referencia_vitais(idade). Estes testes
provam que esses valores são exatamente os limites a que o motor reage
(tags_dos_vitais): o motor e a consulta não podem divergir."""
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

import motor_pontuacao as m  # noqa: E402


def meses(anos, meses_extra=0):
    return anos * 12 + meses_extra


IDADES = [0, 1, 6, 11, 12, meses(1, 6), meses(4), meses(4, 11), meses(5, 11), meses(6), meses(8),
          meses(10, 11), meses(11), meses(12), meses(15), meses(17, 11), meses(18), meses(45), None]


def tags(vitais, idade):
    return m.tags_dos_vitais(vitais, idade)


def test_valores_da_consulta_sao_os_limites_do_motor():
    for idade in IDADES:
        ref = m.referencia_vitais(idade)
        if ref["adulto"]:
            fc_min, fc_max = ref["fc_alerta_abaixo_de"], ref["fc_alerta_acima_de"]
            fr_max = ref["fr_alerta_acima_de"]
            pas_ok, pas_baixa = ref["pas_hipotensao_max"] + 1, ref["pas_hipotensao_max"]
            glic_ok, glic_baixa = ref["glicemia_baixa_max"] + 1, ref["glicemia_baixa_max"]
            assert tags({"PAS": ref["pas_hipertensao_min"]}, idade) == {"hipertensao"}, idade
            assert tags({"PAS": ref["pas_hipertensao_min"] - 1}, idade) == set(), idade
            assert tags({"PAD": ref["pad_baixa_max"]}, idade) == {"hipotensao_diastolica"}, idade
            assert tags({"PAD": ref["pad_alta_min"]}, idade) == {"hipertensao_diastolica"}, idade
        else:
            fc_min, fc_max, fr_max = ref["fc_min"], ref["fc_max"], ref["fr_max"]
            pas_ok, pas_baixa = ref["pas_min"], ref["pas_min"] - 1
            glic_ok, glic_baixa = ref["glicemia_min"], ref["glicemia_min"] - 1
            # PAD e hipertensão sistólica não se aplicam abaixo dos 18 anos
            assert tags({"PAD": 40, "PAS": 200}, idade) == set(), idade
        # FC: o intervalo mostrado é exatamente o que não gera tags
        assert tags({"FC": fc_min}, idade) == set(), idade
        assert tags({"FC": fc_max}, idade) == set(), idade
        assert tags({"FC": fc_min - 1}, idade) == {"bradicardia"}, idade
        assert tags({"FC": fc_max + 1}, idade) == {"taquicardia"}, idade
        # FR: alerta acima do máximo mostrado
        assert tags({"FR": fr_max}, idade) == set(), idade
        assert tags({"FR": fr_max + 1}, idade) == {"taquipneia"}, idade
        # PAS mínima / hipotensão
        assert tags({"PAS": pas_ok}, idade) == set(), idade
        assert tags({"PAS": pas_baixa}, idade) == {"hipotensao"}, idade
        # glicemia
        assert tags({"Glicemia": glic_ok}, idade) == set(), idade
        assert tags({"Glicemia": glic_baixa}, idade) == {"glicemia_baixa"}, idade
        assert tags({"Glicemia": ref["glicemia_alta_min"]}, idade) == {"glicemia_alta"}, idade
        assert tags({"Glicemia": ref["glicemia_alta_min"] - 1}, idade) == set(), idade
        # SpO2 e temperatura
        assert tags({"SpO2": ref["spo2_max_alerta"]}, idade) == {"spo2_baixo"}, idade
        assert tags({"SpO2": ref["spo2_max_alerta"] + 1}, idade) == set(), idade
        assert tags({"Temp": ref["febre_min"]}, idade) == {"febre"}, idade
        assert tags({"Temp": ref["hipotermia_max"]}, idade) == {"hipotermia_vital"}, idade


def test_fronteiras_entre_grupos_na_consulta():
    pares = [(11, 12), (meses(5, 11), meses(6)), (meses(10, 11), meses(11)), (meses(17, 11), meses(18))]
    esperado = {11: "1-12 meses", 12: "1-5 anos", meses(5, 11): "1-5 anos", meses(6): "6-10 anos",
                meses(10, 11): "6-10 anos", meses(11): "> 10 anos", meses(17, 11): "> 10 anos", meses(18): None}
    for antes, depois in pares:
        for idade in (antes, depois):
            ref = m.referencia_vitais(idade)
            assert ref["grupo"] == esperado[idade], idade
            assert ref["adulto"] == (idade >= meses(18)), idade


def test_exemplos_pas_e_peso():
    ref = m.referencia_vitais(meses(4))
    assert (ref["pas_min"], ref["pas_normal"], ref["peso_estimado"]) == (78, 98, 16)
    ref = m.referencia_vitais(6)
    assert (ref["pas_min"], ref["pas_normal"], ref["peso_estimado"]) == (70, 80, 7.5)
    ref = m.referencia_vitais(meses(12))
    assert (ref["pas_min"], ref["pas_normal"], ref["peso_estimado"]) == (90, 120, 36)
    ref = m.referencia_vitais(0)
    assert (ref["pas_min"], ref["pas_normal"], ref["pas_normal_maior_que"], ref["peso_estimado"]) == (60, 60, True, None)
