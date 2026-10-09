// Página de mudança para o Prontidão (sem envio de dados para lado nenhum).
// Lê os casos de treino guardados NESTE browser pelo simulador antigo e deixa
// descarregá-los num ficheiro, para os importar no Formador do Prontidão.
(function () {
  "use strict";
  var CHAVE = "bombeiros_casos_custom";
  var destino = document.documentElement.getAttribute("data-destino") || "https://prontidao.pt/";
  if (!/^https:\/\/prontidao\.pt\//.test(destino)) destino = "https://prontidao.pt/";

  function lerCasos() {
    try {
      var texto = window.localStorage.getItem(CHAVE);
      if (!texto) return null;
      var lista = JSON.parse(texto);
      return Array.isArray(lista) && lista.length ? lista : null;
    } catch (e) { return null; }
  }

  var casos = lerCasos();
  var estado = document.getElementById("estado-casos");
  var botao = document.getElementById("btn-exportar");
  var espera = document.getElementById("espera");

  if (casos) {
    estado.textContent = "Tens " + casos.length + (casos.length === 1 ? " caso guardado" : " casos guardados") + " neste browser.";
    botao.hidden = false;
    botao.addEventListener("click", function () {
      var blob = new Blob([JSON.stringify(casos, null, 2)], { type: "application/json" });
      var url = URL.createObjectURL(blob);
      var a = document.createElement("a");
      a.href = url;
      a.download = "casos_ficticios_custom.json";
      document.body.appendChild(a);
      a.click();
      a.remove();
      setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
      estado.textContent = "Ficheiro descarregado. No Prontidão, abre o Formador e usa «Importar».";
    });
  } else {
    // Sem casos guardados: não há nada a exportar, abre o Prontidão sozinho.
    estado.textContent = "Não há casos guardados neste browser.";
    espera.hidden = false;
    setTimeout(function () { window.location.replace(destino); }, 4000);
  }
})();
