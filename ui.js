// ------------------------------------------------------------------
// Componentes de interface partilhados pelo Caso Treino (index.html) e
// pela Avaliação ABCDE (abcde.html): grelha de sinais vitais com avisos,
// seletor de sinais e sintomas, e desenho do resultado do motor.
// Precisa de window.DADOS (dados.js) e window.Motor (motor.js).
// ------------------------------------------------------------------
(function(raiz){
  "use strict";

  function criarUI(dados, motor){
    var taxonomia = dados.taxonomia;
    var fichas = dados.criterios;
    var atuacoes = dados.atuacoes;

    var GRUPOS_ORDEM = ["Geral","Respiratório","Cardiovascular","Neurológico","Endócrino",
      "Gastrointestinal","Sistêmico","Intoxicações","Trauma","Obstetrícia","Pediatria"];

    var ICON_FLAG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4"><path d="M4 21V4a1 1 0 011-1h13.5a.5.5 0 01.4.8L15 9l3.9 5.2a.5.5 0 01-.4.8H5v6"/></svg>';
    var ICON_CHECK = '<svg class="chk" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><path d="M20 6L9 17l-5-5"/></svg>';
    var ICON_WARN = '<svg viewBox="0 0 24 24" fill="none" stroke="#FFB454" stroke-width="2.2"><path d="M12 9v4M12 17h.01M10.3 3.9L1.8 18a1 1 0 00.9 1.5h18.6a1 1 0 00.9-1.5L13.7 3.9a1 1 0 00-1.7 0z"/></svg>';
    var ICON_STEP = '<svg viewBox="0 0 24 24" fill="none" stroke="#14E8C4" stroke-width="2.2"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11"/></svg>';
    var ICON_EMPTY = '<svg viewBox="0 0 24 24" fill="none" stroke="#5B6472" stroke-width="1.6"><circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>';
    var ICON_OK = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6"><path d="M20 6L9 17l-5-5"/></svg>';
    var ICON_X = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4"><path d="M18 6L6 18M6 6l12 12"/></svg>';

    function normalizar(s){
      return s.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "");
    }
    function formatarVariante(v){
      if (!v) return "";
      return v.split("_").map(function(w){ return w.charAt(0).toUpperCase() + w.slice(1); }).join(" ");
    }
    // ------------------------------------------------------------------
    // Pesquisa de sinais e sintomas (Caso Treino e Avaliação ABCDE): procura no
    // rótulo e nos sinónimos da taxonomia, sem acentos nem maiúsculas.
    // ------------------------------------------------------------------
    function textoPesquisa(t){
      return normalizar([t.label].concat(t.sinonimos || []).join(" | "));
    }

    // Sugestões para o termo escrito (a partir de 2 letras). opts.excluir: Set de
    // tags que não devem aparecer; opts.limite: máximo de sugestões (por omissão 8).
    // Devolve [{ tag, label, sinonimo }], com o sinónimo que correspondeu (ou null).
    function pesquisarTags(termo, opts){
      opts = opts || {};
      var q = normalizar((termo || "").trim());
      if (q.length < 2) return [];
      var excluir = opts.excluir || new Set(), limite = opts.limite || 8;
      var noRotulo = [], noSinonimo = [];
      taxonomia.sinais_sintomas.forEach(function(t){
        if (excluir.has(t.tag)) return;
        if (normalizar(t.label).indexOf(q) !== -1){ noRotulo.push({ tag: t.tag, label: t.label, sinonimo: null }); return; }
        var sin = (t.sinonimos || []).find(function(s){ return normalizar(s).indexOf(q) !== -1; });
        if (sin) noSinonimo.push({ tag: t.tag, label: t.label, sinonimo: sin });
      });
      return noRotulo.concat(noSinonimo).slice(0, limite);
    }

    function formatarIdade(totalMeses){
      var anos = Math.floor(totalMeses / 12), meses = totalMeses % 12;
      var partes = [];
      if (anos) partes.push(anos + (anos === 1 ? " ano" : " anos"));
      if (meses || !anos) partes.push(meses + (meses === 1 ? " mês" : " meses"));
      return partes.join(" e ");
    }

    // Valida a idade escrita em anos e meses (modo pediátrico).
    // Devolve { meses, erro }: erro preenchido se faltar ou for inválida.
    function validarIdade(anosRaw, mesesRaw){
      if (anosRaw === "" || mesesRaw === "") return { meses: null, erro: "Indique a idade (anos e meses) para avaliar os sinais vitais." };
      var anos = Number(anosRaw), meses = Number(mesesRaw);
      if (!Number.isInteger(anos) || !Number.isInteger(meses) || anos < 0 || meses < 0) return { meses: null, erro: "Use apenas números inteiros." };
      if (meses > 11) return { meses: null, erro: "Meses deve estar entre 0 e 11." };
      if (anos > 17) return { meses: null, erro: "Com 18 anos ou mais, escolha Adulto." };
      return { meses: anos * 12 + meses, erro: null };
    }

    // ------------------------------------------------------------------
    // Grelha de sinais vitais e seletor de sinais e sintomas
    // ------------------------------------------------------------------
    var PARAM_ORDEM = ["FC","FR","PAS","PAD","SpO2","Temp","Glicemia","Glasgow"];
    var regrasPorParametro = {};
    taxonomia.sinais_vitais.forEach(function(r){
      (regrasPorParametro[r.parametro] = regrasPorParametro[r.parametro] || []).push(r);
    });

    // parametros (opcional): só estes campos, pela ordem dada (ex.: ["FR","SpO2"]).
    function criarVitalsGrid(container, comHints, obterIdadeMeses, parametros){
      var ordem = parametros || PARAM_ORDEM;
      var inputs = {};
      var hints = {};
      ordem.forEach(function(param){
        var regras = regrasPorParametro[param];
        if (!regras) return;
        var unidade = regras[0].unidade;
        var card = document.createElement("div");
        card.className = "vital-card";
        card.innerHTML =
          '<div class="vital-label">' + param + '</div>' +
          '<div class="vital-input-row"><input type="number" inputmode="decimal" step="any"><span class="vital-unit">' + unidade + '</span></div>' +
          (comHints ? '<div class="vital-hint"></div>' : '');
        container.appendChild(card);
        inputs[param] = card.querySelector("input");
        if (comHints) hints[param] = card.querySelector(".vital-hint");
      });
      return {
        valores: function(){
          var v = {};
          Object.keys(inputs).forEach(function(p){ var raw = inputs[p].value; if (raw !== "") v[p] = parseFloat(raw); });
          return v;
        },
        setValores: function(v){
          v = v || {};
          Object.keys(inputs).forEach(function(p){ inputs[p].value = (v[p] !== undefined) ? v[p] : ""; });
        },
        limpar: function(){ Object.keys(inputs).forEach(function(p){ inputs[p].value = ""; }); },
        atualizarHints: function(){
          if (!comHints) return;
          var ativas = motor.tagsDosVitais(this.valores(), obterIdadeMeses ? obterIdadeMeses() : null);
          ordem.forEach(function(param){
            var regras = regrasPorParametro[param];
            if (!regras || !hints[param]) return;
            var achado = regras.find(function(r){ return ativas.has(r.tag); });
            hints[param].textContent = achado ? achado.label.replace(/\s*\(.*\)$/, "") : "";
          });
        },
        onChange: function(fn){ Object.keys(inputs).forEach(function(p){ inputs[p].addEventListener("input", fn); }); }
      };
    }

    // Os chips com a classe "bloqueada" não mudam ao clicar (a Avaliação ABCDE
    // usa-os para tags que se marcam numa letra).
    function criarPickerTags(container, searchInput){
      var gruposMap = {};
      taxonomia.sinais_sintomas.forEach(function(t){ (gruposMap[t.categoria] = gruposMap[t.categoria] || []).push(t); });

      GRUPOS_ORDEM.forEach(function(grupo){
        var tags = gruposMap[grupo];
        if (!tags || !tags.length) return;
        var card = document.createElement("div");
        card.className = "sym-card" + (grupo === "Geral" ? " open" : "");
        card.dataset.grupo = grupo;
        var chipsHtml = tags.map(function(t){
          var flagged = motor.TAGS_BANDEIRA.has(t.tag);
          return '<div class="sym-chip" data-tag="' + t.tag + '" data-label="' + textoPesquisa(t) + '">' +
            (flagged ? '<span class="flagdot"></span>' : '') + ICON_CHECK + '<span>' + t.label + '</span></div>';
        }).join("");
        card.innerHTML =
          '<div class="sym-card-head"><h3>' + grupo + '</h3><span class="sym-count-pill" data-count="' + grupo + '"></span><div class="chevron"></div></div>' +
          '<div class="sym-card-body"><div class="chips-wrap">' + chipsHtml + '</div></div>';
        container.appendChild(card);
        card.querySelector(".sym-card-head").addEventListener("click", function(){ card.classList.toggle("open"); });
      });

      container.addEventListener("click", function(e){
        var chip = e.target.closest(".sym-chip");
        if (!chip || chip.classList.contains("bloqueada")) return;
        chip.classList.toggle("selected");
        var isFlagged = !!chip.querySelector(".flagdot");
        chip.classList.toggle("flagged", isFlagged && chip.classList.contains("selected"));
        atualizarContagens();
      });

      function atualizarContagens(){
        GRUPOS_ORDEM.forEach(function(grupo){
          var card = container.querySelector('.sym-card[data-grupo="' + grupo + '"]');
          if (!card) return;
          var n = card.querySelectorAll(".sym-chip.selected").length;
          var pill = card.querySelector('[data-count="' + grupo + '"]');
          pill.textContent = n > 0 ? n + " selec." : "";
        });
      }

      if (searchInput){
        searchInput.addEventListener("input", function(){
          var termo = normalizar(searchInput.value.trim());
          var buscando = termo.length > 0;
          container.querySelectorAll(".sym-card").forEach(function(card){
            var algumVisivel = false;
            card.querySelectorAll(".sym-chip").forEach(function(chip){
              var visivel = !buscando || chip.dataset.label.indexOf(termo) !== -1;
              chip.style.display = visivel ? "" : "none";
              if (visivel) algumVisivel = true;
            });
            card.style.display = (buscando && !algumVisivel) ? "none" : "";
            if (buscando && algumVisivel) card.classList.add("open");
            else if (!buscando) card.classList.toggle("open", card.dataset.grupo === "Geral");
          });
        });
      }

      return {
        getSelected: function(){
          var tags = new Set();
          container.querySelectorAll(".sym-chip.selected").forEach(function(chip){ tags.add(chip.dataset.tag); });
          return tags;
        },
        setSelected: function(tagsArray){
          var set = new Set(tagsArray || []);
          container.querySelectorAll(".sym-chip").forEach(function(chip){
            var sel = set.has(chip.dataset.tag);
            chip.classList.toggle("selected", sel);
            var isFlagged = !!chip.querySelector(".flagdot");
            chip.classList.toggle("flagged", isFlagged && sel);
          });
          atualizarContagens();
        },
        limpar: function(){ this.setSelected([]); },
        atualizarContagens: atualizarContagens
      };
    }

    // ------------------------------------------------------------------
    // Resultado do motor
    // ------------------------------------------------------------------
    function tagInfo(tag){
      return taxonomia.sinais_sintomas.concat(taxonomia.sinais_vitais).find(function(x){ return x.tag === tag; });
    }
    function labelDaTag(tag){
      var t = tagInfo(tag);
      return t ? (t.label || "").replace(/\s*\(.*\)$/, "") : tag;
    }

    function renderCriteriaChips(bateram){
      return bateram.map(function(c){
        var t = tagInfo(c.tag);
        var label = t ? (t.label || "").replace(/\s*\(.*\)$/, "") : c.tag;
        if (c.bandeira_vermelha) return '<div class="crit-chip flag">' + ICON_FLAG + '<span>' + label + '</span></div>';
        return '<div class="crit-chip">' + label + '</div>';
      }).join("");
    }
    function renderCriteriaChipsSm(bateram){
      return bateram.map(function(c){
        var t = tagInfo(c.tag);
        var label = t ? (t.label || "").replace(/\s*\(.*\)$/, "") : c.tag;
        return '<div class="crit-chip-sm' + (c.bandeira_vermelha ? " flag" : "") + '">' + label + '</div>';
      }).join("");
    }

    function atuacaoDe(candidato){
      var entry = atuacoes[candidato.fid];
      if (!entry) return null;
      var lista = Array.isArray(entry) ? entry : (candidato.variante ? entry[candidato.variante] : null);
      return (lista && lista.length) ? lista : null;
    }
    function renderAtuacao(lista){
      var ultimoGrupo = null, html = "";
      lista.forEach(function(item){
        if (item.grupo && item.grupo !== ultimoGrupo){
          html += '<div class="at-group-label">' + item.grupo + '</div>';
          ultimoGrupo = item.grupo;
        }
        html += '<li>' + item.texto + '</li>';
      });
      return '<ul class="at-list">' + html + '</ul>';
    }
    function nomeCompleto(c){
      return c.nome + (c.variante ? ' <span class="sub">(' + formatarVariante(c.variante) + ')</span>' : "");
    }
    function nomeDoAlvo(alvo){
      var f = fichas[alvo.ficha_id];
      var nome = f ? f.nome : alvo.ficha_id;
      return nome + (alvo.variante ? " (" + formatarVariante(alvo.variante) + ")" : "");
    }

    function renderGabaritoConteudo(gabarito, titulo){
      var html = '<div class="gabarito-label">' + (titulo || "Gabarito (só instrutor)") + '</div>';
      if (gabarito.tipo === "ambiguo"){
        html += '<div class="gabarito-resposta">Caso ambíguo — válidos: ' +
          gabarito.candidatos_validos.map(nomeDoAlvo).join(" · ") + '</div>';
      } else {
        html += '<div class="gabarito-resposta">' + nomeDoAlvo({ficha_id: gabarito.ficha_id, variante: gabarito.variante}) + '</div>';
      }
      if (gabarito.nota_instrutor) html += '<div class="gabarito-nota">' + gabarito.nota_instrutor + '</div>';
      return html;
    }

    function candidatoCorresponde(c, alvo){
      return c.fid === alvo.ficha_id && (alvo.variante ? c.variante === alvo.variante : true);
    }

    function renderGabaritoResultado(gabarito, candidatos, titulo){
      var alvos = gabarito.tipo === "ambiguo" ? gabarito.candidatos_validos : [{ficha_id: gabarito.ficha_id, variante: gabarito.variante}];
      var achadoIdx = -1;
      for (var i = 0; i < candidatos.length; i++){
        if (alvos.some(function(a){ return candidatoCorresponde(candidatos[i], a); })){ achadoIdx = i; break; }
      }
      var status, statusClass, statusIcon;
      if (achadoIdx === 0){ status = "O motor identificou corretamente como principal"; statusClass = "ok"; statusIcon = ICON_OK; }
      else if (achadoIdx > 0){ status = "Apareceu no ranking, mas não como principal"; statusClass = "parcial"; statusIcon = ICON_WARN; }
      else { status = "O motor não encontrou a ficha esperada entre os candidatos mostrados"; statusClass = "falhou"; statusIcon = ICON_X; }

      var html = '<div class="gabarito-box">' + renderGabaritoConteudo(gabarito, titulo) +
        '<div class="gabarito-check ' + statusClass + '">' + statusIcon + '<span>' + status + '</span></div></div>';
      return html;
    }

    // Ranking, aviso de empate, hipótese destacada e atuação recomendada.
    function renderRanking(candidatos){
      var html = "";

      if (!candidatos.length){
        html = '<div class="empty-state">' + ICON_EMPTY +
          '<div><b>Nenhuma correspondência com confiança suficiente.</b><br>Volte e selecione mais achados (sinais vitais e/ou sintomas) para a análise.</div></div>';
      } else {
        var diff = motor.avaliarDiferenciacao(candidatos);

        if (diff.empatados.length > 1){
          var margem = Math.round((diff.liderF1 - diff.empatados[diff.empatados.length-1].f1) * 100);
          var nomesEmp = diff.empatados.map(function(c){ return c.nome + (c.variante ? " (" + formatarVariante(c.variante) + ")" : ""); }).join(", ");
          html += '<div class="warn-box"><div class="warn-top">' + ICON_WARN +
            '<div><div class="warn-title">Achados insuficientes para diferenciar</div>' +
            '<div class="warn-body">' + diff.empatados.length + ' hipóteses ficaram próximas entre si (diferença ≤ ' + margem + ' pontos). ' +
            '<b>Candidatos:</b> ' + nomesEmp + '. Considere avaliar achados adicionais antes de decidir conduta.</div></div></div></div>';

          html += '<div class="tied-label">' + diff.empatados.length + ' hipóteses empatadas — nenhuma destacada</div>';
          diff.empatados.forEach(function(c){
            html += '<div class="tied-card"><div class="tied-top"><div class="tied-name">' + nomeCompleto(c) + '</div>' +
              '<div class="tied-pct">' + Math.round(c.f1*100) + '%</div></div>' +
              '<div class="tied-criteria">' + renderCriteriaChipsSm(c.bateram) + '</div></div>';
          });

          var resto = candidatos.filter(function(c){ return diff.empatados.indexOf(c) === -1; });
          if (resto.length){
            html += '<div class="outras-label">Outras hipóteses consideradas</div>';
            resto.forEach(function(c){
              html += '<div class="tied-card"><div class="tied-top"><div class="tied-name">' + nomeCompleto(c) + '</div>' +
                '<div class="tied-pct">' + Math.round(c.f1*100) + '%</div></div>' +
                '<div class="tied-criteria">' + renderCriteriaChipsSm(c.bateram) + '</div></div>';
            });
          }
        } else {
          var vencedor = candidatos[0];
          var temBandeira = vencedor.bateram.some(function(c){ return c.bandeira_vermelha; });
          var nBandeiras = vencedor.bateram.filter(function(c){ return c.bandeira_vermelha; }).length;

          html += '<div class="hero ' + (temBandeira ? "sev-red" : "sev-teal") + '">';
          html += '<div class="hero-flag">' + (temBandeira ? ICON_FLAG : ICON_STEP) +
            '<span>' + (temBandeira ? (nBandeiras + " bandeira" + (nBandeiras===1?"":"s") + " vermelha" + (nBandeiras===1?"":"s")) : "Sem bandeiras vermelhas") + '</span></div>';
          html += '<h2 class="display">' + nomeCompleto(vencedor) + '</h2>';
          html += '<div class="hero-meta"><span class="conf-badge">' + Math.round(vencedor.f1*100) + '% compatibilidade</span>' +
            '<span class="conf-label">' + (vencedor.f1 >= 0.6 ? "alta confiança" : "confiança moderada") + '</span></div>';
          html += '<div class="criteria-title">Achados que bateram</div>';
          html += '<div class="criteria-wrap">' + renderCriteriaChips(vencedor.bateram) + '</div>';
          html += '</div>';

          var lista = atuacaoDe(vencedor);
          if (lista){
            html += '<div class="section-box"><div class="section-box-title">' + ICON_STEP + '<span>Atuação recomendada</span></div>' + renderAtuacao(lista) + '</div>';
          }

          var outros = candidatos.slice(1);
          if (outros.length){
            html += '<div class="outras-label">Outras hipóteses consideradas (menor compatibilidade)</div>';
            outros.forEach(function(c){
              html += '<div class="tied-card"><div class="tied-top"><div class="tied-name">' + nomeCompleto(c) + '</div>' +
                '<div class="tied-pct">' + Math.round(c.f1*100) + '%</div></div>' +
                '<div class="tied-criteria">' + renderCriteriaChipsSm(c.bateram) + '</div></div>';
            });
          }
        }
      }
      return html;
    }

    return {
      GRUPOS_ORDEM: GRUPOS_ORDEM,
      PARAM_ORDEM: PARAM_ORDEM,
      ICON_FLAG: ICON_FLAG, ICON_CHECK: ICON_CHECK, ICON_WARN: ICON_WARN, ICON_STEP: ICON_STEP,
      ICON_EMPTY: ICON_EMPTY, ICON_OK: ICON_OK, ICON_X: ICON_X,
      normalizar: normalizar,
      textoPesquisa: textoPesquisa,
      pesquisarTags: pesquisarTags,
      formatarVariante: formatarVariante,
      formatarIdade: formatarIdade,
      validarIdade: validarIdade,
      criarVitalsGrid: criarVitalsGrid,
      criarPickerTags: criarPickerTags,
      tagInfo: tagInfo,
      labelDaTag: labelDaTag,
      nomeDoAlvo: nomeDoAlvo,
      candidatoCorresponde: candidatoCorresponde,
      renderGabaritoConteudo: renderGabaritoConteudo,
      renderGabaritoResultado: renderGabaritoResultado,
      renderRanking: renderRanking
    };
  }

  raiz.UI = criarUI(raiz.DADOS, raiz.Motor);
})(this);
