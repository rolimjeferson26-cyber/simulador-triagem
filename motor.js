// ------------------------------------------------------------------
// Motor de pontuação — porte direto de motor_pontuacao.py
//
// Partilhado pelo Caso Treino (index.html) e pela Avaliação ABCDE
// (abcde.html). No browser cria window.Motor a partir de window.DADOS
// (dados.js); no Node.js exporta a função criarMotor(dados), usada pelo
// teste de paridade em tests/test_paridade.py.
// ------------------------------------------------------------------
(function(raiz){
  "use strict";

  function criarMotor(dados){
    var taxonomia = dados.taxonomia;
    var fichas = dados.criterios;
    var limitesInem = dados.parametros_vitais.limites_alerta_inem;

    var BONUS_BANDEIRA = 2;
    var LIMIAR_DIFERENCIACAO_PONTOS = 12;
    var IDADE_ADULTO_MESES = 216; // 18 anos: a partir daqui usam-se as regras gerais da taxonomia

    // Em vítimas pediátricas, estas tags deixam de usar os limites de adulto da
    // taxonomia e passam a usar os limites do grupo etário do INEM...
    var TAGS_LIMITES_PEDIATRICOS = new Set(["taquicardia", "bradicardia", "taquipneia", "hipotensao"]);
    // ...e estas não se aplicam abaixo dos 18 anos (não ativam).
    var TAGS_SO_ADULTO = new Set(["hipertensao", "hipotensao_diastolica", "hipertensao_diastolica"]);

    function grupoPediatrico(idadeMeses){
      if (idadeMeses === null || idadeMeses === undefined || idadeMeses >= IDADE_ADULTO_MESES) return null;
      var grupo = limitesInem.grupos.find(function(g){ return g.idade_min_meses <= idadeMeses && idadeMeses <= g.idade_max_meses; });
      if (!grupo) throw new Error("idade sem grupo pediátrico: " + idadeMeses + " meses");
      return grupo;
    }

    function pasMinima(grupo, idadeMeses){
      return grupo.pas_min_base + grupo.pas_min_por_ano * Math.floor(idadeMeses / 12);
    }

    function tagsDosVitais(vitais, idadeMeses){
      var grupo = grupoPediatrico(idadeMeses);
      var ativas = new Set();
      function valor(param){
        var v = vitais[param];
        return (v === undefined || v === null || isNaN(v)) ? null : v;
      }
      taxonomia.sinais_vitais.forEach(function(regra){
        if (grupo && (TAGS_LIMITES_PEDIATRICOS.has(regra.tag) || TAGS_SO_ADULTO.has(regra.tag))) return;
        var v = valor(regra.parametro);
        if (v === null) return;
        if (regra.min !== null && v < regra.min) return;
        if (regra.max !== null && v > regra.max) return;
        ativas.add(regra.tag);
      });
      if (grupo){
        var fc = valor("FC"), fr = valor("FR"), pas = valor("PAS");
        if (fc !== null && fc > grupo.fc_max) ativas.add("taquicardia");
        if (fc !== null && fc < grupo.fc_min) ativas.add("bradicardia");
        if (fr !== null && fr > grupo.fr_max) ativas.add("taquipneia");
        if (pas !== null && pas < pasMinima(grupo, idadeMeses)) ativas.add("hipotensao");
      }
      return ativas;
    }

    function pontuarLista(criterios, tagsPresentes){
      var totalPeso = 0, obtidoPeso = 0, bateram = [];
      criterios.forEach(function(c){
        var pesoEfetivo = c.peso * (c.bandeira_vermelha ? BONUS_BANDEIRA : 1);
        totalPeso += pesoEfetivo;
        if (tagsPresentes.has(c.tag)){
          obtidoPeso += pesoEfetivo;
          bateram.push(c);
        }
      });
      var precisao = totalPeso ? obtidoPeso / totalPeso : 0;
      var cobertura = tagsPresentes.size ? bateram.length / tagsPresentes.size : 0;
      var f1 = (precisao + cobertura) ? (2 * precisao * cobertura) / (precisao + cobertura) : 0;
      return { precisao: precisao, cobertura: cobertura, f1: f1, bateram: bateram };
    }

    function variantesDaFicha(ficha){
      if (ficha.formato === "plano") return [[null, ficha.criterios]];
      if (ficha.formato === "por_gravidade") return Object.keys(ficha.niveis_gravidade).map(function(k){ return [k, ficha.niveis_gravidade[k]]; });
      if (ficha.formato === "por_subtipo") return Object.keys(ficha.subtipos).map(function(k){ return [k, ficha.subtipos[k]]; });
      return [];
    }

    // Portões de contexto clínico (opts.contextoTrauma / opts.contextoPediatrico):
    // - Trauma: fichas de Trauma só competem se houver mecanismo confirmado.
    // - Pediátrico: fichas de Pediatria só competem se a vítima for pediátrica
    //   (sem isso, sinais autonómicos genéricos — taquicardia, palidez, sudorese —
    //   fazem fichas pediátricas pequenas "roubarem" o ranking de vítimas adultas,
    //   já que o motor não tem noção de idade por si só).
    function rankear(tagsPresentes, opts){
      opts = opts || {};
      // topN=4, não 3: se um candidato genuinamente empatado com o líder (dentro
      // de LIMIAR_DIFERENCIACAO_PONTOS) ficasse na 4ª posição, um corte em 3
      // o excluiria da avaliação de empate silenciosamente.
      var topN = opts.topN || 4, limiar = opts.limiar != null ? opts.limiar : 0.25, minimoCriterios = opts.minimoCriterios || 2;
      var candidatos = [];
      Object.keys(fichas).forEach(function(fid){
        var ficha = fichas[fid];
        if (ficha.categoria === "Trauma" && !opts.contextoTrauma) return;
        if (ficha.categoria === "Pediatria" && !opts.contextoPediatrico) return;
        variantesDaFicha(ficha).forEach(function(par){
          var variante = par[0], criterios = par[1];
          var r = pontuarLista(criterios, tagsPresentes);
          if (r.bateram.length < minimoCriterios) return;
          candidatos.push({ fid: fid, nome: ficha.nome, variante: variante, precisao: r.precisao, cobertura: r.cobertura, f1: r.f1, bateram: r.bateram });
        });
      });
      candidatos.sort(function(a,b){ return b.f1 - a.f1; });
      return candidatos.filter(function(c){ return c.f1 >= limiar; }).slice(0, topN);
    }

    function avaliarDiferenciacao(candidatos){
      if (!candidatos.length) return { empatados: [], liderF1: 0 };
      var liderF1 = candidatos[0].f1;
      var empatados = candidatos.filter(function(c){ return (liderF1 - c.f1) * 100 < LIMIAR_DIFERENCIACAO_PONTOS; });
      return { empatados: empatados, liderF1: liderF1 };
    }

    var TAGS_BANDEIRA = new Set();
    Object.keys(fichas).forEach(function(fid){
      variantesDaFicha(fichas[fid]).forEach(function(par){
        par[1].forEach(function(c){ if (c.bandeira_vermelha) TAGS_BANDEIRA.add(c.tag); });
      });
    });

    return {
      BONUS_BANDEIRA: BONUS_BANDEIRA,
      LIMIAR_DIFERENCIACAO_PONTOS: LIMIAR_DIFERENCIACAO_PONTOS,
      IDADE_ADULTO_MESES: IDADE_ADULTO_MESES,
      TAGS_BANDEIRA: TAGS_BANDEIRA,
      grupoPediatrico: grupoPediatrico,
      pasMinima: pasMinima,
      tagsDosVitais: tagsDosVitais,
      pontuarLista: pontuarLista,
      variantesDaFicha: variantesDaFicha,
      rankear: rankear,
      avaliarDiferenciacao: avaliarDiferenciacao
    };
  }

  if (typeof module !== "undefined" && module.exports) module.exports = criarMotor;
  else raiz.Motor = criarMotor(raiz.DADOS);
})(this);
